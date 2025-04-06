@echo off
echo [+] Запуск серверов разработки OFS Global...

:: Запуск бэкенда
start cmd /k "cd D:\OFS_Global\ofs_project\ofs_new\backend && run_backend.bat"

:: Запуск фронтенда
start cmd /k "cd D:\OFS_Global\ofs_project\ofs_new\frontend && npm run dev"

echo [+] Сервера запущены!
echo [+] Бэкенд: http://localhost:8000
echo [+] Фронтенд: http://localhost:3000
echo [+] Страница должностей: http://localhost:3000/positions 