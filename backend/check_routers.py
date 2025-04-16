import os
import re

def check_router_names():
    """Проверяет все файлы в app/api/endpoints/*.py и выводит имена всех роутеров"""
    endpoints_dir = os.path.join("app", "api", "endpoints")
    
    if not os.path.exists(endpoints_dir):
        print(f"Директория {endpoints_dir} не найдена")
        return
    
    router_pattern = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*APIRouter\(')
    
    for filename in os.listdir(endpoints_dir):
        if not filename.endswith('.py'):
            continue
        
        module_name = filename[:-3]
        file_path = os.path.join(endpoints_dir, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                content = f.read()
                matches = router_pattern.findall(content)
                if matches:
                    print(f"{module_name}.py: {', '.join(matches)}")
                else:
                    print(f"{module_name}.py: ROUTER NOT FOUND")
            except Exception as e:
                print(f"Ошибка при чтении {file_path}: {e}")

if __name__ == "__main__":
    check_router_names() 