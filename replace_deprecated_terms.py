#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import argparse
from pathlib import Path
import shutil
import tempfile
import time
from tqdm import tqdm
import colorama
from colorama import Fore, Style

colorama.init()

# Словарь для замены терминов: старый термин -> новый термин
REPLACEMENTS = {
    # Точное совпадение слова целиком
    r'\bemployee\b': 'staff',
    r'\bEmployee\b': 'Staff',
    r'\bEMPLOYEE\b': 'STAFF',
    r'\bemployees\b': 'staff',
    r'\bEmployees\b': 'Staff',
    r'\bEMPLOYEES\b': 'STAFF',
    r'\bemployees_\b': 'staff_',
    r'\bemployee_\b': 'staff_',
    # URL пути
    r'/staff/': '/staff/',
    r'/staff\b': '/staff',
    r'"staff"': '"staff"',
    r"'staff'": "'staff'",
    # Точное совпадение для отделов
    r'\bdepartment\b': 'division',
    r'\bDepartment\b': 'Division',
    r'\bDEPARTMENT\b': 'DIVISION',
    r'\bdepartments\b': 'divisions',
    r'\bDepartments\b': 'Divisions',
    r'\bDEPARTMENTS\b': 'DIVISIONS',
    r'\bdepartments_\b': 'divisions_',
    r'\bdepartment_\b': 'division_',
    # URL пути
    r'/divisions/': '/divisions/',
    r'/divisions\b': '/divisions',
    r'"divisions"': '"divisions"',
    r"'divisions'": "'divisions'",
    # Опечатки
    r'\bemploye\b': 'staff',
    r'\bEmploye\b': 'Staff',
    r'\bemployes\b': 'staff',
    r'\bEmployes\b': 'Staff',
    r'\bemploee\b': 'staff',
    r'\bEmploee\b': 'Staff',
    r'\bemploees\b': 'staff',
    r'\bEmploees\b': 'Staff',
}

# Файлы, которые нужно исключить
EXCLUDE_DIRS = [
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "venv",
    "build",
    "dist",
    ".idea",
    ".vs",
    "logs",
    "tmp",
    ".pytest_cache",
    "search_deprecated_terms.py",  # Исключаем сам скрипт поиска
    "replace_deprecated_terms.py",  # Исключаем сам скрипт замены
    "backups"  # Исключаем директорию с бэкапами
]

# Форматы файлов для проверки
INCLUDE_EXTENSIONS = [
    ".py", ".tsx", ".ts", ".js", ".jsx", ".json", ".md", ".html", ".css",
    ".yml", ".yaml", ".sql", ".sh", ".bat", ".csv", ".txt"
]

BACKUP_DIR = "backups_before_replacement"

def should_check_file(file_path):
    """Проверяет, нужно ли сканировать данный файл"""
    # Проверка на исключаемые директории
    parts = Path(file_path).parts
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir in parts:
            return False
    
    # Проверка расширения файла
    ext = Path(file_path).suffix.lower()
    if ext not in INCLUDE_EXTENSIONS:
        return False
    
    # Проверка на бинарный файл
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except UnicodeDecodeError:
        return False

def make_backup(file_path):
    """Создает резервную копию файла перед заменой"""
    backup_path = Path(BACKUP_DIR) / Path(file_path).relative_to('.')
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(file_path, backup_path)
    return backup_path

def replace_terms_in_file(file_path, dry_run=False):
    """Заменяет устаревшие термины в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        replacement_count = 0
        
        # Выполняем замены
        for pattern, replacement in REPLACEMENTS.items():
            # Подсчитываем количество замен для этого паттерна
            matches = re.findall(pattern, content)
            replacement_count += len(matches)
            # Выполняем замену
            content = re.sub(pattern, replacement, content)
        
        # Если есть замены и это не пробный запуск, сохраняем файл
        if replacement_count > 0:
            if not dry_run:
                make_backup(file_path)  # Создаем резервную копию
                
                # Используем временный файл для безопасной записи
                fd, temp_path = tempfile.mkstemp()
                try:
                    with os.fdopen(fd, 'w', encoding='utf-8') as temp_file:
                        temp_file.write(content)
                    # Заменяем оригинальный файл временным файлом
                    shutil.move(temp_path, file_path)
                except Exception as e:
                    print(f"Ошибка при записи файла {file_path}: {e}")
                    os.unlink(temp_path)  # Удаляем временный файл при ошибке
            
            return replacement_count
        
        return 0
    except Exception as e:
        print(f"Ошибка при обработке файла {file_path}: {e}")
        return 0

def scan_directory(directory=".", dry_run=False):
    """Сканирует директорию и заменяет термины во всех подходящих файлах"""
    total_replacements = 0
    processed_files = 0
    files_with_replacements = 0
    
    # Создаем директорию для резервных копий
    if not dry_run:
        Path(BACKUP_DIR).mkdir(exist_ok=True)
        # Сохраняем информацию о времени запуска
        with open(f"{BACKUP_DIR}/info.txt", 'w', encoding='utf-8') as f:
            f.write(f"Замена выполнена: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Заменяемые термины:\n")
            for pattern, replacement in REPLACEMENTS.items():
                f.write(f"  {pattern} -> {replacement}\n")
    
    # Получаем список всех файлов для обработки
    all_files = []
    for root, dirs, files in os.walk(directory):
        # Пропускаем исключаемые директории
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            file_path = os.path.join(root, file)
            if should_check_file(file_path):
                all_files.append(file_path)
    
    # Показываем прогресс-бар
    print(f"{'Анализ' if dry_run else 'Замена'} устаревших терминов в директории: {directory}")
    for term_from, term_to in REPLACEMENTS.items():
        print(f"  {term_from} -> {term_to}")
    
    with tqdm(total=len(all_files), desc="Обработка файлов") as pbar:
        for file_path in all_files:
            replacements = replace_terms_in_file(file_path, dry_run)
            processed_files += 1
            
            if replacements > 0:
                files_with_replacements += 1
                total_replacements += replacements
                
                # Если это пробный запуск, выводим информацию о файле
                if dry_run:
                    rel_path = os.path.relpath(file_path, directory)
                    pbar.write(f"{Fore.YELLOW}Найдено {replacements} замен в {rel_path}{Style.RESET_ALL}")
            
            pbar.update(1)
    
    return {
        "total_replacements": total_replacements,
        "processed_files": processed_files,
        "files_with_replacements": files_with_replacements
    }

def main():
    parser = argparse.ArgumentParser(description="Заменяет устаревшие термины в проекте")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Только анализ, без внесения изменений")
    parser.add_argument("--dir", "-p", default=".", help="Директория для сканирования")
    args = parser.parse_args()

    print(f"{Fore.CYAN}=" * 60)
    print("АВТОМАТИЧЕСКАЯ ЗАМЕНА УСТАРЕВШИХ ТЕРМИНОВ")
    print("=" * 60 + Style.RESET_ALL)
    
    if args.dry_run:
        print(f"{Fore.YELLOW}Режим тестирования (изменения не будут применены){Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}ВНИМАНИЕ: Этот скрипт изменит файлы в проекте!{Style.RESET_ALL}")
        print(f"Резервные копии будут сохранены в директорию: {BACKUP_DIR}")
        confirm = input("Продолжить? (y/N): ")
        if confirm.lower() != 'y':
            print("Отмена операции.")
            return
    
    start_time = time.time()
    results = scan_directory(args.dir, args.dry_run)
    end_time = time.time()
    
    print(f"\n{Fore.GREEN}=" * 60)
    print("РЕЗУЛЬТАТЫ ОПЕРАЦИИ:")
    print(f"Обработано файлов: {results['processed_files']}")
    print(f"Файлов с заменами: {results['files_with_replacements']}")
    print(f"Всего замен: {results['total_replacements']}")
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")
    
    if args.dry_run:
        print(f"\n{Fore.YELLOW}Это был тестовый запуск. Чтобы применить изменения, запустите без --dry-run{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.GREEN}Изменения успешно применены. Резервные копии сохранены в {BACKUP_DIR}{Style.RESET_ALL}")
    
    print("=" * 60 + Style.RESET_ALL)

if __name__ == "__main__":
    main() 