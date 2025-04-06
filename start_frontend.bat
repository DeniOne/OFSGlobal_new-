@echo off
chcp 65001 > nul
echo ============================================
echo        ЗАПУСК ФРОНТЕНДА OFS GLOBAL
echo ============================================
echo.

:: Проверяем наличие Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ОШИБКА] Node.js не найден! Убедитесь, что Node.js установлен и доступен в PATH.
    pause
    exit /b 1
)

:: Переходим в директорию frontend, если она существует
if exist frontend (
    cd frontend
) else (
    echo [ОШИБКА] Директория frontend не найдена!
    pause
    exit /b 1
)

:: Проверяем наличие node_modules
if not exist node_modules (
    echo [ИНФО] Устанавливаем зависимости npm...
    call npm install
    if %ERRORLEVEL% NEQ 0 (
        echo [ОШИБКА] Не удалось установить зависимости.
        pause
        exit /b 1
    )
)

:: Запускаем фронтенд
echo [ИНФО] Запуск фронтенда...
echo [ИНФО] Фронтенд будет доступен по адресу: http://localhost:3003
echo [ИНФО] Для остановки нажмите Ctrl+C
echo.

call npm run dev

echo [ИНФО] Фронтенд остановлен.
pause 