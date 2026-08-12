# html.py
# Файл для создания HTML-отчёта

import os
from datetime import datetime


def generate_html_report(result, filename=None):
    """
    Генерация HTML-отчета

    Args:
        result: результат расчета от calculations.py
        filename: имя файла для сохранения (опционально)

    Returns:
        str: содержимое HTML-отчета
    """
    # Определяем имя файла, если не указано
    if filename is None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"reports/Схема_{result['schema_id']:02d}_X{result['x']}_Y{result['y']}_{timestamp}.html"

    # Создаем директорию reports, если её нет
    os.makedirs("reports", exist_ok=True)

    # Формируем HTML
    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчёт по расчёту надёжности - Схема {result['schema_id']:02d}</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            margin: 20px;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .header-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .info-item {{
            padding: 5px 10px;
        }}
        .info-item strong {{
            color: #2c3e50;
        }}
        .schema-note {{
            background-color: #f8f9fa;
            padding: 10px;
            border-left: 4px solid #3498db;
            margin-bottom: 20px;
            font-style: italic;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th {{
            background-color: #2c3e50;
            color: white;
            padding: 10px;
            text-align: center;
            border: 1px solid #34495e;
        }}
        td {{
            padding: 8px;
            text-align: center;
            border: 1px solid #bdc3c7;
        }}
        td.left {{
            text-align: left;
            padding-left: 12px;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e8f4f8;
        }}
        .total-section {{
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .total-item {{
            padding: 8px 0;
            border-bottom: 1px solid #bdc3c7;
        }}
        .total-item:last-child {{
            border-bottom: none;
        }}
        .probabilities {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
        }}
        .prob-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #bdc3c7;
        }}
        .prob-card h3 {{
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #3498db;
            color: #7f8c8d;
            font-size: 12px;
        }}
        .highlight {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .unit {{
            font-style: italic;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        @media print {{
            body {{
                background-color: white;
                margin: 0;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                border-radius: 0;
                padding: 20px;
            }}
            tr:hover {{
                background-color: inherit;
            }}
            .prob-card {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Расчёт показателей надёжности радиоэлектронного устройства</h1>

        

        <div class="header-info">
            <div class="info-item"><strong>X (десятки):</strong> {result['x']}</div>
            <div class="info-item"><strong>Y (единицы):</strong> {result['y']}</div>
            <div class="info-item"><strong>Сумма S = X + Y:</strong> {result['S']}</div>
            <div class="info-item"><strong>Схема:</strong> {result['schema_name']}</div>
            <div class="info-item"><strong>Условия эксплуатации:</strong> {result['condition']} (α<sub>Σ</sub> = {result['condition_alpha']})</div>
            <div class="info-item"><strong>Столбец таблицы λ<sub>баз</sub>:</strong> {result['condition_column']}</div>
            <div class="info-item"><strong>Температура:</strong> {result['temperature']}°C</div>
            <div class="info-item"><strong>Коэффициент нагрузки K<sub>н</sub>:</strong> {result['kn']}</div>
        </div>

        <div class="schema-note">
            <strong>Примечание:</strong> {result['schema_note']}
        </div>

        <h2>Расчёт интенсивности отказов</h2>
        <table>
            <thead>
                <tr>
                    <th>№</th>
                    <th>Группа элементов</th>
                    <th>УГО</th>
                    <th>Позиционные обозначения</th>
                    <th>Источник</th>
                    <th>Количество n<sub>i</sub></th>
                    <th>λ<sub>i баз</sub>, 10<sup>-6</sup> ч<sup>-1</sup></th>
                    <th>α<sub>Σ</sub></th>
                    <th>α<sub>5</sub></th>
                    <th>Λ<sub>i</sub>, 10<sup>-6</sup> ч<sup>-1</sup></th>
                </tr>
            </thead>
            <tbody>
"""

    # Добавляем строки таблицы
    for idx, row in enumerate(result['table_rows'], 1):
        html_content += f"""
                <tr>
                    <td>{idx}</td>
                    <td class="left">{row['group']}</td>
                    <td>{row['symbol']}</td>
                    <td class="left">{row['positions']}</td>
                    <td>{row['source']}</td>
                    <td>{row['count']}</td>
                    <td>{row['lambda_base']:.4f}</td>
                    <td>{row['alpha']:.2f}</td>
                    <td>{row['a5']:.2f}</td>
                    <td>{row['lambda_group']:.6f}</td>
                </tr>
"""

    html_content += f"""
            </tbody>
        </table>

        <div class="total-section">
            <div class="total-item">
                <strong>Интенсивность отказов схемы Λ = ΣΛ<sub>i</sub>:</strong> 
                {result['total_intensity']:.3g} × 10<sup>-6</sup> ч<sup>-1</sup>
            </div>
            <div class="total-item">
                <strong>Средняя наработка до отказа T<sub>0</sub> = 1 / (Λ · 10<sup>-6</sup>):</strong> 
                {result['mtbf']:.0f} ч
            </div>
        </div>

        <h2>Вероятности безотказной работы и отказа</h2>
        <div class="probabilities">
"""

    # Добавляем карточки с вероятностями
    for prob in result['probabilities']:
        years_text = f"{prob['years']} год" if prob['years'] == 1 else f"{prob['years']} лет"
        html_content += f"""
            <div class="prob-card">
                <h3>{years_text}</h3>
                <p><strong>Время:</strong> {prob['days']} суток ({prob['hours']} ч)</p>
                <p><strong>P(t):</strong> {prob['p']:.2g}</p>
                <p><strong>Q(t):</strong> {prob['q']:.2g}</p>
            </div>
"""

    html_content += f"""
        </div>

        <div class="footer">
            <p>Отчёт сформирован: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}</p>
            <p>Расчёт выполнен по заданию на контрольную работу №2</p>
            <p style="font-size: 10px; color: #95a5a6;">
                Примечание: Λ округлена до трёх значащих цифр, T₀ до целого числа, P(t) и Q(t) до двух значащих цифр
            </p>
        </div>
    </div>
</body>
</html>
"""

    # Сохраняем файл
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return filename