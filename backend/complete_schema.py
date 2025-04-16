"""
Полная схема данных для проекта OFS Global.
Этот файл содержит SQL-запросы для создания всех таблиц и связей.
Включает дополнительные поля для будущих расширений.
"""

# Схема для таблицы пользователей (аутентификация)
USER_SCHEMA = """
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    full_name TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    is_superuser INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_user_timestamp
AFTER UPDATE ON user
FOR EACH ROW
BEGIN
    UPDATE user SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Индекс для email
CREATE INDEX IF NOT EXISTS idx_user_email ON user(email);
"""

# Схема для таблицы организаций
ORGANIZATION_SCHEMA = """
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    org_type TEXT NOT NULL CHECK(org_type IN ('board', 'holding', 'legal_entity', 'location')),
    is_active INTEGER NOT NULL DEFAULT 1,
    parent_id INTEGER,
    ckp TEXT,
    inn TEXT,
    kpp TEXT,
    legal_address TEXT,
    physical_address TEXT,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES organizations(id)
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_organization_timestamp 
AFTER UPDATE ON organizations
FOR EACH ROW
BEGIN
    UPDATE organizations SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_organizations_parent_id ON organizations(parent_id);
CREATE INDEX IF NOT EXISTS idx_organizations_org_type ON organizations(org_type);
"""

# Схема для таблицы подразделений
DIVISION_SCHEMA = """
CREATE TABLE IF NOT EXISTS divisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    organization_id INTEGER NOT NULL,
    parent_id INTEGER,
    ckp TEXT,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id),
    FOREIGN KEY (parent_id) REFERENCES divisions(id)
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_division_timestamp 
AFTER UPDATE ON divisions
FOR EACH ROW
BEGIN
    UPDATE divisions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_divisions_organization_id ON divisions(organization_id);
CREATE INDEX IF NOT EXISTS idx_divisions_parent_id ON divisions(parent_id);
"""

# Схема для таблицы отделов
SECTION_SCHEMA = """
CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT,
    division_id INTEGER NOT NULL,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    ckp TEXT,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_section_timestamp 
AFTER UPDATE ON sections
FOR EACH ROW
BEGIN
    UPDATE sections SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Добавляем индекс на division_id
CREATE INDEX IF NOT EXISTS idx_sections_division_id ON sections(division_id);
-- Индекс на code, если он используется
CREATE INDEX IF NOT EXISTS idx_sections_code ON sections(code);
"""

# Схема для связи подразделений и отделов (многие ко многим)
DIVISION_SECTION_SCHEMA = """
CREATE TABLE IF NOT EXISTS division_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    division_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    is_primary INTEGER NOT NULL DEFAULT 1,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (division_id) REFERENCES divisions(id),
    FOREIGN KEY (section_id) REFERENCES sections(id),
    UNIQUE(division_id, section_id)
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_division_sections_division_id ON division_sections(division_id);
CREATE INDEX IF NOT EXISTS idx_division_sections_section_id ON division_sections(section_id);
"""

# Схема для таблицы функций
FUNCTION_SCHEMA = """
CREATE TABLE IF NOT EXISTS functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_function_timestamp 
AFTER UPDATE ON functions
FOR EACH ROW
BEGIN
    UPDATE functions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
"""

# Схема для связи отделов и функций (многие ко многим)
SECTION_FUNCTION_SCHEMA = """
CREATE TABLE IF NOT EXISTS section_functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    function_id INTEGER NOT NULL,
    is_primary INTEGER NOT NULL DEFAULT 1,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (function_id) REFERENCES functions(id),
    UNIQUE(section_id, function_id)
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_section_functions_section_id ON section_functions(section_id);
CREATE INDEX IF NOT EXISTS idx_section_functions_function_id ON section_functions(function_id);
"""

# Схема для таблицы должностей
POSITION_SCHEMA = """
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    attribute TEXT NOT NULL,
    division_id INTEGER,
    section_id INTEGER,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE SET NULL,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE SET NULL
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_position_timestamp 
AFTER UPDATE ON positions
FOR EACH ROW
BEGIN
    UPDATE positions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_positions_division_id ON positions(division_id);
CREATE INDEX IF NOT EXISTS idx_positions_section_id ON positions(section_id);
-- Индекс на имя, если оно должно быть уникальным или часто ищется
CREATE UNIQUE INDEX IF NOT EXISTS idx_positions_name ON positions(name);
"""

# Схема для связи должностей и функций (многие ко многим)
POSITION_FUNCTIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS position_functions (
    position_id INTEGER NOT NULL,
    function_id INTEGER NOT NULL,
    PRIMARY KEY (position_id, function_id),
    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE,
    FOREIGN KEY (function_id) REFERENCES functions(id) ON DELETE CASCADE
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_position_functions_position_id ON position_functions(position_id);
CREATE INDEX IF NOT EXISTS idx_position_functions_function_id ON position_functions(function_id);
"""

# Схема для функциональных назначений
FUNCTIONAL_ASSIGNMENTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS functional_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id INTEGER NOT NULL,
    function_id INTEGER NOT NULL,
    percentage INTEGER DEFAULT 100,
    is_primary BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE,
    FOREIGN KEY (function_id) REFERENCES functions(id) ON DELETE CASCADE
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_functional_assignments_timestamp 
AFTER UPDATE ON functional_assignments
FOR EACH ROW
BEGIN
    UPDATE functional_assignments SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_functional_assignments_position_id ON functional_assignments(position_id);
CREATE INDEX IF NOT EXISTS idx_functional_assignments_function_id ON functional_assignments(function_id);
CREATE INDEX IF NOT EXISTS idx_functional_assignments_is_primary ON functional_assignments(is_primary);
"""

# Схема для таблицы сотрудников
STAFF_SCHEMA = """
CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    user_id INTEGER NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    middle_name TEXT,
    phone TEXT,
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    organization_id INTEGER,
    primary_organization_id INTEGER,
    location_id INTEGER,
    registration_address TEXT,
    actual_address TEXT,
    telegram_id TEXT,
    vk TEXT,
    instagram TEXT,
    photo_path TEXT,
    document_paths TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE SET NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
    FOREIGN KEY (primary_organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
    FOREIGN KEY (location_id) REFERENCES organizations(id) ON DELETE SET NULL
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_staff_timestamp 
AFTER UPDATE ON staff
FOR EACH ROW
BEGIN
    UPDATE staff SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_staff_email ON staff(email);
CREATE INDEX IF NOT EXISTS idx_staff_user_id ON staff(user_id);
CREATE INDEX IF NOT EXISTS idx_staff_organization_id ON staff(organization_id);
CREATE INDEX IF NOT EXISTS idx_staff_primary_organization_id ON staff(primary_organization_id);
CREATE INDEX IF NOT EXISTS idx_staff_location_id ON staff(location_id);
"""

# Схема для связи сотрудников и должностей
STAFF_POSITION_SCHEMA = """
CREATE TABLE IF NOT EXISTS staff_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    position_id INTEGER NOT NULL,
    division_id INTEGER,
    location_id INTEGER,  -- Физическая локация, где работает сотрудник
    is_primary INTEGER NOT NULL DEFAULT 1,
    is_active INTEGER NOT NULL DEFAULT 1,
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(id),
    FOREIGN KEY (position_id) REFERENCES positions(id),
    FOREIGN KEY (division_id) REFERENCES divisions(id),
    FOREIGN KEY (location_id) REFERENCES organizations(id)
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_staff_position_timestamp 
AFTER UPDATE ON staff_positions
FOR EACH ROW
BEGIN
    UPDATE staff_positions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_staff_positions_staff_id ON staff_positions(staff_id);
CREATE INDEX IF NOT EXISTS idx_staff_positions_position_id ON staff_positions(position_id);
CREATE INDEX IF NOT EXISTS idx_staff_positions_division_id ON staff_positions(division_id);
CREATE INDEX IF NOT EXISTS idx_staff_positions_location_id ON staff_positions(location_id);
CREATE INDEX IF NOT EXISTS idx_staff_positions_is_primary ON staff_positions(is_primary);
CREATE INDEX IF NOT EXISTS idx_staff_positions_is_active ON staff_positions(is_active);
CREATE INDEX IF NOT EXISTS idx_staff_positions_dates ON staff_positions(start_date, end_date);
"""

# Схема для связи сотрудников и физических локаций
STAFF_LOCATION_SCHEMA = """
CREATE TABLE IF NOT EXISTS staff_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    is_current INTEGER NOT NULL DEFAULT 1,
    date_from DATE NOT NULL DEFAULT CURRENT_DATE,
    date_to DATE,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(id),
    FOREIGN KEY (location_id) REFERENCES organizations(id)
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_staff_location_timestamp 
AFTER UPDATE ON staff_locations
FOR EACH ROW
BEGIN
    UPDATE staff_locations SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_staff_locations_staff_id ON staff_locations(staff_id);
CREATE INDEX IF NOT EXISTS idx_staff_locations_location_id ON staff_locations(location_id);
CREATE INDEX IF NOT EXISTS idx_staff_locations_is_current ON staff_locations(is_current);
CREATE INDEX IF NOT EXISTS idx_staff_locations_dates ON staff_locations(date_from, date_to);
"""

# Схема для связи сотрудников и функций
STAFF_FUNCTION_SCHEMA = """
CREATE TABLE IF NOT EXISTS staff_functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_id INTEGER NOT NULL,
    function_id INTEGER NOT NULL,
    commitment_percent INTEGER DEFAULT 100,
    is_primary INTEGER NOT NULL DEFAULT 1,
    date_from DATE NOT NULL DEFAULT CURRENT_DATE,
    date_to DATE,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (staff_id) REFERENCES staff(id),
    FOREIGN KEY (function_id) REFERENCES functions(id)
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_staff_function_timestamp 
AFTER UPDATE ON staff_functions
FOR EACH ROW
BEGIN
    UPDATE staff_functions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_staff_functions_staff_id ON staff_functions(staff_id);
CREATE INDEX IF NOT EXISTS idx_staff_functions_function_id ON staff_functions(function_id);
CREATE INDEX IF NOT EXISTS idx_staff_functions_is_primary ON staff_functions(is_primary);
CREATE INDEX IF NOT EXISTS idx_staff_functions_dates ON staff_functions(date_from, date_to);
"""

# Схема для связей между сотрудниками (функциональные отношения)
FUNCTIONAL_RELATION_SCHEMA = """
CREATE TABLE IF NOT EXISTS functional_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER NOT NULL,
    subordinate_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL CHECK(relation_type IN ('functional', 'administrative', 'project', 'territorial', 'mentoring', 'strategic', 'governance', 'advisory', 'supervisory')),
    description TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE,
    extra_field1 TEXT,
    extra_field2 TEXT,
    extra_field3 TEXT,
    extra_int1 INTEGER,
    extra_int2 INTEGER,
    extra_date1 DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES staff(id),
    FOREIGN KEY (subordinate_id) REFERENCES staff(id)
);

-- Триггер для автоматического обновления даты изменения
CREATE TRIGGER IF NOT EXISTS update_functional_relation_timestamp 
AFTER UPDATE ON functional_relations
FOR EACH ROW
BEGIN
    UPDATE functional_relations SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_functional_relations_manager_id ON functional_relations(manager_id);
CREATE INDEX IF NOT EXISTS idx_functional_relations_subordinate_id ON functional_relations(subordinate_id);
CREATE INDEX IF NOT EXISTS idx_functional_relations_relation_type ON functional_relations(relation_type);
CREATE INDEX IF NOT EXISTS idx_functional_relations_dates ON functional_relations(start_date, end_date);
"""

# Список всех схем для инициализации базы данных
ALL_SCHEMAS = [
    USER_SCHEMA,
    ORGANIZATION_SCHEMA,
    DIVISION_SCHEMA,
    SECTION_SCHEMA,
    DIVISION_SECTION_SCHEMA,
    FUNCTION_SCHEMA,
    SECTION_FUNCTION_SCHEMA,
    POSITION_SCHEMA,
    POSITION_FUNCTIONS_SCHEMA,
    FUNCTIONAL_ASSIGNMENTS_SCHEMA,
    STAFF_SCHEMA,
    STAFF_POSITION_SCHEMA,
    STAFF_LOCATION_SCHEMA,
    STAFF_FUNCTION_SCHEMA,
    FUNCTIONAL_RELATION_SCHEMA
] 