import pandas as pd
import sys

def analyze_excel(filename):
    """Анализирует Excel-файл и выводит информацию о листах и их содержимом"""
    print(f"Анализ файла: {filename}")
    
    # Загружаем Excel-файл
    try:
        # Получаем имена всех листов в файле
        xlsx = pd.ExcelFile(filename)
        sheet_names = xlsx.sheet_names
        
        print(f"\nФайл содержит {len(sheet_names)} листов:")
        for i, sheet in enumerate(sheet_names, 1):
            print(f"{i}. {sheet}")
        
        # Анализируем каждый лист
        for sheet in sheet_names:
            print(f"\n=== Лист: {sheet} ===")
            
            # Загружаем данные листа
            df = pd.read_excel(filename, sheet_name=sheet)
            
            # Базовая информация о листе
            print(f"Размеры: {df.shape[0]} строк, {df.shape[1]} столбцов")
            print("Столбцы:")
            for col in df.columns:
                print(f"  - {col}")
            
            # Показываем первые несколько строк (если данные есть)
            if not df.empty:
                print("\nПервые 5 строк:")
                print(df.head(5).to_string())
            
            print('-' * 80)
            
    except Exception as e:
        print(f"Ошибка при анализе файла: {e}")
        return

if __name__ == "__main__":
    file_path = "ОФС стандартизированная полностью_v2.xlsx"
    analyze_excel(file_path) 