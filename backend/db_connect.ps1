# Скрипт для подключения к PostgreSQL с автоматическим вводом пароля

# Выполняем команду, переданную как параметр
param(
    [Parameter(Mandatory=$true)]
    [string]$Command
)

# Устанавливаем пароль
$env:PGPASSWORD = "QAZwsxr`$t5"

# Выполнение команды psql
& psql -h localhost -U postgres -d ofs_db -c "$Command"

# Очищаем переменную окружения после использования
$env:PGPASSWORD = "" 