/**
 * Типы данных для иерархических связей и управления.
 * Соответствуют Pydantic моделям на бэкенде.
 */

/**
 * Базовый тип для иерархической связи.
 */
export interface HierarchyRelationBase {
  superior_position_id: number;
  subordinate_position_id: number;
  priority: number;
}

/**
 * Тип для создания новой иерархической связи.
 */
export interface HierarchyRelationCreate extends HierarchyRelationBase {}

/**
 * Полный тип иерархической связи, включая ID.
 */
export interface HierarchyRelation extends HierarchyRelationBase {
  id: number;
}

/**
 * Базовый тип для связи управления подразделением/отделом.
 */
export interface UnitManagementBase {
  position_id: number;
  managed_type: 'division' | 'section'; // Или другие типы, если появятся
  managed_id: number;
}

/**
 * Тип для создания новой связи управления.
 */
export interface UnitManagementCreate extends UnitManagementBase {}

/**
 * Полный тип связи управления, включая ID.
 */
export interface UnitManagement extends UnitManagementBase {
  id: number;
} 