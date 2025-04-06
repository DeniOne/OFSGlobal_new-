#!/usr/bin/env python3
import os
import re
import sys
import argparse
from colorama import Fore, Style, init

# Инициализация colorama для Windows
init()

# Термины, которые нужно искать
DEPRECATED_TERMS = [
    "department", "Department", "departments", "Departments", "DEPARTMENT", "DEPARTMENTS",
    "employee", "Employee", "employees", "Employees", "EMPLOYEE", "EMPLOYEES",
    "emploee", "Emploee", "emploees", "Emploees",  # возможные опечатки
]

# Шаблоны для исключения записей о заменах в файлах скриптов
REPLACEMENT_PATTERNS = [
    r'\b\w+\s*:\s*[\'"]staff[\'"]',  # например 'employee': 'staff'
    r'\b\w+\s*:\s*[\'"]Staff[\'"]',  # например 'Employee': 'Staff'
    r'\b\w+\s*:\s*[\'"]division[\'"]', # например 'department': 'division'
    r'\b\w+\s*:\s*[\'"]Division[\'"]', # например 'Department': 'Division'
    r'r[\'"]\S+[\'"]:\s*[\'"]staff[\'"]',  # регулярные выражения замены
    r'r[\'"]\S+[\'"]:\s*[\'"]division[\'"]', # регулярные выражения замены
    r'r[\'"]\S+staff\S*[\'"]', # регулярные выражения содержащие staff
    r'r[\'"]\S+division\S*[\'"]', # регулярные выражения содержащие division
]

# Файлы и директории для исключения
EXCLUDED_DIRS = [
    ".git", "node_modules", "__pycache__", ".vscode", ".idea", 
    "venv", ".venv", "env", "dist", "build"
]
EXCLUDED_FILES = [
    "search_deprecated_terms.py",  # Исключаем сам скрипт
    "package-lock.json", "yarn.lock"
]

# Расширения файлов для проверки
INCLUDED_EXTENSIONS = [
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".html", ".css", 
    ".scss", ".md", ".sql", ".sh", ".bat", ".ps1", ".txt"
]

# Регулярное выражение для поиска терминов
def get_pattern():
    terms = "|".join(DEPRECATED_TERMS)
    return re.compile(f"({terms})")

def should_check_file(filepath):
    """Проверяет, нужно ли сканировать файл"""
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    
    # Проверка исключенных файлов
    if filename in EXCLUDED_FILES:
        return False
    
    # Проверка расширений
    if ext not in INCLUDED_EXTENSIONS:
        return False
    
    return True

def should_check_dir(dirpath, extra_excluded_dirs=None):
    """Проверяет, нужно ли сканировать директорию"""
    dirname = os.path.basename(dirpath)
    
    # Объединяем стандартные исключения и дополнительные
    excluded = EXCLUDED_DIRS.copy()
    if extra_excluded_dirs:
        excluded.extend(extra_excluded_dirs)
    
    # Проверяем, есть ли имя директории в исключенных
    if dirname in excluded:
        return False
    
    # Проверяем, является ли директория подпапкой любой из исключенных
    for excluded_dir in excluded:
        if excluded_dir in dirpath.split(os.sep):
            return False
    
    return True

def scan_file(filepath, pattern):
    """Сканирует файл на наличие устаревших терминов"""
    results = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Компилируем шаблоны исключений
        exclude_patterns = [re.compile(p) for p in REPLACEMENT_PATTERNS]
        
        for i, line in enumerate(lines, 1):
            # Проверяем, не содержит ли строка шаблон замены
            should_skip = False
            for exclude_pattern in exclude_patterns:
                if exclude_pattern.search(line):
                    should_skip = True
                    break
            
            if should_skip:
                continue
            
            # Ищем устаревшие термины
            matches = pattern.findall(line)
            if matches:
                # Подсветка найденных терминов
                highlighted_line = line
                for term in set(matches):
                    highlighted_line = highlighted_line.replace(
                        term, f"{Fore.RED}{term}{Style.RESET_ALL}"
                    )
                
                results.append({
                    'line_number': i,
                    'content': line.strip(),
                    'highlighted': highlighted_line.strip(),
                    'matches': matches
                })
    except UnicodeDecodeError:
        # Пропускаем бинарные файлы
        pass
    except Exception as e:
        print(f"Ошибка при обработке {filepath}: {e}")
    
    return results

def scan_directory(root_dir, extra_excluded_dirs=None):
    """Рекурсивно сканирует директорию"""
    pattern = get_pattern()
    all_results = {}
    total_matches = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Фильтрация директорий
        dirs[:] = [d for d in dirs if should_check_dir(os.path.join(root, d), extra_excluded_dirs)]
        
        for file in files:
            filepath = os.path.join(root, file)
            if should_check_file(filepath):
                results = scan_file(filepath, pattern)
                if results:
                    rel_path = os.path.relpath(filepath, root_dir)
                    all_results[rel_path] = results
                    total_matches += sum(len(r['matches']) for r in results)
    
    return all_results, total_matches

def print_results(results, total_matches):
    """Выводит результаты сканирования"""
    print(f"\n{Fore.CYAN}========== РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ =========={Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Найдено {total_matches} совпадений в {len(results)} файлах{Style.RESET_ALL}\n")
    
    for filepath, file_results in sorted(results.items()):
        print(f"{Fore.GREEN}Файл: {filepath}{Style.RESET_ALL}")
        
        for result in file_results:
            print(f"  Строка {result['line_number']}: {result['highlighted']}")
        
        print()  # Пустая строка между файлами

def main():
    parser = argparse.ArgumentParser(description='Поиск устаревших терминов в проекте.')
    parser.add_argument('--dir', '-d', default='.', help='Директория для сканирования')
    parser.add_argument('--exclude', '-e', nargs='+', help='Дополнительные директории для исключения')
    args = parser.parse_args()
    
    root_dir = args.dir
    extra_excluded_dirs = args.exclude or []
    
    print(f"Сканирование проекта на устаревшие термины в директории: {root_dir}")
    print("Ищем следующие термины:", ", ".join(DEPRECATED_TERMS))
    
    if extra_excluded_dirs:
        print(f"Дополнительно исключены директории: {', '.join(extra_excluded_dirs)}")
    
    results, total_matches = scan_directory(root_dir, extra_excluded_dirs)
    
    if total_matches > 0:
        print_results(results, total_matches)
        print(f"{Fore.RED}Найдено {total_matches} устаревших термина(ов). Нужно поправить!{Style.RESET_ALL}")
        return 1
    else:
        print(f"{Fore.GREEN}Устаревших терминов не найдено. Всё чисто!{Style.RESET_ALL}")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 