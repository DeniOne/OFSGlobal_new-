# Простой скрипт для извлечения информации о чатах из Cursor
# Автор: AI-помощник
# Дата: 06.04.2025

# Установка кодировки UTF-8 без BOM
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'

# Путь к папке с историей чатов
$workspaceStoragePath = "C:/Users/Admin/AppData/Roaming/Cursor/User/workspaceStorage"

# Путь к выходному файлу
$outputFile = "cursor_chats_info.txt"

# Проверяем, существует ли путь
if (-not (Test-Path $workspaceStoragePath)) {
    Write-Host "Path $workspaceStoragePath does not exist. Please check the path."
    exit
}

# Очищаем выходной файл, если он существует
if (Test-Path $outputFile) {
    Clear-Content $outputFile
}

# Записываем заголовок в выходной файл
Add-Content -Path $outputFile -Value "=============================================`r`nCursor Chat History Info`r`nExtraction Date: $(Get-Date)`r`n============================================="

# Перебираем все папки в workspaceStorage
$folders = Get-ChildItem -Path $workspaceStoragePath -Directory
Write-Host "Found $($folders.Count) workspace folders"

foreach ($folder in $folders) {
    $dbPath = Join-Path $folder.FullName "state.vscdb"
    $workspaceJsonPath = Join-Path $folder.FullName "workspace.json"
    
    if (Test-Path $dbPath) {
        $workspaceInfo = "No workspace information"
        if (Test-Path $workspaceJsonPath) {
            try {
                $workspaceJson = Get-Content -Path $workspaceJsonPath -Raw | ConvertFrom-Json
                $workspaceInfo = $workspaceJson.folder
            }
            catch {
                $workspaceInfo = "Error reading workspace.json"
            }
        }
        
        Add-Content -Path $outputFile -Value "`r`n`r`n========== Workspace: $($folder.Name) =========="
        Add-Content -Path $outputFile -Value "Workspace path: $workspaceInfo"
        Add-Content -Path $outputFile -Value "Database path: $dbPath"
        Add-Content -Path $outputFile -Value "Database size: $((Get-Item $dbPath).Length) bytes"
        Add-Content -Path $outputFile -Value "Last modified: $((Get-Item $dbPath).LastWriteTime)"
        
        # Копируем файл базы данных во временный файл для ручной обработки
        $tempDbPath = Join-Path (Get-Location).Path "cursor_chat_$($folder.Name).vscdb"
        try {
            Copy-Item -Path $dbPath -Destination $tempDbPath -Force
            Add-Content -Path $outputFile -Value "Database copy: $tempDbPath"
            Add-Content -Path $outputFile -Value "`r`nTo view the content, install SQLite Browser (https://sqlitebrowser.org/) and open the file."
            Add-Content -Path $outputFile -Value "Execute the following query in SQLite Browser:"
            Add-Content -Path $outputFile -Value "SELECT rowid, [key], value FROM ItemTable WHERE [key] IN ('aiService.prompts', 'workbench.panel.aichat.view.aichat.chatdata')"
            
            Write-Host "Database copy created: $tempDbPath"
        }
        catch {
            Add-Content -Path $outputFile -Value "Failed to create database copy: $_"
            Write-Host "Error copying database: $_"
        }
    }
}

Write-Host "Done! Chat information has been written to $outputFile"
Write-Host "File path: $((Get-Item $outputFile).FullName)"

# Instructions for next steps
Write-Host "`r`nNext steps:"
Write-Host "1. Install SQLite Browser from https://sqlitebrowser.org/"
Write-Host "2. Open the *.vscdb files using SQLite Browser"
Write-Host "3. Go to the 'Execute SQL' tab"
Write-Host "4. Execute query: SELECT rowid, [key], value FROM ItemTable WHERE [key] IN ('aiService.prompts', 'workbench.panel.aichat.view.aichat.chatdata')"
Write-Host "5. Find rows with 'key' column equal to 'workbench.panel.aichat.view.aichat.chatdata'"
Write-Host "6. The value in the 'value' column is the JSON with chat history" 