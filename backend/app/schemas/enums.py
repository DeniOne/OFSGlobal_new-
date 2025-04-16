from enum import Enum

# Enum для типов организаций
class OrgType(str, Enum):
    """Типы организационных структур"""
    BOARD = "board"  # Совет учредителей
    HOLDING = "holding"  # Холдинг/головная компания
    LEGAL_ENTITY = "legal_entity"  # Юридическое лицо (ИП, ООО и т.д.)
    LOCATION = "location"  # Физическая локация/филиал

# Enum для атрибутов должностей
class PositionAttribute(str, Enum):
    """Атрибуты должностей (уровень доступа/важности)"""
    BOARD = "Совет Учредителей"
    TOP_MANAGEMENT = "Высшее Руководство (Генеральный Директор)"
    DIRECTOR = "Директор Направления"
    DEPARTMENT_HEAD = "Руководитель Департамента"
    SECTION_HEAD = "Руководитель Отдела"
    SPECIALIST = "Специалист"

# Enum для типов функциональных связей
class RelationType(str, Enum):
    """Типы функциональных связей между сотрудниками"""
    FUNCTIONAL = "functional"  # Функциональное подчинение
    ADMINISTRATIVE = "administrative"  # Административное подчинение
    PROJECT = "project"  # Проектное подчинение
    TERRITORIAL = "territorial"  # Территориальное подчинение
    MENTORING = "mentoring"  # Менторство
    STRATEGIC = "strategic"  # Стратегическое управление
    GOVERNANCE = "governance"  # Корпоративное управление
    ADVISORY = "advisory"  # Консультативное управление
    SUPERVISORY = "supervisory"  # Надзорное управление 