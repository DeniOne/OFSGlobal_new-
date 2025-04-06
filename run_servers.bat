@echo off
chcp 65001 > nul
echo ============================================
echo      ЗАПУСК СЕРВЕРОВ OFS GLOBAL v2.0
echo ============================================
echo.

:: Определяем базовый путь для проекта
set BASE_DIR=%CD%

:: Останавливаем существующие процессы
echo [ИНФО] Останавливаем предыдущие процессы...
taskkill /F /IM python.exe /T >nul 2>nul
taskkill /F /IM node.exe /T >nul 2>nul

:: Запускаем бэкенд (app.main)
echo [ИНФО] Запуск бэкенда (app.main:app)...
echo [ИНФО] Директория: %BASE_DIR%\backend

:: Переходим в директорию backend
if exist "%BASE_DIR%\backend" (
    cd "%BASE_DIR%\backend"
) else (
    echo [ОШИБКА] Директория backend не найдена!
    pause
    exit /b 1
)

:: Определяем Python
set PYTHON_CMD=python
if exist "%BASE_DIR%\.venv\Scripts\python.exe" (
    set PYTHON_CMD=%BASE_DIR%\.venv\Scripts\python.exe
    echo [ИНФО] Используем Python из виртуального окружения .venv
) else if exist "%BASE_DIR%\backend\.venv\Scripts\python.exe" (
    set PYTHON_CMD=%BASE_DIR%\backend\.venv\Scripts\python.exe
    echo [ИНФО] Используем Python из виртуального окружения backend\.venv
)

:: Запускаем бэкенд в отдельном окне
start "OFS Бэкенд (full_api)" cmd /c "cd %BASE_DIR%\backend && %PYTHON_CMD% -m uvicorn full_api:app --host 127.0.0.1 --port 8001"

:: Ждем пару секунд
echo [ИНФО] Ожидание запуска бэкенда (3 секунды)...
ping -n 4 127.0.0.1 > nul

:: Переходим обратно в базовую директорию
cd "%BASE_DIR%"

:: Ищем директорию фронтенда
echo [ИНФО] Поиск директории фронтенда...
set FRONTEND_DIR=

if exist "%BASE_DIR%\frontend" (
    set FRONTEND_DIR=%BASE_DIR%\frontend
    echo [ИНФО] Найдена директория фронтенда: %FRONTEND_DIR%
) else if exist "%BASE_DIR%\..\frontend" (
    set FRONTEND_DIR=%BASE_DIR%\..\frontend
    echo [ИНФО] Найдена директория фронтенда: %FRONTEND_DIR%
) else (
    echo [ПРЕДУПРЕЖДЕНИЕ] Директория frontend не найдена в ожидаемых местах.
    echo [ПРЕДУПРЕЖДЕНИЕ] Попытка запуска бэкенда без фронтенда.
    goto :skip_frontend
)

:: Переходим в директорию фронтенда
cd "%FRONTEND_DIR%"

:: Проверяем наличие Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] Node.js не найден! Запуск только бэкенда.
    goto :skip_frontend
)

:: Проверяем наличие package.json с dev-скриптом
if not exist package.json (
    echo [ОШИБКА] File package.json не найден! Запуск только бэкенда.
    goto :skip_frontend
)

findstr /C:"\"dev\":" package.json >nul
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] Скрипт "dev" не найден в package.json! Запуск только бэкенда.
    goto :skip_frontend
)

:: Устанавливаем зависимости, если необходимо
if not exist node_modules (
    echo [ИНФО] Установка зависимостей npm...
    call npm install
)

:: Запускаем фронтенд
echo [ИНФО] Запуск фронтенда...
start "OFS Фронтенд" cmd /c "npm run dev"

:skip_frontend

:: Возвращаемся в базовую директорию
cd "%BASE_DIR%"

echo.
echo ============================================
echo [ИНФО] Серверы запущены!
echo [ИНФО] Бэкенд API:  http://localhost:8000
echo [ИНФО] Фронтенд:    http://localhost:3003 (если фронтенд был найден)
echo ============================================
echo.
echo [ИНФО] Нажмите любую клавишу для выхода из этого окна.
echo [ИНФО] Серверы продолжат работать в своих окнах.
echo [ИНФО] Чтобы остановить серверы, закройте их окна или используйте Ctrl+C в них.
pause >nul 