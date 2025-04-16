import api from './api';
import { UnitManagement, UnitManagementCreate } from '../types/hierarchy';

const API_URL = '/hierarchy/unit-management'; // Используем префикс, добавленный в full_api.py

/**
 * Получить все связи управления.
 * TODO: Добавить параметры для фильтрации (position_id, managed_type, managed_id).
 */
export const getAllUnitManagements = async (): Promise<UnitManagement[]> => {
  const response = await api.get<UnitManagement[]>(`${API_URL}/`);
  return response.data;
};

/**
 * Получить связь управления по ID.
 * @param id ID связи
 */
export const getUnitManagementById = async (id: number): Promise<UnitManagement> => {
  const response = await api.get<UnitManagement>(`${API_URL}/${id}`);
  return response.data;
};

/**
 * Создать новую связь управления.
 * @param data Данные для создания связи
 */
export const createUnitManagement = async (data: UnitManagementCreate): Promise<UnitManagement> => {
  const response = await api.post<UnitManagement>(`${API_URL}/`, data);
  return response.data;
};

/**
 * Обновить связь управления.
 * @param id ID связи для обновления
 * @param data Новые данные для связи
 */
export const updateUnitManagement = async (id: number, data: UnitManagementCreate): Promise<UnitManagement> => {
  const response = await api.put<UnitManagement>(`${API_URL}/${id}`, data);
  return response.data;
};

/**
 * Удалить связь управления.
 * @param id ID связи для удаления
 */
export const deleteUnitManagement = async (id: number): Promise<void> => {
  await api.delete(`${API_URL}/${id}`);
}; 