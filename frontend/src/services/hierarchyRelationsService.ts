import api from './api';
import { HierarchyRelation, HierarchyRelationCreate } from '../types/hierarchy';

const API_URL = '/hierarchy/hierarchy-relations'; // Используем префикс, добавленный в full_api.py

/**
 * Получить все иерархические связи.
 * TODO: Добавить параметры для фильтрации (superior_id, subordinate_id).
 */
export const getAllHierarchyRelations = async (): Promise<HierarchyRelation[]> => {
  const response = await api.get<HierarchyRelation[]>(`${API_URL}/`);
  return response.data;
};

/**
 * Получить иерархическую связь по ID.
 * @param id ID связи
 */
export const getHierarchyRelationById = async (id: number): Promise<HierarchyRelation> => {
  const response = await api.get<HierarchyRelation>(`${API_URL}/${id}`);
  return response.data;
};

/**
 * Создать новую иерархическую связь.
 * @param data Данные для создания связи
 */
export const createHierarchyRelation = async (data: HierarchyRelationCreate): Promise<HierarchyRelation> => {
  const response = await api.post<HierarchyRelation>(`${API_URL}/`, data);
  return response.data;
};

/**
 * Обновить иерархическую связь.
 * @param id ID связи для обновления
 * @param data Новые данные для связи
 */
export const updateHierarchyRelation = async (id: number, data: HierarchyRelationCreate): Promise<HierarchyRelation> => {
  const response = await api.put<HierarchyRelation>(`${API_URL}/${id}`, data);
  return response.data;
};

/**
 * Удалить иерархическую связь.
 * @param id ID связи для удаления
 */
export const deleteHierarchyRelation = async (id: number): Promise<void> => {
  await api.delete(`${API_URL}/${id}`);
}; 