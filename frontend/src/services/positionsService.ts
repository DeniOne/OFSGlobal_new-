import api from './api';

// TODO: Определить полный TypeScript тип для Position, если его еще нет
// Вероятно, он должен быть в src/types/index.ts или создать src/types/position.ts
export interface Position {
  id: number;
  name: string;
  description?: string | null;
  is_active: boolean;
  attribute: string; // Должен быть Enum тип, как на бэке
  division_id?: number | null;
  section_id?: number | null;
  // Добавить другие поля, если они есть (created_at, updated_at)
}

const API_URL = '/positions'; // Путь к API должностей

/**
 * Получить все должности.
 * TODO: Добавить параметры для фильтрации.
 */
export const getAllPositions = async (): Promise<Position[]> => {
  const response = await api.get<Position[]>(`${API_URL}/`);
  return response.data;
};

// TODO: Добавить другие функции по мере необходимости (getById, create, update, delete) 