# calculations.py
# Файл со всеми вычислениями и формулами

import math
from data_base import get_condition_by_sum, get_lambda_base, get_a5_value, SCHEMAS


def round_to_significant(value, digits):
    """
    Округление числа до указанного количества значащих цифр
    """
    if value == 0:
        return 0.0

    if abs(value) >= 1:
        return round(value, -int(math.floor(math.log10(abs(value)))) + digits - 1)
    else:
        str_val = f"{value:.10f}"
        mantissa = str_val.split('.')[1] if '.' in str_val else str_val
        pos = 0
        for i, ch in enumerate(mantissa):
            if ch != '0':
                pos = i
                break
        decimal_places = pos + digits
        return round(value, decimal_places)


def calculate_reliability(x, y, schema_id):
    """
    Расчет показателей надежности
    """
    # Проверка допустимых значений
    if x == 0 and y == 0:
        raise ValueError("Сочетание X=0, Y=0 недопустимо")

    if x < 0 or x > 3 or y < 0 or y > 9:
        raise ValueError("X должен быть от 0 до 3, Y от 0 до 9")

    if x == 3 and y != 0:
        raise ValueError("При X=3 допустимо только Y=0")

    # Расчет суммы
    S = x + y

    # Получение условий эксплуатации
    condition = get_condition_by_sum(S)
    col_index = condition["col_index"]  # Индекс столбца для выбора λбаз

    # Расчет температуры
    temperature = 20 + (y * 5)

    # Коэффициент нагрузки (фиксированный)
    kn = 0.5

    # Получение схемы
    if schema_id not in SCHEMAS:
        raise ValueError(f"Схема с номером {schema_id} не найдена")

    schema = SCHEMAS[schema_id]

    # Расчет для каждой группы элементов
    results = []
    total_intensity = 0

    for element in schema["elements"]:
        # Получение базовой интенсивности отказов с учетом столбца
        lambda_base = get_lambda_base(element["lambda_base_key"], col_index)

        # Получение коэффициента a5
        a5 = get_a5_value(element["type"], temperature, kn) if element["has_a5"] else 1.0

        # Расчет интенсивности отказов группы
        lambda_group = element["count"] * lambda_base * condition["alpha"] * a5
        total_intensity += lambda_group

        results.append({
            "group": element["group"],
            "symbol": element["symbol"],
            "positions": element["positions"],
            "source": element["source"],
            "count": element["count"],
            "lambda_base": lambda_base,
            "alpha": condition["alpha"],
            "a5": a5,
            "lambda_group": lambda_group
        })

    # Расчет средней наработки до отказа
    total_intensity_real = total_intensity * 1e-6
    mtbf = 1 / total_intensity_real if total_intensity_real > 0 else float('inf')

    # Расчет вероятностей для разных временных интервалов
    time_intervals = [
        {"years": 1, "days": 365, "hours": 8760},
        {"years": 5, "days": 1826, "hours": 43824},
        {"years": 10, "days": 3652, "hours": 87648}
    ]

    probabilities = []
    for interval in time_intervals:
        t_hours = interval["hours"]
        p = math.exp(-total_intensity_real * t_hours)
        q = 1 - p
        probabilities.append({
            "years": interval["years"],
            "days": interval["days"],
            "hours": interval["hours"],
            "p": p,
            "q": q
        })

    # Округление результатов
    total_intensity_rounded = round_to_significant(total_intensity, 3)
    mtbf_rounded = int(round(mtbf)) if mtbf != float('inf') else float('inf')

    probabilities_rounded = []
    for prob in probabilities:
        probabilities_rounded.append({
            "years": prob["years"],
            "days": prob["days"],
            "hours": prob["hours"],
            "p": round_to_significant(prob["p"], 2),
            "q": round_to_significant(prob["q"], 2)
        })

    return {
        "x": x,
        "y": y,
        "S": S,
        "schema_id": schema_id,
        "schema_name": schema["name"],
        "schema_note": schema.get("note", ""),
        "condition": condition["name"],
        "condition_alpha": condition["alpha"],
        "condition_column": condition["column"],  # <-- ДОБАВЛЕНО!
        "temperature": temperature,
        "kn": kn,
        "results": results,
        "total_intensity": total_intensity_rounded,
        "mtbf": mtbf_rounded,
        "probabilities": probabilities_rounded
    }


def format_results(result):
    """Форматирование результатов для вывода"""
    formatted = {
        "x": result["x"],
        "y": result["y"],
        "S": result["S"],
        "schema_id": result["schema_id"],
        "schema_name": result["schema_name"],
        "schema_note": result["schema_note"],
        "condition": result["condition"],
        "condition_alpha": result["condition_alpha"],
        "condition_column": result["condition_column"],  # <-- ДОБАВЛЕНО!
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