# Останавливаем выполнение при ошибках
$ErrorActionPreference = "Stop"

# Создаем метку времени для имени бэкапа
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

# Создаем директории для бэкапа
$backupDir = "backups"
$tempDir = "temp_$timestamp"
$configDir = "$tempDir\_configs_and_db"

# Создаем необходимые директории
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
New-Item -ItemType Directory -Force -Path $configDir | Out-Null

Write-Host "Копирование важных файлов..."

# Копируем конфиги и базы данных
Get-ChildItem -Path "." -Recurse -File | Where-Object {
    $_.Extension -in ".db",".env",".ini",".json",".conf"
} | ForEach-Object {
    $destPath = Join-Path $configDir $_.Name
    Copy-Item $_.FullName -Destination $destPath -Force
    Write-Host "Скопирован файл: $($_.Name)"
}

Write-Host "Копирование файлов проекта..."

# Копируем все остальные файлы проекта
Get-ChildItem -Path "." -Exclude @("node_modules",".git","venv","backups",$tempDir) | Copy-Item -Destination $tempDir -Recurse -Force

# Создаем ZIP архив
$backupFile = Join-Path $backupDir "backup_$timestamp.zip"
Compress-Archive -Path $tempDir\* -DestinationPath $backupFile -Force

# Удаляем временную директорию
Remove-Item -Path $tempDir -Recurse -Force

Write-Host "Бэкап успешно создан: $backupFile" 