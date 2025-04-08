# Скрипт для извлечения истории чатов из Cursor
# Автор: AI-помощник
# Дата: 06.04.2025

# Устанавливаем кодировку UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Путь к папке с историей чатов
$workspaceStoragePath = "C:/Users/Admin/AppData/Roaming/Cursor/User/workspaceStorage"

# Путь к выходному файлу
$outputFile = "cursor_chats_history.txt"

# Проверяем, существует ли путь
if (-not (Test-Path $workspaceStoragePath)) {
    Write-Host "Путь $workspaceStoragePath не существует. Проверьте правильность пути."
    exit
}

# Очищаем выходной файл, если он существует
if (Test-Path $outputFile) {
    Clear-Content $outputFile
}

# Записываем заголовок в выходной файл
Add-Content -Path $outputFile -Value "=============================================`r`nИстория чатов Cursor`r`nДата извлечения: $(Get-Date)`r`n============================================="

# Поскольку у нас нет System.Data.SQLite.dll, будем использовать альтернативный подход
# Загрузим sqlite3.exe во временную папку и будем использовать его

# Создаем временную папку
$tempFolder = [System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString()
New-Item -ItemType Directory -Path $tempFolder | Out-Null

# Скачиваем sqlite3.exe
$sqliteUrl = "https://www.sqlite.org/2023/sqlite-tools-win32-x86-3410200.zip"
$sqliteZip = "$tempFolder\sqlite.zip"
$sqliteExe = "$tempFolder\sqlite3.exe"

try {
    # Пытаемся скачать SQLite
    Write-Host "Скачиваем SQLite..."
    Invoke-WebRequest -Uri $sqliteUrl -OutFile $sqliteZip
    
    # Распаковываем архив
    Write-Host "Распаковываем архив..."
    Expand-Archive -Path $sqliteZip -DestinationPath $tempFolder
    
    # Находим sqlite3.exe в распакованных файлах
    $sqliteExe = Get-ChildItem -Path $tempFolder -Recurse -Filter "sqlite3.exe" | Select-Object -First 1 -ExpandProperty FullName
    
    if (-not $sqliteExe) {
        throw "Не удалось найти sqlite3.exe в распакованных файлах"
    }
    
    Write-Host "SQLite успешно установлен: $sqliteExe"
}
catch {
    Write-Host "Ошибка при скачивании/распаковке SQLite: $_"
    Write-Host "Попробуем альтернативный подход через PowerShell..."
    
    # Альтернативный подход: используем PowerShell для прямого чтения файла SQLite
    # Но это сложнее и не всегда работает корректно
    # Для простоты просто запишем информацию о файлах без извлечения содержимого
    
    $folders = Get-ChildItem -Path $workspaceStoragePath -Directory
    
    foreach ($folder in $folders) {
        $dbPath = Join-Path $folder.FullName "state.vscdb"
        $workspaceJsonPath = Join-Path $folder.FullName "workspace.json"
        
        if (Test-Path $dbPath) {
            $workspaceInfo = "Нет информации о рабочем пространстве"
            if (Test-Path $workspaceJsonPath) {
                try {
                    $workspaceJson = Get-Content -Path $workspaceJsonPath -Raw | ConvertFrom-Json
                    $workspaceInfo = $workspaceJson.folder
                }
                catch {
                    $workspaceInfo = "Ошибка при чтении workspace.json"
                }
            }
            
            Add-Content -Path $outputFile -Value "`r`n`r`n========== Рабочее пространство: $($folder.Name) =========="
            Add-Content -Path $outputFile -Value "Путь к рабочему пространству: $workspaceInfo"
            Add-Content -Path $outputFile -Value "Путь к базе данных: $dbPath"
            Add-Content -Path $outputFile -Value "Размер базы данных: $((Get-Item $dbPath).Length) байт"
            Add-Content -Path $outputFile -Value "Дата изменения: $((Get-Item $dbPath).LastWriteTime)"
            Add-Content -Path $outputFile -Value "`r`nНе удалось извлечь содержимое чатов из-за отсутствия инструмента SQLite."
            Add-Content -Path $outputFile -Value "Для извлечения содержимого установите SQLite или используйте инструмент SQLite Browser."
        }
    }
    
    Write-Host "Информация о файлах баз данных записана в $outputFile"
    exit
}

# Функция для выполнения запроса SQLite с помощью sqlite3.exe
function Query-Sqlite {
    param (
        [string]$DatabasePath,
        [string]$Query,
        [string]$OutputFormat = "json"
    )
    
    try {
        $result = & $sqliteExe -$OutputFormat $DatabasePath $Query
        return $result
    }
    catch {
        Write-Host "Ошибка при выполнении запроса: $_"
        return $null
    }
}

# Перебираем все папки в workspaceStorage
$folders = Get-ChildItem -Path $workspaceStoragePath -Directory
Write-Host "Найдено $($folders.Count) папок с рабочими пространствами"

foreach ($folder in $folders) {
    $dbPath = Join-Path $folder.FullName "state.vscdb"
    $workspaceJsonPath = Join-Path $folder.FullName "workspace.json"
    
    if (Test-Path $dbPath) {
        Write-Host "Обрабатываем базу данных: $dbPath"
        
        # Получаем информацию о рабочем пространстве
        $workspaceInfo = "Нет информации о рабочем пространстве"
        if (Test-Path $workspaceJsonPath) {
            try {
                $workspaceJson = Get-Content -Path $workspaceJsonPath -Raw | ConvertFrom-Json
                $workspaceInfo = $workspaceJson.folder
            }
            catch {
                $workspaceInfo = "Ошибка при чтении workspace.json"
            }
        }
        
        Add-Content -Path $outputFile -Value "`r`n`r`n========== Рабочее пространство: $($folder.Name) =========="
        Add-Content -Path $outputFile -Value "Путь к рабочему пространству: $workspaceInfo"
        Add-Content -Path $outputFile -Value "Путь к базе данных: $dbPath"
        Add-Content -Path $outputFile -Value "Размер базы данных: $((Get-Item $dbPath).Length) байт"
        Add-Content -Path $outputFile -Value "Дата изменения: $((Get-Item $dbPath).LastWriteTime)"
        
        # Запрос для получения истории чатов
        $query = "SELECT rowid, [key], value FROM ItemTable WHERE [key] IN ('aiService.prompts', 'workbench.panel.aichat.view.aichat.chatdata')"
        
        # Выполняем запрос
        Write-Host "Выполняем запрос к базе данных..."
        $results = Query-Sqlite -DatabasePath $dbPath -Query $query -OutputFormat "json"
        
        if ($results) {
            Write-Host "Получены результаты, обрабатываем..."
            # Преобразуем результаты из JSON
            try {
                $chatData = $results | ConvertFrom-Json
                
                # Для каждого найденного ключа
                foreach ($item in $chatData) {
                    $key = $item.key
                    $value = $item.value
                    
                    Add-Content -Path $outputFile -Value "`r`n----- Ключ: $key -----"
                    
                    if ($key -eq "workbench.panel.aichat.view.aichat.chatdata") {
                        try {
                            # Пытаемся разобрать JSON
                            $chatJson = $value | ConvertFrom-Json
                            
                            # Перебираем все чаты
                            foreach ($chat in $chatJson.chats) {
                                Add-Content -Path $outputFile -Value "`r`n### Чат ID: $($chat.id)"
                                Add-Content -Path $outputFile -Value "Название: $($chat.title)"
                                Add-Content -Path $outputFile -Value "Дата создания: $($chat.createdAt)"
                                Add-Content -Path $outputFile -Value "Модель: $($chat.model)"
                                Add-Content -Path $outputFile -Value "`r`n--- Сообщения ---"
                                
                                # Перебираем все сообщения в чате
                                foreach ($message in $chat.messages) {
                                    $role = $message.role
                                    $content = $message.content
                                    
                                    Add-Content -Path $outputFile -Value "`r`n[$role]: $content"
                                }
                            }
                        }
                        catch {
                            Add-Content -Path $outputFile -Value "Ошибка при разборе данных чата: $_"
                            Add-Content -Path $outputFile -Value "Сырые данные: $value"
                        }
                    }
                    elseif ($key -eq "aiService.prompts") {
                        try {
                            # Пытаемся разобрать JSON
                            $promptsJson = $value | ConvertFrom-Json
                            
                            Add-Content -Path $outputFile -Value "`r`n--- Промпты ---"
                            # Перебираем все промпты
                            foreach ($prompt in $promptsJson) {
                                Add-Content -Path $outputFile -Value "`r`n### Промпт ID: $($prompt.id)"
                                Add-Content -Path $outputFile -Value "Запрос: $($prompt.query)"
                                Add-Content -Path $outputFile -Value "Дата: $($prompt.date)"
                                Add-Content -Path $outputFile -Value "Модель: $($prompt.model)"
                                Add-Content -Path $outputFile -Value "Ответ: $($prompt.response)"
                            }
                        }
                        catch {
                            Add-Content -Path $outputFile -Value "Ошибка при разборе данных промптов: $_"
                            Add-Content -Path $outputFile -Value "Сырые данные: $value"
                        }
                    }
                    else {
                        Add-Content -Path $outputFile -Value "Непонятный формат данных"
                        Add-Content -Path $outputFile -Value $value
                    }
                }
            }
            catch {
                Add-Content -Path $outputFile -Value "Ошибка при обработке результатов: $_"
                Add-Content -Path $outputFile -Value "Сырые данные: $results"
            }
        }
        else {
            Add-Content -Path $outputFile -Value "`r`nНе удалось получить данные из базы данных."
        }
    }
}

# Очищаем временную папку
Remove-Item -Path $tempFolder -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Готово! История чатов извлечена и сохранена в файл $outputFile"
Write-Host "Путь к файлу: $((Get-Item $outputFile).FullName)" 