import api from './api';
import { Position } from '../types/organization';
import { Function, FunctionalAssignment, FunctionalAssignmentCreateDTO } from '../types/function';
import functionsService from './functionsService';

// DTO для создания и обновления должностей
export interface PositionCreateDTO {
  name: string;
  description?: string | null;
  is_active?: boolean;
  attribute: string;
  division_id?: number | null;
  section_id?: number | null;
  function_ids?: number[]; // Список ID функций, связанных с должностью
}

export interface PositionUpdateDTO extends Partial<PositionCreateDTO> {}

const API_URL = '/positions'; // Путь к API должностей

const positionsService = {
  /**
   * Получить все должности.
   * @param filters Параметры фильтрации (например, division_id, is_active, ...)
   */
  async getAllPositions(filters?: Record<string, any>): Promise<Position[]> {
    try {
      // Формируем строку запроса из фильтров
      const queryParams = filters 
        ? '?' + new URLSearchParams(filters as Record<string, string>).toString()
        : '';
      
      const response = await api.get<Position[]>(`${API_URL}/${queryParams}`);
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении списка должностей:', error);
      throw error;
    }
  },

  /**
   * Получить должность по ID.
   */
  async getPositionById(id: number): Promise<Position> {
    try {
      const response = await api.get<Position>(`${API_URL}/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Ошибка при получении должности с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Создать новую должность.
   */
  async createPosition(positionData: PositionCreateDTO): Promise<Position> {
    try {
      const response = await api.post<Position>(`${API_URL}/`, positionData);
      return response.data;
    } catch (error) {
      console.error('Ошибка при создании должности:', error);
      throw error;
    }
  },

  /**
   * Обновить данные должности.
   */
  async updatePosition(id: number, positionData: PositionUpdateDTO): Promise<Position> {
    try {
      const response = await api.put<Position>(`${API_URL}/${id}`, positionData);
      return response.data;
    } catch (error) {
      console.error(`Ошибка при обновлении должности с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Удалить должность.
   */
  async deletePosition(id: number): Promise<void> {
    try {
      await api.delete(`${API_URL}/${id}`);
    } catch (error) {
      console.error(`Ошибка при удалении должности с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Получить функциональные назначения для должности.
   */
  async getPositionFunctionalAssignments(positionId: number): Promise<FunctionalAssignment[]> {
    return functionsService.getFunctionalAssignmentsByPosition(positionId);
  },

  /**
   * Добавить функциональное назначение для должности.
   */
  async addFunctionToPosition(positionId: number, functionId: number, isMain: boolean = false): Promise<FunctionalAssignment> {
    const assignmentData: FunctionalAssignmentCreateDTO = {
      position_id: positionId,
      function_id: functionId,
      is_primary: isMain
    };
    return functionsService.createFunctionalAssignment(assignmentData);
  },

  /**
   * Удалить функциональное назначение.
   */
  async removeFunctionFromPosition(assignmentId: number): Promise<void> {
    return functionsService.deleteFunctionalAssignment(assignmentId);
  },

  /**
   * Обновить функциональное назначение.
   */
  async updatePositionFunction(assignmentId: number, data: Partial<FunctionalAssignmentCreateDTO>): Promise<FunctionalAssignment> {
    // Получаем текущие данные
    const currentAssignment = await functionsService.getFunctionalAssignment(assignmentId);
    
    // Объединяем с новыми данными
    const updateData: FunctionalAssignmentCreateDTO = {
      position_id: data.position_id ?? currentAssignment.position_id,
      function_id: data.function_id ?? currentAssignment.function_id,
      percentage: data.percentage ?? currentAssignment.percentage,
      is_primary: data.is_primary ?? currentAssignment.is_primary
    };
    
    return functionsService.updateFunctionalAssignment(assignmentId, updateData);
  }
};

export default positionsService; 