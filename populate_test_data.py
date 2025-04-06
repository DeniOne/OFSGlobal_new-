import requests
import json
import time
import random
from faker import Faker

# Настройки API
API_URL = "http://127.0.0.1:8000"  # Base URL
API_PREFIX = ""  # Для full_api используем пустой префикс
fake = Faker('ru_RU')

# Включить отладочные сообщения
DEBUG = True

def debug_print(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

# Структура данных

# 1. Организации
organizations = [
    {
        "name": "Фотоматрица",
        "code": "photomatrix",
        "description": "Головная компания группы",
        "org_type": "holding",
        "is_active": True,
        "parent_id": None,
        "inn": "7715648570",
        "kpp": "771501001",
        "legal_address": "г. Москва, ул. Ленина, 12",
        "physical_address": "г. Москва, ул. Ленина, 12"
    }
]

# Юридические лица, дочерние к Фотоматрице
legal_entities = [
    {
        "name": "ООО Фотопро",
        "code": "photopro",
        "description": "Юридическое лицо для основной деятельности",
        "org_type": "legal_entity",
        "is_active": True,
        "inn": "7702386543",
        "kpp": "770201001",
        "legal_address": "г. Москва, ул. Тверская, 24",
        "physical_address": "г. Москва, ул. Тверская, 24"
    },
    {
        "name": "ООО ФотоСервис",
        "code": "photoservice",
        "description": "Вспомогательное юридическое лицо",
        "org_type": "legal_entity",
        "is_active": True,
        "inn": "7703124568",
        "kpp": "770301001",
        "legal_address": "г. Москва, ул. Новый Арбат, 8",
        "physical_address": "г. Москва, ул. Новый Арбат, 8"
    },
    {
        "name": "ИП Фотомастер",
        "code": "photomaster",
        "description": "Малое предприятие для отдельных проектов",
        "org_type": "legal_entity",
        "is_active": True,
        "inn": "770301456099",
        "legal_address": "г. Москва, ул. Садовая, 17",
        "physical_address": "г. Москва, ул. Садовая, 17"
    }
]

# 2. Локации
locations = []
for i in range(1, 10):
    locations.append({
        "name": f"Локация {i}",
        "code": f"location{i}",
        "description": f"Тестовая локация номер {i}",
        "org_type": "location",
        "is_active": True,
        "legal_address": f"г. {fake.city()}, ул. {fake.street_name()}, {random.randint(1, 100)}",
        "physical_address": f"г. {fake.city()}, ул. {fake.street_name()}, {random.randint(1, 100)}"
    })

# 3. Департаменты/отделы
divisions = [
    {
        "name": "Департамент фотографии",
        "code": "photo_dept",
        "description": "Основной департамент фотографии",
        "is_active": True
    },
    {
        "name": "Департамент продаж",
        "code": "sales_dept",
        "description": "Департамент по продажам продукции",
        "is_active": True
    },
    {
        "name": "Департамент управления",
        "code": "management_dept",
        "description": "Управление компанией",
        "is_active": True
    },
    {
        "name": "Отдел фотосъемки",
        "code": "photo_shooting",
        "description": "Отдел выполнения фотосессий",
        "is_active": True
    },
    {
        "name": "Отдел обработки",
        "code": "photo_editing",
        "description": "Отдел обработки и ретуши",
        "is_active": True
    },
    {
        "name": "Отдел розничных продаж",
        "code": "retail_sales",
        "description": "Отдел по розничным продажам",
        "is_active": True
    },
    {
        "name": "Отдел стратегического развития",
        "code": "strategic_dev",
        "description": "Отдел стратегического развития компании",
        "is_active": True
    }
]

# 4. Должности (из запроса пользователя)
positions = [
    {"name": "Фотограф", "code": "photographer", "description": "Выполняет фотосъемку"},
    {"name": "Ретушер", "code": "retoucher", "description": "Обрабатывает и ретуширует фотографии"},
    {"name": "Продавец", "code": "sales_person", "description": "Работает с клиентами и осуществляет продажи"},
    {"name": "Старший фотограф", "code": "senior_photographer", "description": "Опытный фотограф, выполняет сложные задания"},
    {"name": "Управляющий", "code": "manager", "description": "Управляет локацией или подразделением"},
    {"name": "Стажер", "code": "intern", "description": "Обучается в компании"},
    {"name": "Генеральный директор", "code": "ceo", "description": "Руководит компанией"},
    {"name": "Директор по стратегическому развитию", "code": "strategic_director", "description": "Отвечает за стратегию развития"},
    {"name": "Учредитель", "code": "founder", "description": "Основатель компании"},
    {"name": "Руководитель департамента", "code": "dept_head", "description": "Возглавляет департамент"},
    {"name": "Специалист производства", "code": "production_specialist", "description": "Отвечает за производственные процессы"},
    {"name": "Помощник продавца", "code": "sales_assistant", "description": "Помогает в работе с клиентами"}
]

# 5. Функции
functions = [
    {"name": "Фотосъемка", "code": "photo_shooting", "description": "Фотографирование клиентов и объектов"},
    {"name": "Обработка", "code": "photo_editing", "description": "Обработка и ретушь фотографий"},
    {"name": "Продажи", "code": "sales", "description": "Продажа услуг и товаров компании"},
    {"name": "Управление персоналом", "code": "hr_management", "description": "Управление персоналом компании"},
    {"name": "Стратегическое управление", "code": "strategic_management", "description": "Разработка и контроль стратегии компании"}
]

# 6. Соответствие между должностями и отделами
position_to_division = {
    "Фотограф": "Отдел фотосъемки",
    "Ретушер": "Отдел обработки",
    "Продавец": "Отдел розничных продаж",
    "Старший фотограф": "Отдел фотосъемки",
    "Управляющий": "Департамент управления",
    "Стажер": None,  # Может быть в любом отделе
    "Генеральный директор": "Департамент управления",
    "Директор по стратегическому развитию": "Отдел стратегического развития",
    "Учредитель": None,
    "Руководитель департамента": None,  # Может быть в любом департаменте
    "Специалист производства": "Департамент фотографии",
    "Помощник продавца": "Отдел розничных продаж"
}

# 7. Соответствие между должностями и функциями
position_to_function = {
    "Фотограф": "Фотосъемка",
    "Ретушер": "Обработка",
    "Продавец": "Продажи",
    "Старший фотограф": "Фотосъемка",
    "Управляющий": "Управление персоналом",
    "Стажер": None,
    "Генеральный директор": "Стратегическое управление",
    "Директор по стратегическому развитию": "Стратегическое управление",
    "Учредитель": "Стратегическое управление",
    "Руководитель департамента": "Управление персоналом",
    "Специалист производства": "Фотосъемка",
    "Помощник продавца": "Продажи"
}

# Служебные переменные для хранения созданных ID
created_orgs = {}
created_divisions = {}
created_positions = {}
created_functions = {}
created_staff = {}

# Создадим тестовый объект для проверки API
test_organization = {
    "name": "Тестовая организация",
    "code": "test_org",
    "description": "Тестовая организация для проверки API",
    "org_type": "legal_entity",
    "is_active": True,
    "inn": "7701234567",
    "kpp": "770101001",
    "legal_address": "Тестовый адрес",
    "physical_address": "Тестовый адрес"
}

def test_api():
    """Проверка наличия и работоспособности различных API эндпоинтов"""
    print("🔍 Тестирование API...")
    
    endpoints = [
        # Попробуем разные варианты путей
        "/",
        "/organizations/",
        "/divisions/",
        "/staff/",
        "/positions/",
        "/functions/",
    ]
    
    for endpoint in endpoints:
        url = f"{API_URL}{endpoint}"
        try:
            print(f"Проверка: {url}")
            response = requests.get(url)
            print(f"  Статус: {response.status_code}")
            if response.status_code == 200:
                print(f"  Содержимое: {response.text[:100]}...")
            else:
                print(f"  Ошибка: {response.text[:100]}...")
        except Exception as e:
            print(f"  Ошибка: {str(e)}")
    
    # Пробуем создать тестовую организацию
    try:
        print(f"\nПопытка создания тестовой организации через API...")
        post_url = f"{API_URL}{API_PREFIX}/organizations/"
        response = requests.post(post_url, json=test_organization)
        print(f"  Статус: {response.status_code}")
        
        if response.status_code in (200, 201):
            print(f"  Ответ: {response.text}")
            print(f"✅ API работает корректно!")
        else:
            print(f"❌ Не удалось создать тестовую организацию: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка при создании тестовой организации: {str(e)}")
    
    return API_PREFIX

def create_organization(org_data, parent_id=None, api_prefix=""):
    """Создать организацию через API"""
    try:
        if parent_id:
            org_data["parent_id"] = parent_id
        
        # Отладочная информация о запросе
        url = f"{API_URL}{api_prefix}/organizations/"
        debug_print(f"POST {url} с данными: {json.dumps(org_data, ensure_ascii=False)}")
        
        response = requests.post(url, json=org_data)
        
        debug_print(f"Ответ: {response.status_code}, {response.text[:200]}...")
        
        if response.status_code in (200, 201):
            print(f"✅ Создана организация: {org_data['name']}")
            return response.json()
        else:
            print(f"❌ Ошибка при создании организации {org_data['name']}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Исключение при создании организации: {str(e)}")
        return None

def create_division(division_data, org_id, api_prefix=""):
    """Создать подразделение/отдел через API"""
    try:
        division_data["organization_id"] = org_id
        
        url = f"{API_URL}{api_prefix}/divisions/"
        debug_print(f"POST {url} с данными: {json.dumps(division_data, ensure_ascii=False)}")
        
        response = requests.post(url, json=division_data)
        
        debug_print(f"Ответ: {response.status_code}, {response.text[:200]}...")
        
        if response.status_code in (200, 201):
            print(f"✅ Создан отдел: {division_data['name']}")
            return response.json()
        else:
            print(f"❌ Ошибка при создании отдела {division_data['name']}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Исключение при создании отдела: {str(e)}")
        return None

def create_function(function_data, api_prefix=""):
    """Создать функцию через API"""
    try:
        url = f"{API_URL}{api_prefix}/functions/"
        debug_print(f"POST {url} с данными: {json.dumps(function_data, ensure_ascii=False)}")
        
        response = requests.post(url, json=function_data)
        
        debug_print(f"Ответ: {response.status_code}, {response.text[:200]}...")
        
        if response.status_code in (200, 201):
            print(f"✅ Создана функция: {function_data['name']}")
            return response.json()
        else:
            print(f"❌ Ошибка при создании функции {function_data['name']}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Исключение при создании функции: {str(e)}")
        return None

def create_position(position_data, function_id=None, api_prefix=""):
    """Создать должность через API"""
    try:
        if function_id:
            position_data["function_id"] = function_id
        
        url = f"{API_URL}{api_prefix}/positions/"
        debug_print(f"POST {url} с данными: {json.dumps(position_data, ensure_ascii=False)}")
        
        response = requests.post(url, json=position_data)
        
        debug_print(f"Ответ: {response.status_code}, {response.text[:200]}...")
        
        if response.status_code in (200, 201):
            print(f"✅ Создана должность: {position_data['name']}")
            return response.json()
        else:
            print(f"❌ Ошибка при создании должности {position_data['name']}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Исключение при создании должности: {str(e)}")
        return None

def create_staff(staff_data, api_prefix=""):
    """Создать сотрудника через API"""
    try:
        url = f"{API_URL}{api_prefix}/staff/"
        debug_print(f"POST {url} с данными: {json.dumps(staff_data, ensure_ascii=False)}")
        
        response = requests.post(url, json=staff_data)
        
        debug_print(f"Ответ: {response.status_code}, {response.text[:200]}...")
        
        if response.status_code in (200, 201):
            print(f"✅ Создан сотрудник: {staff_data['first_name']} {staff_data['last_name']}")
            return response.json()
        else:
            print(f"❌ Ошибка при создании сотрудника {staff_data['first_name']} {staff_data['last_name']}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Исключение при создании сотрудника: {str(e)}")
        return None

def populate_database():
    """Заполнение базы данных тестовыми данными"""
    print("🚀 Начинаем заполнение базы данных тестовыми данными...")
    
    # Сначала протестируем API и найдем рабочие эндпоинты
    api_prefix = test_api()
    
    if api_prefix is None:
        print("❌ Не удалось найти рабочие API эндпоинты. Возможно, сервер не запущен или API изменилось.")
        return
    
    print(f"\nИспользуем API префикс: '{api_prefix}'")
    
    print("\n1. Создание организаций:")
    # 1. Создание головной организации
    main_org = create_organization(organizations[0], api_prefix=api_prefix)
    if not main_org:
        print("❌ Не удалось создать головную организацию. Прерываем выполнение.")
        return
    
    created_orgs[main_org["name"]] = main_org["id"]
    
    # 2. Создание юридических лиц
    for entity in legal_entities:
        org = create_organization(entity, parent_id=main_org["id"], api_prefix=api_prefix)
        if org:
            created_orgs[org["name"]] = org["id"]
    
    # 3. Создание локаций
    for location in locations:
        # Привязываем локации к случайному юр.лицу
        parent_id = random.choice(list(created_orgs.values()))
        org = create_organization(location, parent_id=parent_id, api_prefix=api_prefix)
        if org:
            created_orgs[org["name"]] = org["id"]
    
    print("\n2. Создание функций:")
    # 4. Создание функций
    for func in functions:
        function = create_function(func, api_prefix=api_prefix)
        if function:
            created_functions[function["name"]] = function["id"]
    
    print("\n3. Создание отделов/департаментов:")
    # 5. Создание отделов/департаментов
    for div in divisions:
        # Привязываем отделы к головной организации
        division = create_division(div, main_org["id"], api_prefix=api_prefix)
        if division:
            created_divisions[division["name"]] = division["id"]
    
    print("\n4. Создание должностей:")
    # 6. Создание должностей
    for pos in positions:
        # Проверяем, есть ли связь с функцией
        func_name = position_to_function.get(pos["name"])
        func_id = created_functions.get(func_name) if func_name else None
        
        position = create_position(pos, func_id, api_prefix=api_prefix)
        if position:
            created_positions[position["name"]] = position["id"]
    
    print("\n5. Создание сотрудников:")
    # 7. Создание сотрудников
    for _ in range(20):  # Создадим 20 сотрудников
        # Выбираем случайную должность
        position_name = random.choice(list(created_positions.keys()))
        position_id = created_positions[position_name]
        
        # Выбираем случайную организацию среди юр.лиц и локаций
        orgs = {k: v for k, v in created_orgs.items() if "Фотоматрица" not in k}  # Исключаем головную
        org_name = random.choice(list(orgs.keys()))
        org_id = orgs[org_name]
        
        # Выбираем подразделение в соответствии с должностью
        div_name = position_to_division.get(position_name)
        if div_name and div_name in created_divisions:
            division_id = created_divisions[div_name]
        else:
            # Если нет привязки или подразделение не создано, выбираем случайное
            division_id = random.choice(list(created_divisions.values()))
        
        # Генерируем данные сотрудника
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # API ожидает разбитое полное имя
        staff_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": fake.email(),
            "phone": fake.phone_number(),
            "organization_id": org_id,
            "is_active": True
        }
        
        staff = create_staff(staff_data, api_prefix=api_prefix)
        if staff:
            created_staff[f"{first_name} {last_name}"] = staff["id"]
    
    print(f"\n✅ База данных успешно заполнена тестовыми данными!")
    print(f"📊 Статистика:")
    print(f"   - Организаций: {len(created_orgs)}")
    print(f"   - Отделов: {len(created_divisions)}")
    print(f"   - Функций: {len(created_functions)}")
    print(f"   - Должностей: {len(created_positions)}")
    print(f"   - Сотрудников: {len(created_staff)}")

if __name__ == "__main__":
    populate_database() 