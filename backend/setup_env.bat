@echo off
echo ========== НАСТРОЙКА ВИРТУАЛЬНОГО ОКРУЖЕНИЯ ==========

REM Проверяем наличие Python
python --version
if errorlevel 1 (
    echo Python не установлен!
    exit /b 1
)

REM Создаем виртуальное окружение, если его нет
if not exist "venv" (
    echo Создаем виртуальное окружение...
    python -m venv venv
)

REM Активируем виртуальное окружение
call venv\Scripts\activate.bat

REM Устанавливаем зависимости
echo Устанавливаем зависимости...
pip install -r requirements.txt

echo ========== НАСТРОЙКА ЗАВЕРШЕНА ==========
echo Для активации окружения используйте: venv\Scripts\activate.bat 