@echo off
chcp 65001 > nul
echo ============================================
echo        ЗАПУСК МОДУЛЬНОГО API OFS GLOBAL
echo ============================================
echo.

:: Определяем базовый путь для проекта
set BASE_DIR=%CD%

:: Проверяем наличие Python
set PYTHON_CMD=python
if exist .venv\Scripts\python.exe (
    set PYTHON_CMD=.venv\Scripts\python.exe
    echo [ИНФО] Используем Python из виртуального окружения .venv
) else if exist backend\.venv\Scripts\python.exe (
    set PYTHON_CMD=backend\.venv\Scripts\python.exe
    echo [ИНФО] Используем Python из виртуального окружения backend\.venv
) else if exist backend\venv_new\Scripts\python.exe (
    set PYTHON_CMD=backend\venv_new\Scripts\python.exe
    echo [ИНФО] Используем Python из виртуального окружения backend\venv_new
)

:: Переходим в директорию backend, если она существует
if exist backend (
    cd backend
) else (
    echo [ОШИБКА] Директория backend не найдена!
    pause
    exit /b 1
)

:: Проверяем существование папки app
if not exist app (
    echo [ОШИБКА] Папка app не найдена в каталоге backend!
    echo [ИНФО] Возможно, рефакторинг API еще не завершен.
    echo [ИНФО] Попробуйте использовать start_full_api.bat вместо этого.
    cd "%BASE_DIR%"
    pause
    exit /b 1
)

:: Проверяем существование файла main.py в папке app
if not exist app\main.py (
    echo [ОШИБКА] Файл main.py не найден в каталоге backend/app!
    echo [ИНФО] Модульная структура API еще не готова.
    echo [ИНФО] Попробуйте использовать start_full_api.bat вместо этого.
    cd "%BASE_DIR%"
    pause
    exit /b 1
)

:: Запуск модульного API
echo [ИНФО] Запуск модульного API (app.main)
echo [ИНФО] API будет доступно по адресу: http://localhost:8001
echo [ИНФО] Для остановки нажмите Ctrl+C
echo.

:: Запускаем модульное API
%PYTHON_CMD% -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

echo [ИНФО] API остановлено.
cd "%BASE_DIR%"
pause 