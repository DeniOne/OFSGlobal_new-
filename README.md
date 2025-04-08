# Утилита извлечения истории чатов Cursor

Набор скриптов для извлечения истории чатов из Cursor IDE.

## Описание

Данная утилита позволяет извлечь историю чатов из Cursor IDE, которая хранится в SQLite базах данных в папке `%APPDATA%\Cursor\User\workspaceStorage`. Утилита предоставляет несколько методов извлечения, использующих разные подходы, что повышает шансы успешного извлечения данных в разных конфигурациях систем.

## Системные требования

- Windows 7/8/10/11
- PowerShell 5.0+
- Python 3.6+ (опционально)
- SQLite (опционально)

## Содержимое

В комплект входят следующие файлы:

1. `extract_all_cursor_chats.bat` - основной скрипт для запуска всех методов извлечения
2. `extract_cursor_chats.ps1` - PowerShell скрипт, загружающий SQLite и извлекающий данные
3. `extract_cursor_chats_dotnet.ps1` - PowerShell скрипт, использующий .NET для работы с SQLite
4. `extract_cursor_chats_simple.ps1` - простой PowerShell скрипт для копирования баз данных
5. `extract_cursor_chats_python.py` - Python скрипт для извлечения данных с помощью модуля sqlite3

## Как использовать

### Метод 1: Запуск всех скриптов сразу

1. Запустите файл `extract_all_cursor_chats.bat` от имени администратора
2. Дождитесь завершения всех скриптов
3. Проверьте созданные текстовые файлы с результатами

### Метод 2: Запуск отдельных скриптов

Вы можете запустить отдельные скрипты в зависимости от ваших предпочтений:

- `extract_cursor_chats.ps1` - основной метод, скачивает SQLite и извлекает данные
- `extract_cursor_chats_dotnet.ps1` - метод с использованием .NET библиотек
- `extract_cursor_chats_simple.ps1` - простой метод, только копирует базы данных
- `extract_cursor_chats_python.py` - метод с использованием Python

#### Для запуска PowerShell скриптов:

```powershell
powershell -ExecutionPolicy Bypass -File имя_скрипта.ps1
```

#### Для запуска Python скрипта:

```cmd
python extract_cursor_chats_python.py
```

## Результаты

После выполнения скриптов будут созданы следующие файлы:

- `cursor_chats_history.txt` - результат основного метода
- `cursor_chats_dotnet.txt` - результат метода .NET
- `cursor_chats_info.txt` - результат простого метода
- `cursor_chats_python.txt` - результат Python метода
- `cursor_chat_*.vscdb` - копии баз данных Cursor

## Ручной метод (если автоматические методы не работают)

Если автоматические методы не работают, вы можете извлечь данные вручную:

1. Установите SQLite Browser с сайта https://sqlitebrowser.org/
2. Откройте файлы `cursor_chat_*.vscdb` с помощью SQLite Browser
3. Перейдите на вкладку "Execute SQL"
4. Выполните запрос:
   ```sql
   SELECT rowid, [key], value FROM ItemTable WHERE [key] IN ('aiService.prompts', 'workbench.panel.aichat.view.aichat.chatdata')
   ```
5. В результатах найдите строки со столбцом 'key' равным 'workbench.panel.aichat.view.aichat.chatdata'
6. Значение в столбце 'value' - это JSON с историей чатов

## Настройка

По умолчанию скрипты ищут историю чатов в папке `C:/Users/Admin/AppData/Roaming/Cursor/User/workspaceStorage`. Если ваш путь отличается, отредактируйте следующие файлы:

- `extract_cursor_chats.ps1` - переменная `$workspaceStoragePath`
- `extract_cursor_chats_dotnet.ps1` - переменная `$workspaceStoragePath`
- `extract_cursor_chats_simple.ps1` - переменная `$workspaceStoragePath`
- `extract_cursor_chats_python.py` - переменная `workspace_storage_path`

## Примечания

- Скрипты создают временные копии баз данных для безопасной работы с ними
- Результаты сохраняются в текстовые файлы в кодировке UTF-8
- Если у вас нет прав администратора, возможно, потребуется запустить скрипты от имени администратора

## Безопасность

- Скрипты не отправляют данные в интернет
- Скрипты не изменяют оригинальные файлы Cursor
- Все операции производятся с копиями баз данных

## Автор

- AI-помощник
- Дата: 06.04.2025 