# Скрипт для извлечения истории чатов из Cursor с использованием .NET
# Автор: AI-помощник
# Дата: 06.04.2025

# Устанавливаем кодировку UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Путь к папке с историей чатов
$workspaceStoragePath = "C:/Users/Admin/AppData/Roaming/Cursor/User/workspaceStorage"

# Путь к выходному файлу
$outputFile = "cursor_chats_dotnet.txt"

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
Add-Content -Path $outputFile -Value "=============================================`r`nИстория чатов Cursor (.NET метод)`r`nДата извлечения: $(Get-Date)`r`n============================================="

# Пытаемся установить пакет System.Data.SQLite через NuGet
Write-Host "Пытаемся получить доступ к библиотеке SQLite..."

# Проверяем, установлен ли NuGet
$nugetPath = $null
try {
    $nugetPath = (Get-Command nuget -ErrorAction SilentlyContinue).Source
}
catch {
    # Ничего не делаем, проверим ниже
}

if (-not $nugetPath) {
    Write-Host "NuGet не установлен. Скачиваем nuget.exe..."
    $nugetUrl = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe"
    $nugetPath = Join-Path (Get-Location).Path "nuget.exe"
    try {
        Invoke-WebRequest -Uri $nugetUrl -OutFile $nugetPath
        Write-Host "NuGet успешно скачан."
    }
    catch {
        Write-Host "Не удалось скачать NuGet. Переходим к альтернативному методу."
        $nugetPath = $null
    }
}

# Пытаемся установить пакет System.Data.SQLite, если NuGet доступен
$sqliteAssemblyPath = $null
if ($nugetPath) {
    $packagesDir = Join-Path (Get-Location).Path "packages"
    if (-not (Test-Path $packagesDir)) {
        New-Item -ItemType Directory -Path $packagesDir | Out-Null
    }
    
    try {
        Write-Host "Устанавливаем пакет System.Data.SQLite..."
        & $nugetPath install System.Data.SQLite.Core -OutputDirectory $packagesDir
        
        # Ищем сборку SQLite
        $sqliteAssembly = Get-ChildItem -Path $packagesDir -Recurse -Filter "System.Data.SQLite.dll" | 
                           Where-Object { $_.FullName -like "*net46*" -or $_.FullName -like "*net47*" -or $_.FullName -like "*net48*" -or $_.FullName -like "*netstandard2.0*" } | 
                           Select-Object -First 1
        
        if ($sqliteAssembly) {
            $sqliteAssemblyPath = $sqliteAssembly.FullName
            Write-Host "SQLite сборка найдена: $sqliteAssemblyPath"
        }
        else {
            Write-Host "Не удалось найти подходящую сборку SQLite."
        }
    }
    catch {
        Write-Host "Ошибка при установке пакета: $_"
    }
}

# Если не удалось установить через NuGet, попробуем скачать сборку напрямую
if (-not $sqliteAssemblyPath) {
    Write-Host "Пытаемся скачать сборку SQLite напрямую..."
    $sqliteZipUrl = "https://system.data.sqlite.org/blobs/1.0.118.0/sqlite-netFx46-binary-bundle-x64-2022-x64.zip"
    $sqliteZipPath = Join-Path (Get-Location).Path "sqlite.zip"
    $sqliteExtractPath = Join-Path (Get-Location).Path "sqlite"
    
    try {
        # Скачиваем архив
        Invoke-WebRequest -Uri $sqliteZipUrl -OutFile $sqliteZipPath
        
        # Создаем директорию для распаковки
        if (-not (Test-Path $sqliteExtractPath)) {
            New-Item -ItemType Directory -Path $sqliteExtractPath | Out-Null
        }
        
        # Распаковываем архив
        Expand-Archive -Path $sqliteZipPath -DestinationPath $sqliteExtractPath -Force
        
        # Ищем сборку SQLite
        $sqliteAssembly = Get-ChildItem -Path $sqliteExtractPath -Recurse -Filter "System.Data.SQLite.dll" | Select-Object -First 1
        
        if ($sqliteAssembly) {
            $sqliteAssemblyPath = $sqliteAssembly.FullName
            Write-Host "SQLite сборка найдена: $sqliteAssemblyPath"
        }
        else {
            Write-Host "Не удалось найти сборку SQLite в скачанном архиве."
        }
        
        # Очищаем временные файлы
        Remove-Item -Path $sqliteZipPath -Force -ErrorAction SilentlyContinue
    }
    catch {
        Write-Host "Ошибка при скачивании сборки: $_"
    }
}

# Проверяем, удалось ли получить доступ к SQLite
if (-not $sqliteAssemblyPath) {
    Write-Host "Не удалось получить доступ к библиотеке SQLite. Пропускаем .NET-метод и переходим к использованию простого метода."
    
    # Запускаем простой скрипт
    if (Test-Path "extract_cursor_chats_simple.ps1") {
        Write-Host "Запускаем простой скрипт для извлечения информации..."
        & .\extract_cursor_chats_simple.ps1
    }
    else {
        Write-Host "Простой скрипт не найден. Запишем только базовую информацию."
        
        # Запись базовой информации о базах данных
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
            }
        }
    }
    
    exit
}

# Функция для чтения данных из SQLite базы данных с использованием .NET
function Read-SqliteDatabase {
    param (
        [string]$DatabasePath,
        [string]$Query
    )
    
    try {
        # Загружаем сборку SQLite
        Add-Type -Path $sqliteAssemblyPath
        
        # Создаем строку подключения
        $connectionString = "Data Source=$DatabasePath;Version=3;"
        
        # Создаем подключение
        $connection = New-Object System.Data.SQLite.SQLiteConnection($connectionString)
        $connection.Open()
        
        # Создаем команду
        $command = $connection.CreateCommand()
        $command.CommandText = $Query
        
        # Создаем адаптер данных
        $adapter = New-Object System.Data.SQLite.SQLiteDataAdapter($command)
        $dataSet = New-Object System.Data.DataSet
        
        # Заполняем набор данных
        [void]$adapter.Fill($dataSet)
        
        # Закрываем подключение
        $connection.Close()
        
        return $dataSet.Tables[0]
    }
    catch {
        Write-Host "Ошибка при чтении базы данных SQLite: $_"
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
        $query = "SELECT rowid, key, value FROM ItemTable WHERE key IN ('aiService.prompts', 'workbench.panel.aichat.view.aichat.chatdata')"
        
        # Выполняем запрос
        Write-Host "Выполняем запрос к базе данных..."
        $results = Read-SqliteDatabase -DatabasePath $dbPath -Query $query
        
        if ($results -and $results.Rows.Count -gt 0) {
            Write-Host "Получено $($results.Rows.Count) строк результатов, обрабатываем..."
            
            # Для каждой строки результатов
            foreach ($row in $results.Rows) {
                $key = $row["key"]
                $value = $row["value"]
                
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
        else {
            Add-Content -Path $outputFile -Value "`r`nНе удалось получить данные из базы данных или данные отсутствуют."
        }
    }
}

Write-Host "Готово! История чатов извлечена и сохранена в файл $outputFile"
Write-Host "Путь к файлу: $((Get-Item $outputFile).FullName)" 