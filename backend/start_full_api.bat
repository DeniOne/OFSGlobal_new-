@echo off
chcp 65001 > nul
echo ============================================
echo        ЗАПУСК FULL API OFS GLOBAL
echo ============================================
echo.

:: Проверяем наличие Python
set PYTHON_CMD=python
if exist .venv\Scripts\python.exe (
    set PYTHON_CMD=.venv\Scripts\python.exe
    echo [ИНФО] Используем Python из виртуального окружения .venv
) else if exist backend\.venv\Scripts\python.exe (
    set PYTHON_CMD=backend\.venv\Scripts\python.exe
    echo [ИНФО] Используем Python из виртуального окружения backend\.venv
)

:: Запуск full_api (если запущено - выведется ошибка)
echo [ИНФО] Запуск полного API (full_api)
echo [ИНФО] API будет доступно по адресу: http://localhost:8000
echo [ИНФО] Для остановки нажмите Ctrl+C
echo.

:: Переходим в директорию backend, если она существует
if exist backend (
    cd backend
)

:: Запускаем full_api
%PYTHON_CMD% -m uvicorn full_api:app --host 127.0.0.1 --port 8000 --reload

echo [ИНФО] API остановлено.
pause 