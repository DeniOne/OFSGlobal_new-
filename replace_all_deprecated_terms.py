#!/usr/bin/env python3
import os
import re
import sys
import shutil
import argparse
from typing import Dict, List, Set, Tuple
import time
import json
from colorama import Fore, Style, init

# Инициализация colorama для Windows
init()

# Словарь замен: ключ - шаблон регулярного выражения, значение - замена
REPLACEMENTS = {
    # Staff -> Staff
    r'\bemployee\b': 'staff',
    r'\bEmployee\b': 'Staff',
    r'\bEMPLOYEE\b': 'STAFF',
    r'\bemployees\b': 'staff',
    r'\bEmployees\b': 'Staff',
    r'\bEMPLOYEES\b': 'STAFF',
    r'\bemployees_\b': 'staff_',
    r'\bemployee_\b': 'staff_',
    r'\bemployee-\b': 'staff-',
    r'\bemployee/\b': 'staff/',
    r'/staff/': '/staff/',
    r'/staff\b': '/staff',
    r'"staff"': '"staff"',
    r"'staff'": "'staff'",
    r'\.staff': '.staff',
    r'_staff': '_staff',
    r'\bemploee\b': 'staff',
    r'\bEmploee\b': 'Staff',
    r'\bemploees\b': 'staff',
    r'\bEmploees\b': 'Staff',
    
    # Division -> Division
    r'\bdepartment\b': 'division',
    r'\bDepartment\b': 'Division',
    r'\bDEPARTMENT\b': 'DIVISION',
    r'\bdepartments\b': 'divisions',
    r'\bDepartments\b': 'Divisions',
    r'\bDEPARTMENTS\b': 'DIVISIONS',
    r'\bdepartments_\b': 'divisions_',
    r'\bdepartment_\b': 'division_',
    r'\bdepartment-\b': 'division-',
    r'\bdepartment/\b': 'division/',
    r'/divisions/': '/divisions/',
    r'/divisions\b': '/divisions',
    r'"divisions"': '"divisions"',
    r"'divisions'": "'divisions'",
    r'\.divisions': '.divisions',
    r'_divisions': '_divisions',
}

# Директории, которые нужно исключить
EXCLUDE_DIRS = [
    '.git',
    '.idea',
    '.vscode',
    'node_modules',
    '__pycache__',
    'venv',
    '.venv',
    'env',
    'dist',
    'build',
]

# Шаблоны директорий для исключения при резервном копировании
BACKUP_EXCLUDE_PATTERNS = [
    'backups_before_replacement*',
]

# Расширения файлов, которые нужно обрабатывать
INCLUDE_EXTENSIONS = [
    '.py', '.ts', '.tsx', '.js', '.jsx', '.html', '.css', '.scss', 
    '.md', '.sql', '.json', '.yaml', '.yml', '.txt'
]

def should_check_file(file_path, exclude_paths):
    """Проверяет, нужно ли сканировать файл"""
    # Проверяем пути исключения
    for exclude_path in exclude_paths:
        if exclude_path in file_path:
            return False
    
    # Исключаем директории бэкапов
    for pattern in BACKUP_EXCLUDE_PATTERNS:
        pattern_base = pattern.rstrip('*')
        if pattern_base in file_path:
            return False
    
    # Проверяем имя файла
    file_name = os.path.basename(file_path)
    if file_name.startswith('.'):
        return False
    
    # Проверка расширения
    _, ext = os.path.splitext(file_name)
    return ext.lower() in INCLUDE_EXTENSIONS

def make_backup(directory, backup_dir=None):
    """Создает резервную копию директории, если backup_dir не указан"""
    if not backup_dir:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backups_before_replacement_{timestamp}"
    
    if not os.path.exists(backup_dir):
        print(f"{Fore.YELLOW}Создание резервной копии в {backup_dir}...{Style.RESET_ALL}")
        
        # Создаем функцию для фильтрации директорий и файлов
        def ignore_func(src, names):
            ignored = set()
            for name in names:
                path = os.path.join(src, name)
                # Исключаем папки с бэкапами и другие нежелательные файлы
                if os.path.isdir(path):
                    for pattern in BACKUP_EXCLUDE_PATTERNS:
                        if name.startswith(pattern.rstrip('*')) or (pattern.endswith('*') and name.startswith(pattern[:-1])):
                            ignored.add(name)
                            break
                
                # Исключаем временные файлы и другие ненужные типы
                if name.endswith(('.exe', '.dll', '.so', '.pyc')) or name in ('node_modules', '__pycache__', '.git'):
                    ignored.add(name)
            
            return ignored
        
        try:
            shutil.copytree(directory, backup_dir, ignore=ignore_func)
            
            # Создаем информационный файл
            with open(os.path.join(backup_dir, "info.txt"), "w", encoding="utf-8") as f:
                f.write(f"Backup created at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Original directory: {os.path.abspath(directory)}\n")
                f.write(f"Replacements to be applied:\n")
                for pattern, replacement in REPLACEMENTS.items():
                    f.write(f"  {pattern} -> {replacement}\n")
                    
            print(f"{Fore.GREEN}Резервная копия создана в {backup_dir}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Ошибка при создании бэкапа: {e}{Style.RESET_ALL}")
            return None
    else:
        print(f"{Fore.YELLOW}Резервная копия {backup_dir} уже существует, использую её{Style.RESET_ALL}")
    
    return backup_dir

def compile_patterns():
    """Компилирует шаблоны регулярных выражений для более быстрого поиска"""
    compiled_patterns = {}
    for pattern, replacement in REPLACEMENTS.items():
        compiled_patterns[re.compile(pattern)] = replacement
    return compiled_patterns

def replace_in_file(file_path, patterns, dry_run=False, backup_dir=None):
    """Заменяет устаревшие термины в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = 0
        matches = []
        
        # Находим все совпадения для отчета
        for pattern, replacement in patterns.items():
            for match in pattern.finditer(content):
                matches.append((match.group(), replacement, match.start(), match.end()))
        
        # Если нет изменений, просто возвращаем 0
        if not matches:
            return 0, []
        
        # Если это тестовый запуск, возвращаем количество найденных совпадений
        if dry_run:
            return len(matches), matches
        
        # Создаем бэкап файла, если указана директория бэкапа
        if backup_dir:
            rel_path = os.path.relpath(file_path)
            backup_file_path = os.path.join(backup_dir, rel_path)
            
            # Убедимся, что директория для бэкапа существует
            os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
            
            # Копируем файл в директорию бэкапа
            shutil.copy2(file_path, backup_file_path)
        
        # Выполняем замены
        for pattern, replacement in patterns.items():
            new_content, count = pattern.subn(replacement, content)
            if count > 0:
                changes_made += count
                content = new_content
        
        # Если контент изменился, записываем его обратно в файл
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return changes_made, matches
    except UnicodeDecodeError:
        # Пропускаем бинарные файлы
        return 0, []
    except Exception as e:
        print(f"{Fore.RED}Ошибка при обработке {file_path}: {e}{Style.RESET_ALL}")
        return 0, []

def process_directory(directory, patterns, dry_run=False, backup_dir=None, extra_excluded_dirs=None):
    """Обрабатывает директорию, заменяя устаревшие термины во всех файлах"""
    total_replacements = 0
    modified_files = 0
    processed_files = 0
    all_matches = {}
    
    excluded_paths = set(EXCLUDE_DIRS)
    if extra_excluded_dirs:
        excluded_paths.update(extra_excluded_dirs)
    
    for root, dirs, files in os.walk(directory):
        # Исключаем директории
        dirs_to_remove = []
        for d in dirs:
            full_path = os.path.join(root, d)
            if d in excluded_paths:
                dirs_to_remove.append(d)
                continue
                
            # Исключаем директории бэкапов
            for pattern in BACKUP_EXCLUDE_PATTERNS:
                pattern_base = pattern.rstrip('*')
                if d.startswith(pattern_base) or pattern_base in full_path:
                    dirs_to_remove.append(d)
                    break
        
        for d in dirs_to_remove:
            if d in dirs:
                dirs.remove(d)
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory)
            
            if should_check_file(file_path, excluded_paths):
                processed_files += 1
                
                replacements, matches = replace_in_file(file_path, patterns, dry_run, backup_dir)
                
                if replacements > 0:
                    total_replacements += replacements
                    modified_files += 1
                    
                    if dry_run and matches:
                        all_matches[rel_path] = matches
                    
                    if not dry_run and (modified_files % 10 == 0):
                        print(f"{Fore.GREEN}Обработано {processed_files} файлов, изменено {modified_files}{Style.RESET_ALL}")
    
    return total_replacements, modified_files, processed_files, all_matches

def main():
    parser = argparse.ArgumentParser(description='Заменяет устаревшие термины в проекте.')
    parser.add_argument('--dir', '-d', default='.', help='Директория для сканирования')
    parser.add_argument('--backup-dir', '-b', help='Директория для бэкапа (создаст автоматически, если не указана)')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Тестовый запуск без внесения изменений')
    parser.add_argument('--exclude', '-e', nargs='+', help='Дополнительные директории для исключения')
    args = parser.parse_args()
    
    directory = args.dir
    dry_run = args.dry_run
    
    start_time = time.time()
    
    # Компилируем регулярные выражения
    patterns = compile_patterns()
    
    if dry_run:
        print(f"{Fore.YELLOW}ТЕСТОВЫЙ ЗАПУСК: Изменения НЕ будут применены{Style.RESET_ALL}")
        print(f"Анализ устаревших терминов в {directory}...")
        backup_dir = None
    else:
        print(f"{Fore.RED}ВНИМАНИЕ: Автоматическая замена терминов!{Style.RESET_ALL}")
        print(f"{Fore.RED}Это изменит файлы в проекте. Убедитесь, что у вас есть резервная копия, или используйте --dry-run для предварительного тестирования.{Style.RESET_ALL}")
        backup_dir = args.backup_dir
        backup_dir = make_backup(directory, backup_dir)
        
        confirmation = input(f"{Fore.YELLOW}Продолжить замену? (y/n): {Style.RESET_ALL}")
        if confirmation.lower() != 'y':
            print("Операция отменена.")
            return
    
    total_replacements, modified_files, processed_files, all_matches = process_directory(
        directory, patterns, dry_run, backup_dir, args.exclude
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{Fore.CYAN}========== РЕЗУЛЬТАТЫ =========={Style.RESET_ALL}")
    
    if dry_run:
        print(f"{Fore.YELLOW}Тестовый запуск завершен. Найдено {total_replacements} замен в {modified_files} файлах.{Style.RESET_ALL}")
        
        if all_matches:
            print(f"\n{Fore.CYAN}Примеры замен:{Style.RESET_ALL}")
            count = 0
            for file_path, matches in sorted(all_matches.items()):
                print(f"{Fore.GREEN}{file_path}{Style.RESET_ALL}: {len(matches)} замен")
                for match, replacement, _, _ in matches[:5]:  # Показываем только первые 5 замен для каждого файла
                    print(f"  {Fore.RED}{match}{Style.RESET_ALL} -> {Fore.GREEN}{replacement}{Style.RESET_ALL}")
                
                count += 1
                if count >= 10:  # Показываем только первые 10 файлов
                    print(f"... и еще {len(all_matches) - 10} файлов")
                    break
            
        print(f"\n{Fore.YELLOW}Для применения изменений запустите без флага --dry-run{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}Операция завершена!{Style.RESET_ALL}")
        print(f"Обработано {processed_files} файлов")
        print(f"Изменено {modified_files} файлов")
        print(f"Выполнено {total_replacements} замен")
        print(f"Резервная копия сохранена в: {backup_dir}")
    
    print(f"Время выполнения: {duration:.2f} секунд")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 