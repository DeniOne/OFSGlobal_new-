# Скрипт для одновременного запуска серверов разработки OFS Global

Write-Host "🚀 Запуск серверов разработки OFS Global..." -ForegroundColor Cyan

# Пути к директориям проекта
$projectRoot = "D:\OFS_Global\ofs_project\ofs_new"
$backendPath = "$projectRoot\backend"
$frontendPath = "$projectRoot\frontend"

# Остановить предыдущие процессы (опционально)
Write-Host "🔄 Останавливаем предыдущие процессы Python и Node..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Запуск бэкенда
Write-Host "🔹 Запускаем бэкенд сервер..." -ForegroundColor Green
if (Test-Path "$backendPath\run_backend.bat") {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$backendPath'; .\run_backend.bat" -WindowStyle Normal
    Write-Host "  ✅ Бэкенд запущен. Backend API будет доступен по адресу: http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "  ❌ Ошибка: Не найден скрипт запуска бэкенда в $backendPath" -ForegroundColor Red
}

# Запуск фронтенда
Write-Host "🔹 Запускаем фронтенд сервер..." -ForegroundColor Green
if (Test-Path $frontendPath) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$frontendPath'; npm run dev" -WindowStyle Normal
    Write-Host "  ✅ Фронтенд запущен. Сайт будет доступен по адресу: http://localhost:3000 (или другому порту, если 3000 занят)" -ForegroundColor Green
} else {
    Write-Host "  ❌ Ошибка: Не найдена директория фронтенда $frontendPath" -ForegroundColor Red
}

Write-Host "`n🎉 Готово! Оба сервера запущены в отдельных окнах. Для завершения работы закройте окна или используйте Ctrl+C в каждом окне." -ForegroundColor Cyan
Write-Host "📊 Страница должностей доступна по адресу: http://localhost:3000/positions" -ForegroundColor Magenta 