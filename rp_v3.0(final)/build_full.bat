@echo off
chcp 65001 > nul
title Сборка ReliabilityCalculator v1.0

echo ╔══════════════════════════════════════════════════╗
echo ║     Сборка ReliabilityCalculator v1.0           ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: Путь к Python (для пользователя n9zt)
set PYTHON_PATH=C:\Users\n9zt\AppData\Local\Programs\Python\Python314\python.exe

echo [1/5] Проверка Python...

if exist "%PYTHON_PATH%" (
    echo Найден Python: %PYTHON_PATH%
    set PYTHON=%PYTHON_PATH%
) else (
    python --version > nul 2>&1
    if errorlevel 1 (
        echo [ОШИБКА] Python не найден!
        echo.
        echo Введите путь к python.exe вручную:
        set /p PYTHON="Путь к python.exe: "
        if not exist "!PYTHON!" (
            echo [ОШИБКА] Файл не найден: !PYTHON!
            pause
            exit /b 1
        )
    ) else (
        set PYTHON=python
    )
)

echo Используется Python: %PYTHON%
%PYTHON% --version
echo.

:: Очистка старых файлов
echo [2/5] Очистка старых файлов...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec
echo.

:: Установка зависимостей
echo [3/5] Установка зависимостей...
%PYTHON% -m pip install --upgrade pip
%PYTHON% -m pip install Pillow pyinstaller
echo.

:: Сборка EXE
echo [4/5] Сборка исполняемого файла...
%PYTHON% -m PyInstaller --onefile --windowed --name "ReliabilityCalculator" --add-data "images;images" main.py
echo.

if not exist "dist\ReliabilityCalculator.exe" (
    echo [ОШИБКА] Сборка не удалась!
    pause
    exit /b 1
)

:: Создание дистрибутива
echo [5/5] Создание дистрибутива...

if exist "ReliabilityCalculator_v1.0" rmdir /s /q "ReliabilityCalculator_v1.0"
mkdir "ReliabilityCalculator_v1.0"
copy "dist\ReliabilityCalculator.exe" "ReliabilityCalculator_v1.0\"
mkdir "ReliabilityCalculator_v1.0\images"

:: Копирование всех изображений
for %%f in (images\*.jpg) do copy "%%f" "ReliabilityCalculator_v1.0\images\"
for %%f in (images\*.png) do copy "%%f" "ReliabilityCalculator_v1.0\images\"

:: Создание README
(
echo ========================================
echo    РАСЧЁТ ПОКАЗАТЕЛЕЙ НАДЁЖНОСТИ РЭА
echo           Версия 1.0
echo ========================================
echo.
echo СИСТЕМНЫЕ ТРЕБОВАНИЯ:
echo - Windows 10 или Windows 11
echo - 100 МБ свободного места
echo - Нет необходимости устанавливать Python
echo.
echo УСТАНОВКА:
echo 1. Распакуйте архив в любую папку
echo 2. Запустите ReliabilityCalculator.exe
echo.
echo ИСПОЛЬЗОВАНИЕ:
echo 1. Введите X (предпоследняя цифра номера зачетки) - от 0 до 3
echo 2. Введите Y (последняя цифра номера зачетки) - от 0 до 9
echo    (при X=3 допустимо только Y=0)
echo 3. Выберите схему из предложенных вариантов
echo 4. Нажмите кнопку "Рассчитать"
echo 5. Отчет автоматически сохранится в папке reports/
echo 6. При желании отчет можно открыть в браузере
echo.
echo ПРИМЕР:
echo - Номер зачетки: ...24
echo - X = 2, Y = 4
echo - S = 6 -> условия эксплуатации: "Корабельные"
echo - T = 20 + 5*4 = 40°C
echo.
echo РЕЗУЛЬТАТЫ:
echo - Интенсивность отказов Λ (10^-6 ч^-1)
echo - Средняя наработка до отказа T0 (ч)
echo - Вероятность безотказной работы P(t)
echo - Вероятность отказа Q(t)
echo   для 1 года, 5 лет и 10 лет
echo.
echo ОКРУГЛЕНИЕ:
echo - Λ: до трех значащих цифр
echo - T0: до целого числа
echo - P(t) и Q(t): до двух значащих цифр
echo.
echo ========================================
) > "ReliabilityCalculator_v1.0\README.txt"

:: Создание ZIP
echo Создание ZIP-архива...
powershell Compress-Archive -Path ".\ReliabilityCalculator_v1.0" -DestinationPath ".\ReliabilityCalculator_v1.0.zip" -Force

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║     СБОРКА УСПЕШНО ЗАВЕРШЕНА!                   ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo Готовые файлы:
echo   - Папка: ReliabilityCalculator_v1.0\
echo   - Архив: ReliabilityCalculator_v1.0.zip
echo.
echo В папке дистрибутива:
echo   ReliabilityCalculator_v1.0\
echo   ├── ReliabilityCalculator.exe
echo   ├── images\
echo   │   ├── scheme_1_3.jpg
echo   │   ├── scheme_1_4.jpg
echo   │   └── ... (все схемы)
echo   └── README.txt
echo.
echo Запустите ReliabilityCalculator.exe для проверки
echo.
pause