# Скрипт для бэкапа
$ErrorActionPreference = "Stop"

# Настройки
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$backupDir = "backups"
$backupPath = "$backupDir\backup_$timestamp.zip"
$tempDir = "$backupDir\temp_$timestamp"
$configsDir = "$tempDir\_configs_and_db"

# Создаем директории
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
New-Item -ItemType Directory -Path $configsDir -Force | Out-Null

Write-Host "Создаем бэкап..." -ForegroundColor Cyan

# Копируем важные файлы
Get-ChildItem -Path "." -Include "*.db",".env","*.env","*.ini","*.json","*.conf" -Recurse -File | 
ForEach-Object {
    $dest = Join-Path $configsDir $_.Name
    Copy-Item $_.FullName -Destination $dest -Force
    Write-Host "Копируем: $($_.Name)" -ForegroundColor Yellow
}

# Копируем остальные файлы
Get-ChildItem -Path "." -Exclude "node_modules",".git","venv",".venv","__pycache__","backups" -Recurse |
Where-Object { $_.PSIsContainer -eq $false } |
ForEach-Object {
    $dest = Join-Path $tempDir $_.Name
    Copy-Item $_.FullName -Destination $dest -Force
}

# Создаем архив
Compress-Archive -Path "$tempDir\*" -DestinationPath $backupPath -Force

# Очищаем
Remove-Item -Path $tempDir -Recurse -Force

Write-Host "Готово! Бэкап создан: $backupPath" -ForegroundColor Green 