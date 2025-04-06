from fastapi import APIRouter, Depends, HTTPException
import sqlite3
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

# Создаем свою функцию для получения соединения с БД
def get_db():
    """Предоставляет соединение с базой данных."""
    DB_PATH = "full_api_new.db"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

router = APIRouter(
    prefix="/org-structure",
    tags=["organization structure"],
    responses={404: {"description": "Not found"}},
)

# Модели для возвращаемых данных
class OrgStructureNode(BaseModel):
    id: int
    name: str
    code: str
    entity_type: str  # organization, division, section, etc.
    org_type: Optional[str] = None  # для organization: HOLDING, LEGAL_ENTITY, LOCATION, BOARD
    children: Optional[List[Any]] = []

class StaffNode(BaseModel):
    id: int
    name: str
    position: str
    email: Optional[str] = None
    relations: Optional[List[Dict[str, Any]]] = []

class MatrixRelation(BaseModel):
    id: int
    from_id: int
    to_id: int
    from_name: str
    to_name: str
    relation_type: str
    description: Optional[str] = None
    extra_info: Optional[str] = None

# API эндпоинты для организационной структуры
@router.get("/hierarchy", response_model=List[OrgStructureNode])
def get_org_hierarchy(db: sqlite3.Connection = Depends(get_db)):
    """
    Получает иерархическую структуру организации.
    Структура включает организации, подразделения, отделы.
    """
    cursor = db.cursor()
    
    # Получаем все организации верхнего уровня (без parent_id или parent_id = NULL)
    cursor.execute("""
        SELECT id, name, code, org_type, description
        FROM organizations
        WHERE parent_id IS NULL
        ORDER BY name
    """)
    
    top_orgs = cursor.fetchall()
    result = []
    
    # Для каждой организации верхнего уровня строим дерево
    for org in top_orgs:
        org_node = build_org_tree(db, org)
        result.append(org_node)
    
    return result

def build_org_tree(db, org):
    """Рекурсивно строит дерево организационной структуры"""
    org_id, name, code, org_type, desc = org
    
    # Создаем узел для текущей организации
    node = {
        "id": org_id,
        "name": name,
        "code": code,
        "entity_type": "organization",
        "org_type": org_type,
        "children": []
    }
    
    cursor = db.cursor()
    
    # Получаем дочерние организации
    cursor.execute("""
        SELECT id, name, code, org_type, description
        FROM organizations
        WHERE parent_id = ?
        ORDER BY name
    """, (org_id,))
    
    child_orgs = cursor.fetchall()
    for child_org in child_orgs:
        child_node = build_org_tree(db, child_org)
        node["children"].append(child_node)
    
    # Если это HOLDING или LEGAL_ENTITY, получаем связанные подразделения
    if org_type in ["holding", "legal_entity"]:
        cursor.execute("""
            SELECT id, name, code, description
            FROM divisions
            WHERE organization_id = ?
            AND parent_id IS NULL
            ORDER BY name
        """, (org_id,))
        
        divisions = cursor.fetchall()
        for div in divisions:
            div_id, div_name, div_code, div_desc = div
            div_node = {
                "id": div_id,
                "name": div_name,
                "code": div_code,
                "entity_type": "division",
                "children": []
            }
            
            # Получаем отделы этого подразделения
            cursor.execute("""
                SELECT s.id, s.name, s.code, s.description
                FROM sections s
                JOIN division_sections ds ON s.id = ds.section_id
                WHERE ds.division_id = ?
                ORDER BY s.name
            """, (div_id,))
            
            sections = cursor.fetchall()
            for section in sections:
                sec_id, sec_name, sec_code, sec_desc = section
                sec_node = {
                    "id": sec_id,
                    "name": sec_name,
                    "code": sec_code,
                    "entity_type": "section",
                    "children": []
                }
                
                # Получаем функции этого отдела
                cursor.execute("""
                    SELECT f.id, f.name, f.code, f.description
                    FROM functions f
                    JOIN section_functions sf ON f.id = sf.function_id
                    WHERE sf.section_id = ?
                    ORDER BY f.name
                """, (sec_id,))
                
                functions = cursor.fetchall()
                for func in functions:
                    func_id, func_name, func_code, func_desc = func
                    func_node = {
                        "id": func_id,
                        "name": func_name,
                        "code": func_code,
                        "entity_type": "function",
                        "children": []
                    }
                    
                    sec_node["children"].append(func_node)
                
                div_node["children"].append(sec_node)
            
            # Получаем дочерние подразделения
            cursor.execute("""
                SELECT id, name, code, description
                FROM divisions
                WHERE parent_id = ?
                ORDER BY name
            """, (div_id,))
            
            child_divisions = cursor.fetchall()
            for child_div in child_divisions:
                child_div_id, child_div_name, child_div_code, child_div_desc = child_div
                child_div_node = build_division_tree(db, child_div)
                div_node["children"].append(child_div_node)
                
            node["children"].append(div_node)
    
    return node

def build_division_tree(db, division):
    """Рекурсивно строит дерево подразделений"""
    div_id, div_name, div_code, div_desc = division
    
    div_node = {
        "id": div_id,
        "name": div_name,
        "code": div_code,
        "entity_type": "division",
        "children": []
    }
    
    cursor = db.cursor()
    
    # Получаем отделы этого подразделения
    cursor.execute("""
        SELECT s.id, s.name, s.code, s.description
        FROM sections s
        JOIN division_sections ds ON s.id = ds.section_id
        WHERE ds.division_id = ?
        ORDER BY s.name
    """, (div_id,))
    
    sections = cursor.fetchall()
    for section in sections:
        sec_id, sec_name, sec_code, sec_desc = section
        sec_node = {
            "id": sec_id,
            "name": sec_name,
            "code": sec_code,
            "entity_type": "section",
            "children": []
        }
        
        # Получаем функции этого отдела
        cursor.execute("""
            SELECT f.id, f.name, f.code, f.description
            FROM functions f
            JOIN section_functions sf ON f.id = sf.function_id
            WHERE sf.section_id = ?
            ORDER BY f.name
        """, (sec_id,))
        
        functions = cursor.fetchall()
        for func in functions:
            func_id, func_name, func_code, func_desc = func
            func_node = {
                "id": func_id,
                "name": func_name,
                "code": func_code,
                "entity_type": "function",
                "children": []
            }
            
            sec_node["children"].append(func_node)
        
        div_node["children"].append(sec_node)
    
    # Получаем дочерние подразделения
    cursor.execute("""
        SELECT id, name, code, description
        FROM divisions
        WHERE parent_id = ?
        ORDER BY name
    """, (div_id,))
    
    child_divisions = cursor.fetchall()
    for child_div in child_divisions:
        child_div_node = build_division_tree(db, child_div)
        div_node["children"].append(child_div_node)
    
    return div_node

@router.get("/staff-tree", response_model=List[StaffNode])
def get_staff_hierarchy(db: sqlite3.Connection = Depends(get_db)):
    """
    Получает иерархию сотрудников на основе функциональных отношений.
    Показывает административное подчинение и другие типы отношений.
    """
    cursor = db.cursor()
    
    # Находим топ-менеджеров (тех, кто не имеет менеджеров с типом отношения 'administrative')
    cursor.execute("""
        SELECT s.id, s.first_name, s.last_name, s.email 
        FROM staff s
        WHERE s.id NOT IN (
            SELECT subordinate_id 
            FROM functional_relations 
            WHERE relation_type = 'administrative' AND is_active = 1
        )
        AND s.is_active = 1
        ORDER BY s.last_name, s.first_name
    """)
    
    top_managers = cursor.fetchall()
    result = []
    
    # Для каждого топ-менеджера строим дерево подчиненных
    for manager in top_managers:
        manager_id, first_name, last_name, email = manager
        
        # Получаем основную должность менеджера
        cursor.execute("""
            SELECT p.name
            FROM positions p
            JOIN staff_positions sp ON p.id = sp.position_id
            WHERE sp.staff_id = ? AND sp.is_primary = 1
            LIMIT 1
        """, (manager_id,))
        
        position_row = cursor.fetchone()
        position = position_row[0] if position_row else "Неизвестная должность"
        
        manager_node = {
            "id": manager_id,
            "name": f"{first_name} {last_name}",
            "position": position,
            "email": email,
            "relations": [],
            "children": []
        }
        
        # Строим дерево подчиненных для этого менеджера
        build_staff_tree(db, manager_id, manager_node)
        result.append(manager_node)
    
    return result

def build_staff_tree(db, manager_id, node):
    """Рекурсивно строит дерево подчиненных для менеджера"""
    cursor = db.cursor()
    
    # Получаем прямых подчиненных текущего менеджера (административное подчинение)
    cursor.execute("""
        SELECT s.id, s.first_name, s.last_name, s.email, fr.relation_type, fr.description
        FROM staff s
        JOIN functional_relations fr ON s.id = fr.subordinate_id
        WHERE fr.manager_id = ? AND fr.relation_type = 'administrative' AND fr.is_active = 1
        ORDER BY s.last_name, s.first_name
    """, (manager_id,))
    
    subordinates = cursor.fetchall()
    
    for sub in subordinates:
        sub_id, first_name, last_name, email, relation_type, description = sub
        
        # Получаем основную должность сотрудника
        cursor.execute("""
            SELECT p.name
            FROM positions p
            JOIN staff_positions sp ON p.id = sp.position_id
            WHERE sp.staff_id = ? AND sp.is_primary = 1
            LIMIT 1
        """, (sub_id,))
        
        position_row = cursor.fetchone()
        position = position_row[0] if position_row else "Неизвестная должность"
        
        sub_node = {
            "id": sub_id,
            "name": f"{first_name} {last_name}",
            "position": position,
            "email": email,
            "relations": [],
            "children": []
        }
        
        # Получаем другие типы отношений для этого сотрудника
        cursor.execute("""
            SELECT fr.id, fr.manager_id, fr.relation_type, fr.description, 
                   m.first_name, m.last_name
            FROM functional_relations fr
            JOIN staff m ON fr.manager_id = m.id
            WHERE fr.subordinate_id = ? 
              AND fr.relation_type != 'administrative'
              AND fr.is_active = 1
        """, (sub_id,))
        
        other_relations = cursor.fetchall()
        for rel in other_relations:
            rel_id, rel_manager_id, rel_type, rel_desc, m_first, m_last = rel
            relation = {
                "id": rel_id,
                "manager_id": rel_manager_id,
                "manager_name": f"{m_first} {m_last}",
                "relation_type": rel_type,
                "description": rel_desc
            }
            sub_node["relations"].append(relation)
        
        # Рекурсивно строим дерево для этого подчиненного
        build_staff_tree(db, sub_id, sub_node)
        
        # Добавляем подчиненного в дерево
        node["children"].append(sub_node)

@router.get("/matrix-relations", response_model=List[MatrixRelation])
def get_matrix_relations(
    relation_type: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Получает матричные отношения между сотрудниками.
    Можно фильтровать по типу отношения.
    """
    cursor = db.cursor()
    
    query = """
        SELECT fr.id, fr.manager_id, fr.subordinate_id, fr.relation_type, fr.description, fr.extra_field1,
               m.first_name AS m_first, m.last_name AS m_last,
               s.first_name AS s_first, s.last_name AS s_last
        FROM functional_relations fr
        JOIN staff m ON fr.manager_id = m.id
        JOIN staff s ON fr.subordinate_id = s.id
        WHERE fr.is_active = 1
    """
    
    params = []
    
    if relation_type:
        query += " AND fr.relation_type = ?"
        params.append(relation_type)
    
    query += " ORDER BY fr.relation_type, m.last_name, m.first_name, s.last_name, s.first_name"
    
    cursor.execute(query, params)
    relations = cursor.fetchall()
    
    result = []
    for rel in relations:
        rel_id, manager_id, subordinate_id, rel_type, description, extra_field1, m_first, m_last, s_first, s_last = rel
        
        relation = {
            "id": rel_id,
            "from_id": manager_id,
            "to_id": subordinate_id,
            "from_name": f"{m_first} {m_last}",
            "to_name": f"{s_first} {s_last}",
            "relation_type": rel_type,
            "description": description,
            "extra_info": extra_field1
        }
        
        result.append(relation)
    
    return result

@router.get("/staff-info/{staff_id}", response_model=Dict[str, Any])
def get_staff_detailed_info(staff_id: int, db: sqlite3.Connection = Depends(get_db)):
    """
    Получает детальную информацию о сотруднике, включая все его должности,
    локации, функции и отношения с другими сотрудниками.
    """
    cursor = db.cursor()
    
    # Получаем основную информацию о сотруднике
    cursor.execute("""
        SELECT id, first_name, last_name, middle_name, email, phone, 
               primary_organization_id, is_active, description
        FROM staff
        WHERE id = ?
    """, (staff_id,))
    
    staff_data = cursor.fetchone()
    if not staff_data:
        raise HTTPException(status_code=404, detail=f"Сотрудник с ID {staff_id} не найден")
    
    staff_id, first_name, last_name, middle_name, email, phone, primary_org_id, is_active, description = staff_data
    
    # Получаем название основной организации
    primary_org_name = None
    if primary_org_id:
        cursor.execute("SELECT name FROM organizations WHERE id = ?", (primary_org_id,))
        org_row = cursor.fetchone()
        if org_row:
            primary_org_name = org_row[0]
    
    # Получаем все должности сотрудника
    cursor.execute("""
        SELECT sp.id, p.name AS position_name, d.name AS division_name, 
               sp.is_primary, sp.start_date, sp.end_date
        FROM staff_positions sp
        JOIN positions p ON sp.position_id = p.id
        LEFT JOIN divisions d ON sp.division_id = d.id
        WHERE sp.staff_id = ?
        ORDER BY sp.is_primary DESC, sp.start_date DESC
    """, (staff_id,))
    
    positions = []
    for pos in cursor.fetchall():
        pos_id, pos_name, div_name, is_primary, start_date, end_date = pos
        positions.append({
            "id": pos_id,
            "position_name": pos_name,
            "division_name": div_name,
            "is_primary": bool(is_primary),
            "start_date": start_date,
            "end_date": end_date
        })
    
    # Получаем все локации сотрудника
    cursor.execute("""
        SELECT sl.id, o.name AS location_name, sl.is_current, sl.date_from, sl.date_to
        FROM staff_locations sl
        JOIN organizations o ON sl.location_id = o.id
        WHERE sl.staff_id = ?
        ORDER BY sl.is_current DESC, sl.date_from DESC
    """, (staff_id,))
    
    locations = []
    for loc in cursor.fetchall():
        loc_id, loc_name, is_current, date_from, date_to = loc
        locations.append({
            "id": loc_id,
            "location_name": loc_name,
            "is_current": bool(is_current),
            "date_from": date_from,
            "date_to": date_to
        })
    
    # Получаем все функции сотрудника
    cursor.execute("""
        SELECT sf.id, f.name AS function_name, sf.commitment_percent, 
               sf.is_primary, sf.date_from, sf.date_to
        FROM staff_functions sf
        JOIN functions f ON sf.function_id = f.id
        WHERE sf.staff_id = ?
        ORDER BY sf.is_primary DESC, sf.date_from DESC
    """, (staff_id,))
    
    functions = []
    for func in cursor.fetchall():
        func_id, func_name, commitment, is_primary, date_from, date_to = func
        functions.append({
            "id": func_id,
            "function_name": func_name,
            "commitment_percent": commitment,
            "is_primary": bool(is_primary),
            "date_from": date_from,
            "date_to": date_to
        })
    
    # Получаем все отношения, где сотрудник является подчиненным
    cursor.execute("""
        SELECT fr.id, fr.manager_id, m.first_name, m.last_name, 
               fr.relation_type, fr.description, fr.start_date, fr.end_date
        FROM functional_relations fr
        JOIN staff m ON fr.manager_id = m.id
        WHERE fr.subordinate_id = ? AND fr.is_active = 1
        ORDER BY fr.relation_type
    """, (staff_id,))
    
    managers = []
    for rel in cursor.fetchall():
        rel_id, manager_id, m_first, m_last, rel_type, description, start_date, end_date = rel
        managers.append({
            "id": rel_id,
            "manager_id": manager_id,
            "manager_name": f"{m_first} {m_last}",
            "relation_type": rel_type,
            "description": description,
            "start_date": start_date,
            "end_date": end_date
        })
    
    # Получаем все отношения, где сотрудник является руководителем
    cursor.execute("""
        SELECT fr.id, fr.subordinate_id, s.first_name, s.last_name, 
               fr.relation_type, fr.description, fr.start_date, fr.end_date
        FROM functional_relations fr
        JOIN staff s ON fr.subordinate_id = s.id
        WHERE fr.manager_id = ? AND fr.is_active = 1
        ORDER BY fr.relation_type
    """, (staff_id,))
    
    subordinates = []
    for rel in cursor.fetchall():
        rel_id, sub_id, s_first, s_last, rel_type, description, start_date, end_date = rel
        subordinates.append({
            "id": rel_id,
            "subordinate_id": sub_id,
            "subordinate_name": f"{s_first} {s_last}",
            "relation_type": rel_type,
            "description": description,
            "start_date": start_date,
            "end_date": end_date
        })
    
    # Формируем результат
    result = {
        "id": staff_id,
        "name": f"{first_name} {last_name}",
        "full_name": f"{last_name} {first_name} {middle_name or ''}".strip(),
        "email": email,
        "phone": phone,
        "is_active": bool(is_active),
        "description": description,
        "primary_organization": {
            "id": primary_org_id,
            "name": primary_org_name
        } if primary_org_id else None,
        "positions": positions,
        "locations": locations,
        "functions": functions,
        "managers": managers,
        "subordinates": subordinates
    }
    
    return result 