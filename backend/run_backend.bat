@echo off
chcp 65001 > nul
echo =================================
echo    ЗАПУСК БЭКЕНДА OFS GLOBAL
echo =================================
echo.

:: Проверяем путь к Python
set PYTHON_CMD=python
if exist ..\.venv\Scripts\python.exe (
    set PYTHON_CMD=..\.venv\Scripts\python.exe
    echo [ИНФО] Используем Python из виртуального окружения .venv
)

:: Доступные команды запуска
if "%1"=="full" goto :full_api
if "%1"=="help" goto :help

:: Запуск стандартного API
echo [ИНФО] Запуск стандартного API (app.main:app)
echo [ИНФО] API будет доступен по адресу: http://localhost:8000
echo [ИНФО] Для остановки нажмите Ctrl+C
echo.
%PYTHON_CMD% -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
goto :end

:full_api
echo [ИНФО] Запуск полного API (full_api)
echo [ИНФО] API будет доступен по адресу: http://localhost:8000
echo [ИНФО] Для остановки нажмите Ctrl+C
echo.
%PYTHON_CMD% -m uvicorn full_api:app --host 127.0.0.1 --port 8000 --reload
goto :end

:help
echo.
echo Использование: run_backend.bat [опция]
echo.
echo Опции:
echo   (пусто)  - запуск стандартного API (app.main:app)
echo   full     - запуск полного API (full_api.py)
echo   help     - показать эту справку
echo.

:end
pause 