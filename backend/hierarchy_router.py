from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional, Dict, Any, Set
import sqlite3
import logging
from models.hierarchy import (
    HierarchyRelationBase, HierarchyRelationCreate, HierarchyRelation,
    UnitManagementBase, UnitManagementCreate, UnitManagement,
    HierarchyRelationWithDetails, UnitManagementWithDetails
)
from pydantic import ValidationError
import traceback
import uvicorn
from datetime import datetime, date, timedelta

# Настройка логирования
logger = logging.getLogger("hierarchy_api")

# Создаем роутер
router = APIRouter()

# Функция для получения соединения с БД (должна быть переопределена при подключении роутера)
async def get_db():
    """
    Возвращает соединение с базой данных для текущего запроса.
    """
    conn = sqlite3.connect("full_api_new.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Позволяет получать данные как словари
    conn.execute('PRAGMA journal_mode=WAL') 
    try:
        yield conn
    finally:
        conn.close()

# Вспомогательная функция для получения иерархической связи с деталями
async def get_hierarchy_relation_with_details(db: sqlite3.Connection, relation_id: int) -> Optional[HierarchyRelationWithDetails]:
    """Получить связь по ID с полной информацией о должностях."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT hr.*, 
            p1.name as superior_position_name, 
            p1.attribute as superior_position_attribute,
            p2.name as subordinate_position_name, 
            p2.attribute as subordinate_position_attribute
        FROM hierarchy_relations hr
        LEFT JOIN positions p1 ON hr.superior_position_id = p1.id
        LEFT JOIN positions p2 ON hr.subordinate_position_id = p2.id
        WHERE hr.id = ?
    """, (relation_id,))
    row = cursor.fetchone()
    if not row:
        return None
    
    return HierarchyRelationWithDetails(**dict(row))

# Вспомогательная функция для получения связи управления с деталями
async def get_unit_management_with_details(db: sqlite3.Connection, relation_id: int) -> Optional[UnitManagementWithDetails]:
    """Получить связь управления по ID с полной информацией о должности и управляемой единице."""
    cursor = db.cursor()
    cursor.execute("""
        SELECT um.*, 
            p.name as position_name, 
            p.attribute as position_attribute,
            CASE 
                WHEN um.managed_type = 'division' THEN (SELECT name FROM divisions WHERE id = um.managed_id)
                WHEN um.managed_type = 'section' THEN (SELECT name FROM sections WHERE id = um.managed_id)
                ELSE NULL
            END as managed_name
        FROM unit_management um
        LEFT JOIN positions p ON um.position_id = p.id
        WHERE um.id = ?
    """, (relation_id,))
    row = cursor.fetchone()
    if not row:
        return None
    
    return UnitManagementWithDetails(**dict(row))

# Вспомогательная рекурсивная функция для построения дерева
async def build_hierarchy_tree(
    db: sqlite3.Connection, 
    position_id: Optional[int], 
    nodes: List[Dict[str, Any]], 
    edges: List[Dict[str, Any]], 
    visited_nodes: Set[int]
):
    """Рекурсивно строит дерево подчиненных для заданной должности."""
    cursor = db.cursor()
    
    # Получаем прямых подчиненных
    cursor.execute("""
        SELECT hr.*, 
               p_sub.name as subordinate_position_name, 
               p_sub.attribute as subordinate_position_attribute
        FROM hierarchy_relations hr
        JOIN positions p_sub ON hr.subordinate_position_id = p_sub.id
        WHERE hr.superior_position_id = ? AND hr.is_active = 1
        ORDER BY hr.priority
    """, (position_id,))
    
    subordinates = cursor.fetchall()
    
    for sub_relation in subordinates:
        sub_position_id = sub_relation['subordinate_position_id']
        
        # Проверка на циклы
        if sub_position_id in visited_nodes:
            logger.warning(f"Обнаружен цикл в иерархии: {position_id} -> {sub_position_id}. Пропускаем.")
            continue

        # Добавляем узел подчиненного, если его еще нет
        if not any(node['id'] == f'pos-{sub_position_id}' for node in nodes):
            nodes.append({
                "id": f'pos-{sub_position_id}',
                "data": {
                    "label": sub_relation['subordinate_position_name'],
                    "attribute": sub_relation['subordinate_position_attribute'],
                    "db_id": sub_position_id # Сохраняем ID из БД
                },
                "position": {"x": 0, "y": 0}, # Позиции рассчитает dagre
                # Стиль можно будет добавить на фронте или здесь
            })
            visited_nodes.add(sub_position_id) # Добавляем в посещенные

        # Добавляем ребро связи
        edge_id = f'e_rel_{sub_relation["id"]}'
        if not any(edge['id'] == edge_id for edge in edges):
             edges.append({
                "id": edge_id,
                "source": f'pos-{position_id}',
                "target": f'pos-{sub_position_id}',
                "type": 'smoothstep', 
                "markerEnd": { "type": "arrowclosed" },
                 "data": { "priority": sub_relation['priority'] } # Доп. данные ребра
            })

        # Рекурсивно строим дерево для подчиненного
        await build_hierarchy_tree(db, sub_position_id, nodes, edges, visited_nodes)


# Новый эндпоинт для получения дерева
@router.get("/org-tree/", response_model=Dict[str, List[Dict[str, Any]]], tags=["hierarchy", "org-chart"])
async def get_organization_tree(
    root_position_id: Optional[int] = Query(None, description="ID корневой должности для построения частичного дерева"),
    organization_id: Optional[int] = Query(None, description="ID организации для фильтрации должностей"),
    depth: Optional[int] = Query(None, description="Максимальная глубина дерева (0 - только корневой узел)"),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Получить организационную структуру в виде узлов и ребер, 
    готовых для отображения в react-flow.
    Строит дерево на основе активных связей в hierarchy_relations.
    
    - Используйте root_position_id для построения частичного дерева от указанной должности
    - Используйте organization_id для фильтрации должностей по конкретной организации
    - Используйте depth для ограничения глубины дерева (по умолчанию - без ограничений)
    """
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    visited_nodes: Set[int] = set() # Для отслеживания циклов

    cursor = db.cursor()

    # Модифицируем функцию build_hierarchy_tree для поддержки глубины
    async def build_hierarchy_tree_with_depth(
        db: sqlite3.Connection, 
        position_id: Optional[int], 
        nodes: List[Dict[str, Any]], 
        edges: List[Dict[str, Any]], 
        visited_nodes: Set[int],
        current_depth: int = 0,
        max_depth: Optional[int] = None
    ):
        """Рекурсивно строит дерево с ограничением глубины"""
        # Если достигли максимальной глубины и это не None, прекращаем рекурсию
        if max_depth is not None and current_depth >= max_depth:
            return

        # Если позиция не указана или уже посещена, выходим
        if position_id is None or position_id in visited_nodes:
            return
        
        # Получаем всех подчиненных для текущей должности
        query = """
            SELECT hr.*, p.name, p.attribute 
            FROM hierarchy_relations hr
            JOIN positions p ON p.id = hr.subordinate_position_id
            WHERE hr.superior_position_id = ? AND hr.is_active = 1
        """
        params = [position_id]
        
        # Если указан ID организации, добавляем фильтр
        if organization_id is not None:
            query = """
                SELECT hr.*, p.name, p.attribute 
                FROM hierarchy_relations hr
                JOIN positions p ON p.id = hr.subordinate_position_id
                JOIN staff s ON s.position_id = p.id
                JOIN organizations o ON s.organization_id = o.id
                WHERE hr.superior_position_id = ? AND hr.is_active = 1
                AND o.id = ?
            """
            params.append(organization_id)
        
        try:
            cursor.execute(query, params)
            subordinates = cursor.fetchall()
            
            for sub_relation in subordinates:
                sub_position_id = sub_relation['subordinate_position_id']
                
                # Если еще не добавляли этот узел, добавляем его
                if sub_position_id not in visited_nodes:
                    nodes.append({
                        "id": f'pos-{sub_position_id}',
                        "data": {
                            "label": sub_relation['name'],
                            "attribute": sub_relation['attribute'],
                            "db_id": sub_position_id
                        },
                        "position": {"x": 0, "y": 0}
                    })
                    visited_nodes.add(sub_position_id)
                
                # Всегда добавляем ребро, т.к. может быть несколько отношений между теми же узлами
                edges.append({
                    "id": f'e-{sub_relation["id"]}',
                    "source": f'pos-{position_id}',
                    "target": f'pos-{sub_position_id}',
                    "type": 'smoothstep', 
                    "markerEnd": { "type": "arrowclosed" },
                    "data": { "priority": sub_relation['priority'] } # Доп. данные ребра
                })

                # Рекурсивно строим дерево для подчиненного с увеличением глубины
                await build_hierarchy_tree_with_depth(
                    db, 
                    sub_position_id, 
                    nodes, 
                    edges, 
                    visited_nodes,
                    current_depth + 1,
                    max_depth
                )
        except Exception as e:
            logger.error(f"Ошибка при получении подчиненных для должности {position_id}: {e}")
            raise

    try:
        if root_position_id is not None:
            # Строим дерево от указанного корня
            query = "SELECT * FROM positions WHERE id = ?"
            params = [root_position_id]
            
            # Если указан ID организации, добавляем фильтр
            if organization_id is not None:
                query = """
                    SELECT p.*
                    FROM positions p
                    JOIN staff s ON s.position_id = p.id
                    JOIN organizations o ON s.organization_id = o.id
                    WHERE p.id = ? AND o.id = ?
                """
                params.append(organization_id)
                
            cursor.execute(query, params)
            root_pos = cursor.fetchone()
            
            if not root_pos:
                if organization_id is not None:
                    raise HTTPException(status_code=404, detail=f"Корневая должность с ID {root_position_id} не найдена или не относится к организации с ID {organization_id}.")
                else:
                    raise HTTPException(status_code=404, detail=f"Корневая должность с ID {root_position_id} не найдена.")
            
            nodes.append({
                "id": f'pos-{root_pos["id"]}',
                "data": {
                    "label": root_pos['name'],
                    "attribute": root_pos['attribute'],
                    "db_id": root_pos["id"]
                },
                "position": {"x": 0, "y": 0}
            })
            visited_nodes.add(root_pos["id"])
            await build_hierarchy_tree_with_depth(db, root_pos["id"], nodes, edges, visited_nodes, 0, depth)
        else:
            # Строим полное дерево, начиная с должностей без руководителя (верхний уровень)
            query = """
                SELECT p.* 
                FROM positions p
                LEFT JOIN hierarchy_relations hr ON p.id = hr.subordinate_position_id AND hr.is_active = 1
                WHERE hr.superior_position_id IS NULL 
                   OR p.id NOT IN (SELECT subordinate_position_id FROM hierarchy_relations WHERE is_active = 1)
            """
            params = []
            
            # Если указан ID организации, добавляем фильтр
            if organization_id is not None:
                query = """
                    SELECT p.* 
                    FROM positions p
                    JOIN staff s ON s.position_id = p.id
                    JOIN organizations o ON s.organization_id = o.id
                    LEFT JOIN hierarchy_relations hr ON p.id = hr.subordinate_position_id AND hr.is_active = 1
                    WHERE (hr.superior_position_id IS NULL 
                       OR p.id NOT IN (SELECT subordinate_position_id FROM hierarchy_relations WHERE is_active = 1))
                       AND o.id = ?
                """
                params.append(organization_id)
                
            cursor.execute(query, params)
            top_level_positions = cursor.fetchall()

            if not top_level_positions:
                 message = "Не найдены должности верхнего уровня для построения полного дерева."
                 if organization_id is not None:
                     message += f" Для организации с ID {organization_id}."
                 logger.warning(message)
                 return {"nodes": [], "edges": []}


            for pos in top_level_positions:
                pos_id = pos['id']
                if pos_id not in visited_nodes: # Добавляем узел, только если его еще нет
                    nodes.append({
                        "id": f'pos-{pos_id}',
                        "data": {
                            "label": pos['name'],
                            "attribute": pos['attribute'],
                             "db_id": pos_id
                        },
                        "position": {"x": 0, "y": 0}
                    })
                    visited_nodes.add(pos_id)
                    await build_hierarchy_tree_with_depth(db, pos_id, nodes, edges, visited_nodes, 0, depth)
        
        return {"nodes": nodes, "edges": edges}

    except Exception as e:
        # Log the error message and traceback separately
        error_message = f"Ошибка при построении дерева организационной структуры: {e}"
        logger.error(error_message)
        logger.error(f"Traceback: {traceback.format_exc()}") # Log traceback separately
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при построении дерева")

# Маршруты для иерархических связей (hierarchy_relations)

@router.post("/hierarchy-relations/", response_model=HierarchyRelation, status_code=status.HTTP_201_CREATED, tags=["hierarchy"])
async def create_hierarchy_relation(
    relation: HierarchyRelationCreate,
    db: sqlite3.Connection = Depends(get_db)
):
    """Создать новую иерархическую связь между должностями."""
    cursor = db.cursor()
    
    # Проверяем существование должностей
    cursor.execute("SELECT id FROM positions WHERE id = ?", (relation.superior_position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Руководящая должность с ID {relation.superior_position_id} не найдена")
    
    cursor.execute("SELECT id FROM positions WHERE id = ?", (relation.subordinate_position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Подчиненная должность с ID {relation.subordinate_position_id} не найдена")
    
    # Проверяем, что не создаем цикл (должность не может быть руководителем самой себя)
    if relation.superior_position_id == relation.subordinate_position_id:
        raise HTTPException(status_code=400, detail="Должность не может быть руководителем самой себя")
    
    # Дополнительная проверка на циклы в иерархии
    # TODO: реализовать более сложную проверку для избежания циклов в графе иерархии
    
    try:
        cursor.execute("""
            INSERT INTO hierarchy_relations 
            (superior_position_id, subordinate_position_id, priority, is_active, description, extra_field1, extra_field2, extra_int1)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            relation.superior_position_id,
            relation.subordinate_position_id,
            relation.priority,
            1 if relation.is_active else 0,
            relation.description,
            relation.extra_field1,
            relation.extra_field2,
            relation.extra_int1
        ))
        db.commit()
        
        relation_id = cursor.lastrowid
        cursor.execute("SELECT * FROM hierarchy_relations WHERE id = ?", (relation_id,))
        created_relation = cursor.fetchone()
        
        return HierarchyRelation(**dict(created_relation))
    
    except sqlite3.IntegrityError as e:
        db.rollback()
        logger.error(f"Ошибка целостности БД при создании иерархической связи: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при создании иерархической связи: {e}")
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при создании иерархической связи: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/hierarchy-relations/", response_model=List[HierarchyRelationWithDetails], tags=["hierarchy"])
async def read_hierarchy_relations(
    superior_position_id: Optional[int] = Query(None, description="Фильтр по ID руководящей должности"),
    subordinate_position_id: Optional[int] = Query(None, description="Фильтр по ID подчиненной должности"),
    is_active: Optional[bool] = Query(None, description="Фильтр по статусу активности"),
    priority: Optional[int] = Query(None, description="Фильтр по приоритету"),
    skip: int = 0,
    limit: int = 100,
    db: sqlite3.Connection = Depends(get_db)
):
    """Получить список иерархических связей с фильтрацией."""
    cursor = db.cursor()
    
    query = """
        SELECT hr.*, 
            p1.name as superior_position_name, 
            p1.attribute as superior_position_attribute,
            p2.name as subordinate_position_name, 
            p2.attribute as subordinate_position_attribute
        FROM hierarchy_relations hr
        LEFT JOIN positions p1 ON hr.superior_position_id = p1.id
        LEFT JOIN positions p2 ON hr.subordinate_position_id = p2.id
        WHERE 1=1
    """
    params = []
    
    if superior_position_id is not None:
        query += " AND hr.superior_position_id = ?"
        params.append(superior_position_id)
    
    if subordinate_position_id is not None:
        query += " AND hr.subordinate_position_id = ?"
        params.append(subordinate_position_id)
    
    if is_active is not None:
        query += " AND hr.is_active = ?"
        params.append(1 if is_active else 0)
    
    if priority is not None:
        query += " AND hr.priority = ?"
        params.append(priority)
    
    query += " ORDER BY hr.priority, hr.id LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        
        for row in rows:
            try:
                relation = HierarchyRelationWithDetails(**dict(row))
                result.append(relation)
            except ValidationError as e:
                logger.warning(f"Ошибка валидации данных иерархической связи ID {row['id']}: {e}")
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении списка иерархических связей: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/hierarchy-relations/{relation_id}", response_model=HierarchyRelationWithDetails, tags=["hierarchy"])
async def read_hierarchy_relation(
    relation_id: int,
    db: sqlite3.Connection = Depends(get_db)
):
    """Получить информацию об иерархической связи по ID."""
    relation = await get_hierarchy_relation_with_details(db, relation_id)
    if not relation:
        raise HTTPException(status_code=404, detail="Иерархическая связь не найдена")
    return relation

@router.put("/hierarchy-relations/{relation_id}", response_model=HierarchyRelation, tags=["hierarchy"])
async def update_hierarchy_relation(
    relation_id: int,
    relation: HierarchyRelationCreate,
    db: sqlite3.Connection = Depends(get_db)
):
    """Обновить иерархическую связь."""
    cursor = db.cursor()
    
    # Проверяем существование связи
    cursor.execute("SELECT id FROM hierarchy_relations WHERE id = ?", (relation_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Иерархическая связь не найдена")
    
    # Проверяем существование должностей
    cursor.execute("SELECT id FROM positions WHERE id = ?", (relation.superior_position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Руководящая должность с ID {relation.superior_position_id} не найдена")
    
    cursor.execute("SELECT id FROM positions WHERE id = ?", (relation.subordinate_position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Подчиненная должность с ID {relation.subordinate_position_id} не найдена")
    
    # Проверяем, что не создаем цикл
    if relation.superior_position_id == relation.subordinate_position_id:
        raise HTTPException(status_code=400, detail="Должность не может быть руководителем самой себя")
    
    try:
        cursor.execute("""
            UPDATE hierarchy_relations SET
                superior_position_id = ?,
                subordinate_position_id = ?,
                priority = ?,
                is_active = ?,
                description = ?,
                extra_field1 = ?,
                extra_field2 = ?,
                extra_int1 = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            relation.superior_position_id,
            relation.subordinate_position_id,
            relation.priority,
            1 if relation.is_active else 0,
            relation.description,
            relation.extra_field1,
            relation.extra_field2,
            relation.extra_int1,
            relation_id
        ))
        db.commit()
        
        cursor.execute("SELECT * FROM hierarchy_relations WHERE id = ?", (relation_id,))
        updated_relation = cursor.fetchone()
        
        return HierarchyRelation(**dict(updated_relation))
    except sqlite3.IntegrityError as e:
        db.rollback()
        logger.error(f"Ошибка целостности БД при обновлении иерархической связи: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении иерархической связи: {e}")
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при обновлении иерархической связи: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.delete("/hierarchy-relations/{relation_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["hierarchy"])
async def delete_hierarchy_relation(
    relation_id: int,
    db: sqlite3.Connection = Depends(get_db)
):
    """Удалить иерархическую связь."""
    cursor = db.cursor()
    
    # Проверяем существование связи
    cursor.execute("SELECT id FROM hierarchy_relations WHERE id = ?", (relation_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Иерархическая связь не найдена")
    
    try:
        cursor.execute("DELETE FROM hierarchy_relations WHERE id = ?", (relation_id,))
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при удалении иерархической связи: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

# Маршруты для управления подразделениями (unit_management)

@router.post("/unit-management/", response_model=UnitManagement, status_code=status.HTTP_201_CREATED, tags=["hierarchy"])
async def create_unit_management(
    unit_management: UnitManagementCreate,
    db: sqlite3.Connection = Depends(get_db)
):
    """Создать новую связь между должностью и управляемой единицей (подразделением, отделом)."""
    cursor = db.cursor()
    
    # Проверяем существование должности
    cursor.execute("SELECT id FROM positions WHERE id = ?", (unit_management.position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Должность с ID {unit_management.position_id} не найдена")
    
    # Проверяем существование управляемой единицы в зависимости от её типа
    if unit_management.managed_type == "division":
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (unit_management.managed_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Подразделение с ID {unit_management.managed_id} не найдено")
    elif unit_management.managed_type == "section":
        cursor.execute("SELECT id FROM sections WHERE id = ?", (unit_management.managed_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Отдел с ID {unit_management.managed_id} не найден")
    else:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемый тип управляемой единицы: {unit_management.managed_type}")
    
    try:
        cursor.execute("""
            INSERT INTO unit_management 
            (position_id, managed_type, managed_id, is_active, description, extra_field1, extra_field2, extra_int1)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            unit_management.position_id,
            unit_management.managed_type,
            unit_management.managed_id,
            1 if unit_management.is_active else 0,
            unit_management.description,
            unit_management.extra_field1,
            unit_management.extra_field2,
            unit_management.extra_int1
        ))
        db.commit()
        
        management_id = cursor.lastrowid
        cursor.execute("SELECT * FROM unit_management WHERE id = ?", (management_id,))
        created_management = cursor.fetchone()
        
        return UnitManagement(**dict(created_management))
    
    except sqlite3.IntegrityError as e:
        db.rollback()
        logger.error(f"Ошибка целостности БД при создании связи управления: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при создании связи управления: {e}")
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при создании связи управления: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/unit-management/", response_model=List[UnitManagementWithDetails], tags=["hierarchy"])
async def read_unit_managements(
    position_id: Optional[int] = Query(None, description="Фильтр по ID управляющей должности"),
    managed_type: Optional[str] = Query(None, description="Фильтр по типу управляемой единицы ('division', 'section')"),
    managed_id: Optional[int] = Query(None, description="Фильтр по ID управляемой единицы"),
    is_active: Optional[bool] = Query(None, description="Фильтр по статусу активности"),
    skip: int = 0,
    limit: int = 100,
    db: sqlite3.Connection = Depends(get_db)
):
    """Получить список связей управления с фильтрацией."""
    cursor = db.cursor()
    
    query = """
        SELECT um.*, 
            p.name as position_name, 
            p.attribute as position_attribute,
            CASE 
                WHEN um.managed_type = 'division' THEN (SELECT name FROM divisions WHERE id = um.managed_id)
                WHEN um.managed_type = 'section' THEN (SELECT name FROM sections WHERE id = um.managed_id)
                ELSE NULL
            END as managed_name
        FROM unit_management um
        LEFT JOIN positions p ON um.position_id = p.id
        WHERE 1=1
    """
    params = []
    
    if position_id is not None:
        query += " AND um.position_id = ?"
        params.append(position_id)
    
    if managed_type is not None:
        query += " AND um.managed_type = ?"
        params.append(managed_type)
    
    if managed_id is not None:
        query += " AND um.managed_id = ?"
        params.append(managed_id)
    
    if is_active is not None:
        query += " AND um.is_active = ?"
        params.append(1 if is_active else 0)
    
    query += " ORDER BY um.id LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        
        for row in rows:
            try:
                management = UnitManagementWithDetails(**dict(row))
                result.append(management)
            except ValidationError as e:
                logger.warning(f"Ошибка валидации данных связи управления ID {row['id']}: {e}")
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении списка связей управления: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.get("/unit-management/{management_id}", response_model=UnitManagementWithDetails, tags=["hierarchy"])
async def read_unit_management(
    management_id: int,
    db: sqlite3.Connection = Depends(get_db)
):
    """Получить информацию о связи управления по ID."""
    management = await get_unit_management_with_details(db, management_id)
    if not management:
        raise HTTPException(status_code=404, detail="Связь управления не найдена")
    return management

@router.put("/unit-management/{management_id}", response_model=UnitManagement, tags=["hierarchy"])
async def update_unit_management(
    management_id: int,
    unit_management: UnitManagementCreate,
    db: sqlite3.Connection = Depends(get_db)
):
    """Обновить связь управления."""
    cursor = db.cursor()
    
    # Проверяем существование связи
    cursor.execute("SELECT id FROM unit_management WHERE id = ?", (management_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Связь управления не найдена")
    
    # Проверяем существование должности
    cursor.execute("SELECT id FROM positions WHERE id = ?", (unit_management.position_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail=f"Должность с ID {unit_management.position_id} не найдена")
    
    # Проверяем существование управляемой единицы в зависимости от её типа
    if unit_management.managed_type == "division":
        cursor.execute("SELECT id FROM divisions WHERE id = ?", (unit_management.managed_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Подразделение с ID {unit_management.managed_id} не найдено")
    elif unit_management.managed_type == "section":
        cursor.execute("SELECT id FROM sections WHERE id = ?", (unit_management.managed_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Отдел с ID {unit_management.managed_id} не найден")
    else:
        raise HTTPException(status_code=400, detail=f"Неподдерживаемый тип управляемой единицы: {unit_management.managed_type}")
    
    try:
        cursor.execute("""
            UPDATE unit_management SET
                position_id = ?,
                managed_type = ?,
                managed_id = ?,
                is_active = ?,
                description = ?,
                extra_field1 = ?,
                extra_field2 = ?,
                extra_int1 = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            unit_management.position_id,
            unit_management.managed_type,
            unit_management.managed_id,
            1 if unit_management.is_active else 0,
            unit_management.description,
            unit_management.extra_field1,
            unit_management.extra_field2,
            unit_management.extra_int1,
            management_id
        ))
        db.commit()
        
        cursor.execute("SELECT * FROM unit_management WHERE id = ?", (management_id,))
        updated_management = cursor.fetchone()
        
        return UnitManagement(**dict(updated_management))
    except sqlite3.IntegrityError as e:
        db.rollback()
        logger.error(f"Ошибка целостности БД при обновлении связи управления: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении связи управления: {e}")
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при обновлении связи управления: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@router.delete("/unit-management/{management_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["hierarchy"])
async def delete_unit_management(
    management_id: int,
    db: sqlite3.Connection = Depends(get_db)
):
    """Удалить связь управления."""
    cursor = db.cursor()
    
    # Проверяем существование связи
    cursor.execute("SELECT id FROM unit_management WHERE id = ?", (management_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Связь управления не найдена")
    
    try:
        cursor.execute("DELETE FROM unit_management WHERE id = ?", (management_id,))
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        logger.error(f"Ошибка при удалении связи управления: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера") 