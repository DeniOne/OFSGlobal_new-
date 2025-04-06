# Скрипт для полного резервного копирования проекта
# Создает ZIP-файл со всем проектом, базой данных и конфигами в директории backups/

$ErrorActionPreference = "Stop"

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupName = "ofs_project_backup_$timestamp"
$backupDir = "backups"
$backupPath = "$backupDir\$backupName.zip"

# Создаем директорию для резервных копий, если ее нет
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
    Write-Host "Создана директория $backupDir"
}

# Список директорий и файлов, которые нужно исключить из бэкапа
$excludedDirs = @(
    "*\node_modules\*", 
    "*\.git\*", 
    "*\venv\*", 
    "*\.venv\*", 
    "*\__pycache__\*",
    "*\backups\*",
    "*\dist\*",
    "*\build\*"
)

# Список файлов для специального копирования
$specialFiles = @(
    "*.db",        # SQLite базы данных
    ".env",        # Конфиги окружения
    "*.env",       # Все .env файлы
    "*.ini",       # Конфиги
    "*.conf",      # Конфиги
    "*.config",    # Конфиги
    "*.json"       # JSON конфиги
)

Write-Host "Создаем резервную копию проекта..." -ForegroundColor Cyan

# Создаем временную директорию для подготовки файлов
$tempDir = "$backupDir\temp_$timestamp"
$configsDir = "$tempDir\_configs_and_db"

New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
New-Item -ItemType Directory -Path $configsDir -Force | Out-Null

# Функция для проверки исключений
function Test-ShouldExclude($path) {
    foreach ($pattern in $excludedDirs) {
        if ($path -like $pattern) {
            return $true
        }
    }
    return $false
}

# Копируем специальные файлы
Write-Host "Копирование конфигов и баз данных..."
foreach ($pattern in $specialFiles) {
    Get-ChildItem -Path "." -Recurse -File | Where-Object {
        -not (Test-ShouldExclude $_.FullName) -and ($_.Name -like $pattern)
    } | ForEach-Object {
        $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 1)
        $destination = Join-Path $configsDir $relativePath
        $destinationDir = Split-Path $destination -Parent
        
        if (-not (Test-Path $destinationDir)) {
            New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
        }
        
        Copy-Item $_.FullName -Destination $destination -Force
        Write-Host "  Скопирован файл: $relativePath" -ForegroundColor Yellow
    }
}

# Копируем остальные файлы проекта
Write-Host "Копирование файлов проекта..."
Get-ChildItem -Path "." -Recurse -File | Where-Object {
    $file = $_
    -not (Test-ShouldExclude $_.FullName) -and -not ($specialFiles | Where-Object { $file.Name -like $_ })
} | ForEach-Object {
    $relativePath = $_.FullName.Substring((Get-Location).Path.Length + 1)
    $destination = Join-Path $tempDir $relativePath
    $destinationDir = Split-Path $destination -Parent
    
    if (-not (Test-Path $destinationDir)) {
        New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
    }
    
    Copy-Item $_.FullName -Destination $destination -Force
}

# Создаем ZIP архив
Write-Host "Создание ZIP архива..."
Compress-Archive -Path "$tempDir\*" -DestinationPath $backupPath -CompressionLevel Optimal -Force

Write-Host "Резервная копия успешно создана: $backupPath" -ForegroundColor Green
Write-Host "  - Все файлы проекта" -ForegroundColor Green
Write-Host "  - Базы данных и конфиги в директории _configs_and_db" -ForegroundColor Green

# Очищаем временные файлы
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force
} 