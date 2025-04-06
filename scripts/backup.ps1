# Скрипт для автоматического бэкапа проекта OFS Global
# Запускать из корня проекта командой: .\scripts\backup.ps1

$ErrorActionPreference = "Stop"

# Настройки бэкапа
$projectRoot = $PSScriptRoot | Split-Path -Parent
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$backupName = "ofs_global_backup_$timestamp"
$backupDir = "D:\OFS_Global\backups"
$backupPath = Join-Path -Path $backupDir -ChildPath "$backupName.zip"

# Папки и файлы для исключения из бэкапа
$excludeItems = @(
    "node_modules",
    "venv",
    "__pycache__",
    "*.pyc",
    ".git",
    ".env",
    "*.log",
    "dist",
    "build",
    "*.db"
)

# Создаём директорию для бэкапов, если её нет
if (-not (Test-Path -Path $backupDir)) {
    Write-Host "Создаём директорию для бэкапов: $backupDir" -ForegroundColor Yellow
    New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
}

# Функция для вывода сообщений с цветом
function Write-ColorMessage {
    param (
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# Проверяем наличие PowerShell 5.0+ для использования Compress-Archive
$psVersion = $PSVersionTable.PSVersion
if ($psVersion.Major -lt 5) {
    Write-ColorMessage "Требуется PowerShell 5.0 или выше для использования Compress-Archive." "Red"
    Write-ColorMessage "Текущая версия PowerShell: $($psVersion.ToString())" "Red"
    exit 1
}

# Начинаем процесс бэкапа
Write-ColorMessage "🔄 Начинаем процесс создания бэкапа..." "Cyan"
Write-ColorMessage "📂 Корень проекта: $projectRoot" "Gray"
Write-ColorMessage "📅 Временная метка: $timestamp" "Gray"
Write-ColorMessage "📦 Файл бэкапа будет создан: $backupPath" "Gray"

# Создаём временную директорию для сбора файлов
$tempDir = Join-Path -Path $env:TEMP -ChildPath "ofs_backup_temp_$timestamp"
if (Test-Path -Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force
}
New-Item -Path $tempDir -ItemType Directory -Force | Out-Null

# Функция для создания бэкапа с прогрессом
function Backup-Project {
    param (
        [string]$SourcePath,
        [string]$TempPath,
        [array]$ExcludeList
    )
    
    Write-ColorMessage "🔍 Копируем файлы проекта во временный каталог..." "Yellow"
    
    # Подготавливаем список исключений для robocopy
    $excludeParams = @()
    foreach ($item in $ExcludeList) {
        if ($item -like "*.*") {
            # Для файлов используем /XF
            $excludeParams += "/XF"
            $excludeParams += $item
        } 
        else {
            # Для директорий используем /XD
            $excludeParams += "/XD"
            $excludeParams += $item
        }
    }
    
    # Используем robocopy для копирования файлов с исключениями
    $robocopyArgs = @(
        "`"$SourcePath`"",
        "`"$TempPath`"",
        "/E",
        "/NP",
        "/NFL",
        "/NDL",
        "/MT:8"
    ) + $excludeParams
    
    # Выполняем robocopy
    $robocopyProcess = Start-Process -FilePath "robocopy" -ArgumentList $robocopyArgs -NoNewWindow -PassThru -Wait
    
    # Robocopy возвращает специфические коды завершения, 0-7 считаются успешными
    if ($robocopyProcess.ExitCode -ge 8) {
        Write-ColorMessage "❌ Ошибка при копировании файлов!" "Red"
        return $false
    }
    
    Write-ColorMessage "✅ Файлы успешно скопированы во временный каталог." "Green"
    return $true
}

# Создаём бэкап
try {
    $backupResult = Backup-Project -SourcePath $projectRoot -TempPath $tempDir -ExcludeList $excludeItems
    
    if ($backupResult) {
        Write-ColorMessage "📦 Создаём архив..." "Yellow"
        Compress-Archive -Path "$tempDir\*" -DestinationPath $backupPath -Force
        
        Write-ColorMessage "✅ Бэкап успешно создан: $backupPath" "Green"
        
        # Выводим информацию о размере бэкапа
        $backupSize = (Get-Item -Path $backupPath).Length / 1MB
        Write-ColorMessage "📊 Размер бэкапа: $([math]::Round($backupSize, 2)) МБ" "Cyan"
        
        # Выводим информацию о последних бэкапах
        Write-ColorMessage "`n📜 Последние 5 бэкапов:" "Magenta"
        Get-ChildItem -Path $backupDir -Filter "*.zip" | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -First 5 | 
            Format-Table @{L='Имя';E={$_.Name}}, @{L='Дата';E={$_.LastWriteTime}}, @{L='Размер (МБ)';E={"{0:N2}" -f ($_.Length / 1MB)}}
    }
}
catch {
    Write-ColorMessage "❌ Произошла ошибка при создании бэкапа:" "Red"
    Write-ColorMessage $_.Exception.Message "Red"
    exit 1
}
finally {
    # Удаляем временную директорию
    if (Test-Path -Path $tempDir) {
        Write-ColorMessage "🧹 Удаляем временную директорию..." "Gray"
        Remove-Item -Path $tempDir -Recurse -Force
    }
}

Write-ColorMessage "`n✨ Бэкап проекта OFS Global успешно завершён!" "Green" 