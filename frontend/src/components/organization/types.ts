export type EntityType = 'business' | 'legal' | 'territorial';

// Типы для связей
export type RelationType = 'manager' | 'department' | 'functional' | 'other';

// Тип для комментариев
export interface Comment {
  text: string;
  completed: boolean;
  date: string;
}

// Тип узла (сотрудник или подразделение)
export interface EntityNode {
  id: string;
  name: string;
  type: string;
  position?: string;
  manager?: string;
  staff?: string;
  avatar?: string; // URL аватарки сотрудника
  comments?: Comment[]; // Комментарии к узлу со статусом выполнения
}

// Тип связи между узлами
export interface EntityRelation {
  id: string;
  from: string;
  to: string;
  type: RelationType;
  label?: string;
} 