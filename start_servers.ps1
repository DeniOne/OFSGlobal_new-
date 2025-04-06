# Скрипт для одновременного запуска фронтенд и бэкенд серверов
Write-Host "Запускаем сервера OFS Global..." -ForegroundColor Cyan

# Запуск бэкенда в отдельном окне
Write-Host "Запускаем backend на порту 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --reload --port 8000"

# Ждем 3 секунды, чтобы бэкенд успел запуститься
Start-Sleep -Seconds 3

# Запуск фронтенда в отдельном окне
Write-Host "Запускаем frontend на порту 3006..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "Оба сервера запущены! Открой http://localhost:3006 в браузере" -ForegroundColor Magenta 