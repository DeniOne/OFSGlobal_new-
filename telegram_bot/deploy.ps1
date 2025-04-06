# Скрипт развертывания телеграм-бота
Write-Host "🚀 Начало развертывания телеграм-бота..."

# Проверяем наличие Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python не установлен. Пожалуйста, установите Python 3.8 или выше."
    exit 1
}

# Создаем виртуальное окружение
Write-Host "📦 Создание виртуального окружения..."
python -m venv venv

# Активируем виртуальное окружение
Write-Host "🔌 Активация виртуального окружения..."
.\venv\Scripts\Activate.ps1

# Устанавливаем зависимости
Write-Host "📥 Установка зависимостей..."
pip install python-telegram-bot==13.7
pip install -r requirements.txt

# Проверяем наличие файла .env
if (-not (Test-Path .env)) {
    Write-Host "⚠️ Файл .env не найден. Создаем новый..."
    @"
BOT_TOKEN=7551929518:AAETdyi8z_hnfmEB7ki-VSAYiSkEJtu7jQM
ADMIN_IDS=ваш_телеграм_id
STORAGE_PATH=./data
"@ | Out-File -FilePath .env -Encoding UTF8
    Write-Host "⚠️ Пожалуйста, отредактируйте файл .env и добавьте ваш токен бота и ID администраторов."
}

# Создаем директорию для данных
Write-Host "📁 Создание директории для данных..."
New-Item -ItemType Directory -Force -Path "./data"

# Создаем директорию для логов
Write-Host "📁 Создание директории для логов..."
New-Item -ItemType Directory -Force -Path "./data/logs"

# Создаем службу Windows
Write-Host "⚙️ Создание службы Windows..."
$serviceName = "TelegramBot"
$pythonPath = (Get-Command python).Path
$scriptPath = (Get-Location).Path + "\bot.py"

# Создаем команду для установки службы
$cmd = "nssm install $serviceName $pythonPath $scriptPath"
Write-Host "Выполняется команда: $cmd"
Invoke-Expression $cmd

# Настраиваем службу
Write-Host "⚙️ Настройка службы..."
nssm set $serviceName AppDirectory $scriptPath
nssm set $serviceName DisplayName "Telegram Bot Service"
nssm set $serviceName Description "Служба для телеграм-бота сбора данных сотрудников"
nssm set $serviceName Start SERVICE_AUTO_START

Write-Host "✅ Развертывание завершено!"
Write-Host "📝 Для запуска бота выполните: Start-Service $serviceName"
Write-Host "📝 Для остановки бота выполните: Stop-Service $serviceName"

# Запускаем бота
Write-Host "🚀 Запуск бота..."
python bot.py 