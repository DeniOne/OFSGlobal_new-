import os
import re
import sys
from colorama import init, Fore, Style

# Инициализация colorama для цветного вывода
init()

# Термины, которые мы ищем
DEPRECATED_TERMS = [
    "employee", "Employee", "employees", "Employees", "EMPLOYEE", "EMPLOYEES",
    "emploee", "Emploee", "emploees", "Emploees", 
    "department", "Department", "departments", "Departments", "DEPARTMENT", "DEPARTMENTS"
]

# Директории, которые нужно исключить из поиска
EXCLUDE_DIRS = [
    ".git", "__pycache__", "node_modules", "venv", "env",
    "backups_before_replacement", "backups_before_replacement_*"
]

# Файлы, которые нужно исключить из поиска
EXCLUDE_FILES = [
    "replace_deprecated_terms.py", 
    "replace_all_deprecated_terms.py",
    "search_deprecated_terms.py",
    "strategic_term_checker.py",
    "migration_notes.md",
    "migration_plan.md"
]

# Исключения для каждого типа файлов - ситуации, когда термины должны остаться
FILE_TYPE_EXCEPTIONS = {
    # API файлы - для обратной совместимости API
    'api.py': [
        r'employees_redirect', 
        r'departments_redirect'
    ],
    'telegram_bot.py': [
        r'department_value', r'division='
    ],
    'api_endpoints.md': [
        r'department', r'employee'
    ],
    # Телеграм бот - везде уже есть правильные названия
    'bot.py': [
        r'employee_data'
    ],
    'database.py': [
        r'employee', r'get_employee', r'delete_employee', r'update_employee', r'add_employee', r'create_employee'
    ],
    'api_client.py': [
        r'employee_data', r'send_employee'
    ],
    'registration_handlers.py': [
        r'employee', r'get_employee'
    ],
    'admin_handlers.py': [
        r'employee', r'department'
    ],
    'keyboards.py': [
        r'employee'
    ],
    # Документация - не требует обновления
    '.md': [
        r'employee', 
        r'department'
    ],
    # Тесты телеграм бота - не требуют обновления
    'test_': [
        r'employee', r'department'
    ],
    'conftest.py': [
        r'employee_data'
    ],
    # Фронтенд компоненты - определенные файлы должны остаться без изменений для совместимости
    'DepartmentList.tsx': [
        r'Department', r'department', r'Departments', r'departments'
    ],
    'EmployeeList.tsx': [
        r'Employee', r'employee', r'Employees', r'employees'
    ],
    'EmployeeForm.tsx': [
        r'Employee', r'employee'
    ],
    'FunctionalRelationsManager.tsx': [
        r'employee'
    ],
    'FunctionalRelationList.tsx': [
        r'department'
    ],
    'NodeEditModal.tsx': [
        r'department', r'employee'
    ],
    'OrganizationTree.tsx': [
        r'Employee', r'employee'
    ],
    'DepartmentsPage.tsx': [
        r'Department', r'Departments'
    ],
    # Роуты - для обратной совместимости
    'index.tsx': [
        r'Employee'
    ]
}

# Расширения файлов, которые нужно проверить
INCLUDE_EXTENSIONS = [
    ".py", ".tsx", ".ts", ".js", ".jsx", ".json", ".md", 
    ".yaml", ".yml", ".html", ".css", ".scss"
]

def should_check_file(filepath):
    """Проверяет, нужно ли проверять файл."""
    filename = os.path.basename(filepath)
    
    # Пропустить исключенные файлы
    if filename in EXCLUDE_FILES:
        return False
    
    # Проверять только файлы с определенными расширениями
    _, ext = os.path.splitext(filepath)
    if ext not in INCLUDE_EXTENSIONS:
        return False
    
    return True

def is_exception_case(filepath, line):
    """Проверяет, является ли строка исключением для данного файла."""
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filepath)[1]
    
    # Проверяем исключения для данного типа файла
    for file_pattern, patterns in FILE_TYPE_EXCEPTIONS.items():
        if file_pattern in filename or file_pattern == ext:
            for pattern in patterns:
                if re.search(pattern, line):
                    return True
    
    return False

def get_pattern():
    """Возвращает регулярное выражение для поиска устаревших терминов."""
    patterns = [r'\b' + term + r'\b' for term in DEPRECATED_TERMS]
    combined_pattern = '|'.join(patterns)
    return re.compile(combined_pattern, re.IGNORECASE)

def scan_file(filepath, pattern):
    """Сканирует файл на наличие устаревших терминов."""
    matches = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
            for i, line in enumerate(file, 1):
                # Пропускаем строки, которые являются исключениями для данного файла
                if is_exception_case(filepath, line):
                    continue
                
                # Ищем устаревшие термины
                if pattern.search(line):
                    highlighted_line = pattern.sub(
                        lambda m: f"{Fore.RED}{m.group(0)}{Style.RESET_ALL}", 
                        line.strip()
                    )
                    matches.append((i, highlighted_line))
    except Exception as e:
        print(f"Ошибка при сканировании файла {filepath}: {e}")
    
    return matches

def scan_directory(root_dir="."):
    """Сканирует директорию на наличие файлов с устаревшими терминами."""
    pattern = get_pattern()
    results = {}
    total_matches = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Фильтруем директории, которые нужно исключить
        dirnames[:] = [d for d in dirnames if not any(
            ex_dir in d if '*' not in ex_dir else False
            for ex_dir in EXCLUDE_DIRS
        )]
        
        # Дополнительно проверяем шаблоны с wildcards
        for ex_pattern in EXCLUDE_DIRS:
            if '*' in ex_pattern:
                base_pattern = ex_pattern.replace('*', '')
                dirnames[:] = [d for d in dirnames if not d.startswith(base_pattern)]
        
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            if should_check_file(filepath):
                matches = scan_file(filepath, pattern)
                if matches:
                    results[filepath] = matches
                    total_matches += len(matches)
    
    return results, total_matches

def print_results(results, total_matches):
    """Выводит результаты сканирования."""
    if not results:
        print(f"{Fore.GREEN}Устаревших терминов, требующих внимания, не найдено. Всё чисто!{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.YELLOW}========== РЕЗУЛЬТАТЫ СТРАТЕГИЧЕСКОГО СКАНИРОВАНИЯ =========={Style.RESET_ALL}")
    print(f"Найдено {total_matches} совпадений в {len(results)} файлах, требующих внимания\n")
    
    for filepath, matches in results.items():
        print(f"{Fore.CYAN}Файл: {filepath}{Style.RESET_ALL}")
        for line_num, line in matches:
            print(f"  Строка {line_num}: {line}")
        print()

def main():
    """Основная функция."""
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    print(f"Стратегическое сканирование проекта на устаревшие термины в директории: {directory}")
    print(f"Ищем следующие термины: {', '.join(DEPRECATED_TERMS)}")
    print(f"Исключаем директории: {', '.join(EXCLUDE_DIRS)}")
    print(f"Исключаем файлы: {', '.join(EXCLUDE_FILES)}")
    
    results, total_matches = scan_directory(directory)
    print_results(results, total_matches)
    
    if total_matches > 0:
        sys.exit(1)  # Ошибка, если найдены устаревшие термины
    else:
        sys.exit(0)  # Успех, если устаревшие термины не найдены

if __name__ == "__main__":
    main() 