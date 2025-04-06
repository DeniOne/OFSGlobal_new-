# Скрипт для запуска проекта OFS Global
# Устанавливает все зависимости и запускает фронтенд и бэкенд

# Настраиваем кодировку консоли для корректного отображения кириллицы
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Функция для проверки и установки пакетов Python
function Install-PythonPackages {
    Write-Host "Проверка и установка необходимых пакетов Python..." -ForegroundColor Cyan

    # Список необходимых пакетов
    $packages = @("fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose", "passlib", "python-multipart", "email-validator", "alembic", "python-dotenv")

    foreach ($package in $packages) {
        Write-Host "Проверка пакета $package..." -ForegroundColor Gray
        # Проверяем, установлен ли пакет
        $installed = pip list | Select-String -Pattern "^$package "
        
        if (-not $installed) {
            Write-Host "Установка пакета $package..." -ForegroundColor Yellow
            pip install $package
        } else {
            Write-Host "Пакет $package уже установлен." -ForegroundColor Green
        }
    }

    Write-Host "Все необходимые пакеты Python установлены!" -ForegroundColor Green
}

# Основная функция запуска
function Start-OFSProject {
    # Используем абсолютные пути для надежности
    $projectRoot = "D:\OFS_Global\ofs_project\ofs_new"
    $backendPath = "$projectRoot\backend"
    $frontendPath = "$projectRoot\frontend"
    
    # Переходим в корневую директорию проекта
    Set-Location -Path $projectRoot
    Write-Host "Текущая директория: $projectRoot" -ForegroundColor Cyan
    
    # Активируем виртуальное окружение, если оно существует
    $venvPath = "D:\OFS_Global\ofs_project\new_venv"
    if (Test-Path -Path "$venvPath\Scripts\Activate.ps1") {
        Write-Host "Активируем виртуальное окружение Python..." -ForegroundColor Cyan
        & "$venvPath\Scripts\Activate.ps1"
    } else {
        Write-Host "Виртуальное окружение не найдено, используем системный Python." -ForegroundColor Yellow
    }
    
    # Устанавливаем пакеты Python
    Install-PythonPackages
    
    # Проверяем наличие директорий backend и frontend
    if (-not (Test-Path -Path $backendPath)) {
        Write-Host "Ошибка: Директория backend не найдена по пути $backendPath" -ForegroundColor Red
        return
    }
    
    if (-not (Test-Path -Path $frontendPath)) {
        Write-Host "Ошибка: Директория frontend не найдена по пути $frontendPath" -ForegroundColor Red
        return
    }
    
    # Запускаем бэкенд в отдельном процессе
    Write-Host "Запуск бэкенд-сервера из $backendPath..." -ForegroundColor Cyan
    $backendProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command ""cd '$backendPath'; uvicorn app.main:app --reload""" -PassThru -WindowStyle Normal
    
    # Ждем немного, чтобы бэкенд успел запуститься
    Start-Sleep -Seconds 3
    
    # Запускаем фронтенд в отдельном процессе
    Write-Host "Запуск фронтенд-сервера из $frontendPath..." -ForegroundColor Cyan
    $frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command ""cd '$frontendPath'; npm run build""" -PassThru -WindowStyle Normal
    
    # Ждем, пока фронтенд полностью перекомпилируется
    Start-Sleep -Seconds 10
    
    # Запускаем фронтенд в отдельном процессе
    $frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-Command ""cd '$frontendPath'; npm run dev""" -PassThru -WindowStyle Normal
    
    Write-Host "Проект OFS Global запущен!" -ForegroundColor Green
    Write-Host "Бэкенд доступен по адресу: http://localhost:8000" -ForegroundColor Yellow
    Write-Host "Фронтенд доступен по адресу: http://localhost:3000" -ForegroundColor Yellow
    Write-Host "Для остановки серверов закройте окна PowerShell или нажмите Ctrl+C" -ForegroundColor Red
    
    # Ждем, пока пользователь не закроет скрипт
    try {
        # Держим скрипт запущенным, пока пользователь не нажмет Ctrl+C
        while ($true) { Start-Sleep -Seconds 1 }
    } finally {
        # При выходе останавливаем процессы
        if ($backendProcess -and (-not $backendProcess.HasExited)) {
            Stop-Process -Id $backendProcess.Id -Force
        }
        if ($frontendProcess -and (-not $frontendProcess.HasExited)) {
            Stop-Process -Id $frontendProcess.Id -Force
        }
    }
}

# Запускаем проект
Start-OFSProject 