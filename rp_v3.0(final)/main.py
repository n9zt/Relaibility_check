# main.py
# Точка входа в программу

import tkinter as tk
from ui import ReliabilityApp

def main():
    root = tk.Tk()
    app = ReliabilityApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()