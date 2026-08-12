# ui.py
# Графический интерфейс пользователя

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from PIL import Image, ImageTk
import os
import sys
from data_base import SCHEMAS
from calculations import calculate_reliability
from html import generate_html_report


class ReliabilityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Расчёт показателей надёжности РЭА")

        self.root.state('zoomed')
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)

        self.x_var = tk.StringVar()
        self.y_var = tk.StringVar()
        self.selected_schema = tk.IntVar(value=1)
        self.preview_enabled = tk.BooleanVar(value=False)

        self.images = {}
        self.preview_window = None
        self.preview_photo = None
        self.is_preview_showing = False
        self.current_hover_schema = None
        self.tile_frames = {}

        self.create_widgets()
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen())

    def toggle_fullscreen(self):
        if self.root.attributes('-fullscreen'):
            self.root.attributes('-fullscreen', False)
            self.root.state('zoomed')
        else:
            self.root.attributes('-fullscreen', True)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(main_frame, text="Ввод исходных данных", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="X (предпоследняя цифра):").grid(row=0, column=0, sticky=tk.W, padx=5)
        x_entry = ttk.Entry(input_frame, textvariable=self.x_var, width=5)
        x_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Y (последняя цифра):").grid(row=0, column=2, sticky=tk.W, padx=5)
        y_entry = ttk.Entry(input_frame, textvariable=self.y_var, width=5)
        y_entry.grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="(X=0..3, Y=0..9, при X=3 допустимо только Y=0)").grid(row=0, column=4, padx=10)

        self.calc_btn = ttk.Button(input_frame, text="Рассчитать", command=self.calculate)
        self.calc_btn.grid(row=0, column=5, padx=10)

        self.clear_btn = ttk.Button(input_frame, text="Очистить", command=self.clear_fields)
        self.clear_btn.grid(row=0, column=6, padx=5)

        preview_check = ttk.Checkbutton(
            input_frame,
            text="Увеличивать схему при наведении",
            variable=self.preview_enabled
        )
        preview_check.grid(row=0, column=7, padx=10)

        schemas_frame = ttk.LabelFrame(main_frame, text="Выбор схемы (нажмите на плитку для выбора)", padding="10")
        schemas_frame.pack(fill=tk.BOTH, expand=True)

        canvas_container = ttk.Frame(schemas_frame)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_container, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        images_path = os.path.join(base_path, 'images')

        row = 0
        col = 0
        max_cols = 3

        for schema_id, schema_data in SCHEMAS.items():
            tile_frame = tk.Frame(scrollable_frame, relief=tk.RAISED, borderwidth=3, bg='white')
            tile_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            self.tile_frames[schema_id] = tile_frame

            content_frame = ttk.Frame(tile_frame)
            content_frame.pack(padx=5, pady=5)

            try:
                img_path = schema_data["image"]
                if not os.path.isabs(img_path):
                    img_path = os.path.join(base_path, img_path)

                # Проверяем существование файла
                if not os.path.exists(img_path):
                    # Пробуем альтернативные форматы
                    alt_paths = [
                        os.path.join(images_path, f"scheme_{schema_id}.jpg"),
                        os.path.join(images_path, f"scheme_{schema_id}.png"),
                        os.path.join(images_path, f"schema{schema_id}.png"),
                        os.path.join(images_path, f"schema{schema_id}.jpg"),
                        os.path.join(images_path, f"scheme_1_{schema_id}.jpg"),
                        os.path.join(images_path, f"scheme_3_{schema_id}.jpg"),
                        os.path.join(images_path, f"scheme_4_{schema_id}.jpg"),
                        os.path.join(images_path, f"scheme_5_{schema_id}.jpg"),
                        os.path.join(images_path, f"scheme_6_{schema_id}.jpg"),
                    ]
                    for alt in alt_paths:
                        if os.path.exists(alt):
                            img_path = alt
                            break

                img = Image.open(img_path)
                img = img.resize((250, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.images[schema_id] = photo

                img_label = ttk.Label(content_frame, image=photo, cursor="hand2")
                img_label.pack(padx=5, pady=5)

                img_label.schema_id = schema_id
                img_label.img_path = img_path
                img_label.tile_frame = tile_frame

                img_label.bind("<Enter>", self.on_image_enter)
                img_label.bind("<Leave>", self.on_image_leave)
                img_label.bind("<Button-1>", self.on_image_click)

            except Exception as e:
                ttk.Label(content_frame, text=f"Схема {schema_id}\n(изображение не найдено)").pack(padx=10, pady=10)

            ttk.Label(content_frame, text=schema_data["name"], font=("Arial", 10, "bold")).pack()

            select_btn = ttk.Button(content_frame, text="Выбрать",
                                    command=lambda sid=schema_id: self.select_schema(sid))
            select_btn.pack(pady=5)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе. Введите X и Y, выберите схему и нажмите 'Рассчитать'")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))

        self.highlight_selected(1)

    def on_image_enter(self, event):
        if not self.preview_enabled.get():
            return
        widget = event.widget
        self.current_hover_schema = widget.schema_id
        self.show_preview(widget.schema_id, widget.img_path)

    def on_image_leave(self, event):
        if not self.preview_enabled.get():
            return
        if self.preview_window and self.preview_window.winfo_exists():
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            preview_x = self.preview_window.winfo_rootx()
            preview_y = self.preview_window.winfo_rooty()
            preview_width = self.preview_window.winfo_width()
            preview_height = self.preview_window.winfo_height()
            if not (preview_x <= x <= preview_x + preview_width and
                    preview_y <= y <= preview_y + preview_height):
                self.hide_preview()
        else:
            self.hide_preview()
        self.current_hover_schema = None

    def on_image_click(self, event):
        widget = event.widget
        self.select_schema(widget.schema_id)

    def highlight_selected(self, schema_id):
        for sid, frame in self.tile_frames.items():
            frame.config(bg='white', highlightbackground='white', highlightthickness=0)
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.config(bg='white')
        if schema_id in self.tile_frames:
            frame = self.tile_frames[schema_id]
            frame.config(bg='#90EE90', highlightbackground='#228B22', highlightthickness=3)
            for child in frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.config(bg='#90EE90')

    def select_schema(self, schema_id):
        self.selected_schema.set(schema_id)
        self.status_var.set(f"Выбрана схема: {SCHEMAS[schema_id]['name']}")
        self.highlight_selected(schema_id)
        self.hide_preview()

    def show_preview(self, schema_id, img_path):
        if not self.preview_enabled.get():
            return
        if self.is_preview_showing and self.current_hover_schema == schema_id:
            return
        try:
            self.hide_preview()
            self.preview_window = tk.Toplevel(self.root)
            self.preview_window.title(f"Предпросмотр - Схема {schema_id}")
            self.preview_window.geometry("600x450")
            self.preview_window.attributes('-topmost', True)
            self.preview_window.protocol("WM_DELETE_WINDOW", self.hide_preview)
            self.is_preview_showing = True

            img = Image.open(img_path)
            width, height = img.size
            max_width, max_height = 550, 400
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.preview_photo = photo

            label = ttk.Label(self.preview_window, image=photo)
            label.pack(padx=10, pady=10, expand=True)

            info_frame = ttk.Frame(self.preview_window)
            info_frame.pack(fill=tk.X, pady=5)

            ttk.Label(info_frame, text=f"Схема {schema_id}: {SCHEMAS[schema_id]['name']}",
                      font=("Arial", 10)).pack(side=tk.LEFT, padx=10)

            ttk.Button(info_frame, text="Выбрать",
                       command=lambda: self.select_schema(schema_id)).pack(side=tk.RIGHT, padx=5)
            ttk.Button(info_frame, text="Закрыть",
                       command=self.hide_preview).pack(side=tk.RIGHT, padx=5)

            self.preview_window.bind("<Enter>", lambda e: None)
            self.preview_window.bind("<Leave>", self.on_preview_leave)

        except Exception as e:
            self.hide_preview()

    def on_preview_leave(self, event):
        if not self.preview_enabled.get():
            return
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        preview_x = self.preview_window.winfo_rootx()
        preview_y = self.preview_window.winfo_rooty()
        preview_width = self.preview_window.winfo_width()
        preview_height = self.preview_window.winfo_height()
        if not (preview_x <= x <= preview_x + preview_width and
                preview_y <= y <= preview_y + preview_height):
            widget_at_pointer = self.root.winfo_containing(x, y)
            if widget_at_pointer and hasattr(widget_at_pointer, 'schema_id'):
                return
            self.hide_preview()

    def hide_preview(self):
        if self.preview_window is not None and self.preview_window.winfo_exists():
            self.preview_window.destroy()
        self.preview_window = None
        self.preview_photo = None
        self.is_preview_showing = False
        self.current_hover_schema = None

    def clear_fields(self):
        self.x_var.set("")
        self.y_var.set("")
        self.status_var.set("Поля очищены")

    def calculate(self):
        try:
            x_str = self.x_var.get().strip()
            y_str = self.y_var.get().strip()

            if not x_str or not y_str:
                messagebox.showerror("Ошибка", "Введите значения X и Y")
                return

            x = int(x_str)
            y = int(y_str)

            if x == 0 and y == 0:
                messagebox.showerror("Ошибка", "Сочетание X=0, Y=0 недопустимо")
                return

            if x < 0 or x > 3 or y < 0 or y > 9:
                messagebox.showerror("Ошибка", "X должен быть от 0 до 3, Y от 0 до 9")
                return

            if x == 3 and y != 0:
                messagebox.showerror("Ошибка", "При X=3 допустимо только Y=0")
                return

            schema_id = self.selected_schema.get()

            if schema_id not in SCHEMAS:
                messagebox.showerror("Ошибка", "Выберите схему")
                return

            self.hide_preview()

            self.status_var.set("Выполняется расчет...")
            self.root.update()

            result = calculate_reliability(x, y, schema_id)
            formatted = self.format_results(result)
            html_file = generate_html_report(formatted)

            self.status_var.set(f"Расчет выполнен. Отчет сохранен: {html_file}")

            if messagebox.askyesno("Отчет готов", f"Отчет сохранен в файл:\n{html_file}\n\nОткрыть отчет?"):
                webbrowser.open(html_file)

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{str(e)}")
            self.status_var.set("Ошибка при выполнении расчета")

    def format_results(self, result):
        formatted = {
            "x": result["x"],
            "y": result["y"],
            "S": result["S"],
            "schema_id": result["schema_id"],
            "schema_name": result["schema_name"],
            "schema_note": result.get("schema_note", ""),
            "condition": result["condition"],
            "condition_alpha": result["condition_alpha"],
            "condition_column": result.get("condition_column", "Не указано"),
            "temperature": result["temperature"],
            "kn": result["kn"],
            "table_rows": [],
            "total_intensity": result["total_intensity"],
            "mtbf": result["mtbf"],
            "probabilities": result["probabilities"]
        }

        for row in result["results"]:
            formatted["table_rows"].append({
                "group": row["group"],
                "symbol": row["symbol"],
                "positions": row["positions"],
                "source": row["source"],
                "count": row["count"],
                "lambda_base": row["lambda_base"],
                "alpha": row["alpha"],
                "a5": row["a5"],
                "lambda_group": row["lambda_group"]
            })

        return formatted

    def on_closing(self):
        self.hide_preview()
        self.root.destroy()