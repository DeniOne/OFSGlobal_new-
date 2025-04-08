#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для извлечения истории чатов из Cursor с использованием Python и sqlite3
Автор: AI-помощник
Дата: 06.04.2025
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
import glob
import shutil

# Путь к папке с историей чатов
workspace_storage_path = r"C:/Users/Admin/AppData/Roaming/Cursor/User/workspaceStorage"

# Путь к выходному файлу
output_file = "cursor_chats_python.txt"

def main():
    """Основная функция скрипта"""
    print("Запуск скрипта для извлечения истории чатов из Cursor...")
    
    # Проверяем, существует ли путь
    if not os.path.exists(workspace_storage_path):
        print(f"Путь {workspace_storage_path} не существует. Проверьте правильность пути.")
        return
    
    # Очищаем выходной файл, если он существует
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"=============================================\n")
        f.write(f"История чатов Cursor (Python метод)\n")
        f.write(f"Дата извлечения: {datetime.now()}\n")
        f.write(f"=============================================\n")
    
    # Получаем список всех папок в workspaceStorage
    folders = [f for f in os.listdir(workspace_storage_path) if os.path.isdir(os.path.join(workspace_storage_path, f))]
    print(f"Найдено {len(folders)} папок с рабочими пространствами")
    
    # Перебираем все папки
    for folder in folders:
        folder_path = os.path.join(workspace_storage_path, folder)
        db_path = os.path.join(folder_path, "state.vscdb")
        workspace_json_path = os.path.join(folder_path, "workspace.json")
        
        if os.path.exists(db_path):
            print(f"Обрабатываем базу данных: {db_path}")
            
            # Получаем информацию о рабочем пространстве
            workspace_info = "Нет информации о рабочем пространстве"
            if os.path.exists(workspace_json_path):
                try:
                    with open(workspace_json_path, 'r', encoding='utf-8') as f:
                        workspace_json = json.load(f)
                        workspace_info = workspace_json.get('folder', "Нет информации")
                except Exception as e:
                    workspace_info = f"Ошибка при чтении workspace.json: {str(e)}"
            
            # Копируем базу данных для безопасной работы с ней
            temp_db_path = f"temp_{folder}_state.vscdb"
            try:
                shutil.copy2(db_path, temp_db_path)
                print(f"Создана временная копия базы данных: {temp_db_path}")
            except Exception as e:
                print(f"Ошибка при копировании базы данных: {str(e)}")
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n\n========== Рабочее пространство: {folder} ==========\n")
                    f.write(f"Путь к рабочему пространству: {workspace_info}\n")
                    f.write(f"Путь к базе данных: {db_path}\n")
                    f.write(f"Размер базы данных: {os.path.getsize(db_path)} байт\n")
                    f.write(f"Дата изменения: {datetime.fromtimestamp(os.path.getmtime(db_path))}\n")
                    f.write(f"\nНе удалось создать копию базы данных: {str(e)}\n")
                continue
            
            # Записываем информацию о рабочем пространстве
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n\n========== Рабочее пространство: {folder} ==========\n")
                f.write(f"Путь к рабочему пространству: {workspace_info}\n")
                f.write(f"Путь к базе данных: {db_path}\n")
                f.write(f"Размер базы данных: {os.path.getsize(db_path)} байт\n")
                f.write(f"Дата изменения: {datetime.fromtimestamp(os.path.getmtime(db_path))}\n")
            
            # Работаем с базой данных SQLite
            try:
                # Подключаемся к базе данных
                conn = sqlite3.connect(temp_db_path)
                cursor = conn.cursor()
                
                # Запрос для получения истории чатов
                query = "SELECT rowid, key, value FROM ItemTable WHERE key IN ('aiService.prompts', 'workbench.panel.aichat.view.aichat.chatdata')"
                
                # Выполняем запрос
                print("Выполняем запрос к базе данных...")
                cursor.execute(query)
                results = cursor.fetchall()
                
                if results:
                    print(f"Получено {len(results)} строк результатов, обрабатываем...")
                    
                    # Для каждой строки результатов
                    for row in results:
                        rowid, key, value = row
                        
                        with open(output_file, 'a', encoding='utf-8') as f:
                            f.write(f"\n----- Ключ: {key} -----\n")
                        
                        if key == "workbench.panel.aichat.view.aichat.chatdata":
                            try:
                                # Пытаемся разобрать JSON
                                chat_json = json.loads(value)
                                
                                # Перебираем все чаты
                                for chat in chat_json.get('chats', []):
                                    with open(output_file, 'a', encoding='utf-8') as f:
                                        f.write(f"\n### Чат ID: {chat.get('id', 'Нет ID')}\n")
                                        f.write(f"Название: {chat.get('title', 'Без названия')}\n")
                                        f.write(f"Дата создания: {chat.get('createdAt', 'Неизвестно')}\n")
                                        f.write(f"Модель: {chat.get('model', 'Неизвестно')}\n")
                                        f.write(f"\n--- Сообщения ---\n")
                                    
                                    # Перебираем все сообщения в чате
                                    for message in chat.get('messages', []):
                                        role = message.get('role', 'unknown')
                                        content = message.get('content', 'Нет содержимого')
                                        
                                        with open(output_file, 'a', encoding='utf-8') as f:
                                            f.write(f"\n[{role}]: {content}\n")
                            except Exception as e:
                                with open(output_file, 'a', encoding='utf-8') as f:
                                    f.write(f"Ошибка при разборе данных чата: {str(e)}\n")
                                    # Запишем часть сырых данных (ограничим размер)
                                    max_length = min(1000, len(value))
                                    f.write(f"Начало сырых данных: {value[:max_length]}...\n")
                        
                        elif key == "aiService.prompts":
                            try:
                                # Пытаемся разобрать JSON
                                prompts_json = json.loads(value)
                                
                                with open(output_file, 'a', encoding='utf-8') as f:
                                    f.write(f"\n--- Промпты ---\n")
                                
                                # Перебираем все промпты
                                for prompt in prompts_json:
                                    with open(output_file, 'a', encoding='utf-8') as f:
                                        f.write(f"\n### Промпт ID: {prompt.get('id', 'Нет ID')}\n")
                                        f.write(f"Запрос: {prompt.get('query', 'Нет запроса')}\n")
                                        f.write(f"Дата: {prompt.get('date', 'Неизвестно')}\n")
                                        f.write(f"Модель: {prompt.get('model', 'Неизвестно')}\n")
                                        f.write(f"Ответ: {prompt.get('response', 'Нет ответа')}\n")
                            except Exception as e:
                                with open(output_file, 'a', encoding='utf-8') as f:
                                    f.write(f"Ошибка при разборе данных промптов: {str(e)}\n")
                                    # Запишем часть сырых данных (ограничим размер)
                                    max_length = min(1000, len(value))
                                    f.write(f"Начало сырых данных: {value[:max_length]}...\n")
                        
                        else:
                            with open(output_file, 'a', encoding='utf-8') as f:
                                f.write(f"Непонятный формат данных\n")
                                # Запишем часть сырых данных (ограничим размер)
                                max_length = min(1000, len(value))
                                f.write(f"Начало сырых данных: {value[:max_length]}...\n")
                
                else:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(f"\nНе удалось получить данные из базы данных или данные отсутствуют.\n")
                
                # Закрываем соединение с базой данных
                cursor.close()
                conn.close()
            
            except Exception as e:
                print(f"Ошибка при работе с базой данных: {str(e)}")
                with open(output_file, 'a', encoding='utf-8') as f:
                    f.write(f"\nОшибка при работе с базой данных: {str(e)}\n")
            
            # Удаляем временный файл базы данных
            try:
                os.remove(temp_db_path)
                print(f"Временная копия базы данных удалена")
            except Exception as e:
                print(f"Ошибка при удалении временной копии базы данных: {str(e)}")

    print(f"Готово! История чатов извлечена и сохранена в файл {os.path.abspath(output_file)}")

# Создаем bat-файл для запуска Python-скрипта
def create_bat_file():
    """Создает bat-файл для запуска Python-скрипта"""
    bat_content = f"""@echo off
echo Запуск скрипта извлечения истории чатов из Cursor...
python "{os.path.abspath(__file__)}"
echo.
echo Готово! Нажмите любую клавишу для выхода...
pause >nul
"""
    
    with open("extract_cursor_chats_python.bat", 'w') as f:
        f.write(bat_content)
    
    print(f"Создан bat-файл для запуска: {os.path.abspath('extract_cursor_chats_python.bat')}")

if __name__ == "__main__":
    main()
    create_bat_file() 