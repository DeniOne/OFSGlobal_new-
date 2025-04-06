import pytest
import json
from pathlib import Path

from ..database import Database

def test_add_employee(test_database, sample_employee_data):
    """Тест добавления сотрудника"""
    # Добавляем сотрудника
    employee_id = test_database.add_employee(sample_employee_data)
    
    # Проверяем, что ID создан
    assert employee_id is not None
    
    # Проверяем, что файл создан
    employee_file = Path(test_database.storage_path) / f"{employee_id}.json"
    assert employee_file.exists()
    
    # Проверяем содержимое файла
    with open(employee_file, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
        assert saved_data == sample_employee_data

def test_get_employee(test_database, sample_employee_data):
    """Тест получения данных сотрудника"""
    # Добавляем сотрудника
    employee_id = test_database.add_employee(sample_employee_data)
    
    # Получаем данные
    staff = test_database.get_employee(employee_id)
    
    # Проверяем данные
    assert staff == sample_employee_data

def test_update_employee(test_database, sample_employee_data):
    """Тест обновления данных сотрудника"""
    # Добавляем сотрудника
    employee_id = test_database.add_employee(sample_employee_data)
    
    # Обновляем данные
    updated_data = sample_employee_data.copy()
    updated_data["position"] = "Старший разработчик"
    
    test_database.update_employee(employee_id, updated_data)
    
    # Проверяем обновленные данные
    staff = test_database.get_employee(employee_id)
    assert staff == updated_data

def test_delete_employee(test_database, sample_employee_data):
    """Тест удаления сотрудника"""
    # Добавляем сотрудника
    employee_id = test_database.add_employee(sample_employee_data)
    
    # Удаляем сотрудника
    test_database.delete_employee(employee_id)
    
    # Проверяем, что файл удален
    employee_file = Path(test_database.storage_path) / f"{employee_id}.json"
    assert not employee_file.exists()

def test_get_all_staff(test_database, sample_employee_data):
    """Тест получения списка всех сотрудников"""
    # Добавляем несколько сотрудников
    employee_ids = []
    for i in range(3):
        data = sample_employee_data.copy()
        data["name"] = f"Сотрудник {i}"
        employee_ids.append(test_database.add_employee(data))
    
    # Получаем список всех сотрудников
    staff = test_database.get_all_staff()
    
    # Проверяем количество и данные
    assert len(staff) == 3
    assert all(emp["name"].startswith("Сотрудник") for emp in staff)

def test_get_staff_by_competency(test_database, sample_employee_data):
    """Тест поиска сотрудников по компетенции"""
    # Добавляем сотрудников с разными компетенциями
    employee1 = sample_employee_data.copy()
    employee1["name"] = "Python разработчик"
    employee1["competencies"] = ["Python", "SQL"]
    
    employee2 = sample_employee_data.copy()
    employee2["name"] = "Java разработчик"
    employee2["competencies"] = ["Java", "Spring"]
    
    test_database.add_employee(employee1)
    test_database.add_employee(employee2)
    
    # Ищем Python разработчиков
    python_devs = test_database.get_staff_by_competency("Python")
    assert len(python_devs) == 1
    assert python_devs[0]["name"] == "Python разработчик"
    
    # Ищем Java разработчиков
    java_devs = test_database.get_staff_by_competency("Java")
    assert len(java_devs) == 1
    assert java_devs[0]["name"] == "Java разработчик" 