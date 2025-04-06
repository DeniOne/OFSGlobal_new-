import api from './api';

// Интерфейсы для работы с API подразделений
export interface Division {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  organization_id: number;
  parent_id?: number;
  created_at: string;
  updated_at: string;
}

export interface DivisionCreateDTO {
  name: string;
  code: string;
  description?: string;
  is_active?: boolean;
  organization_id: number;
  parent_id?: number;
}

export interface DivisionUpdateDTO {
  name?: string;
  code?: string;
  description?: string;
  is_active?: boolean;
  organization_id?: number;
  parent_id?: number;
}

export interface DivisionFilter {
  organization_id?: number;
  parent_id?: number;
  include_inactive?: boolean;
  skip?: number;
  limit?: number;
}

const divisionService = {
  /**
   * Получить список подразделений с возможностью фильтрации
   */
  async getDivisions(filters: DivisionFilter = {}): Promise<Division[]> {
    try {
      const { data } = await api.get('/divisions', { params: filters });
      return data;
    } catch (error) {
      console.error('Ошибка при получении списка подразделений:', error);
      throw error;
    }
  },

  /**
   * Получить подразделение по ID
   */
  async getDivisionById(id: number): Promise<Division> {
    try {
      const { data } = await api.get(`/divisions/${id}`);
      return data;
    } catch (error) {
      console.error(`Ошибка при получении подразделения с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Создать новое подразделение
   */
  async createDivision(divisionData: DivisionCreateDTO): Promise<Division> {
    try {
      const { data } = await api.post('/divisions', divisionData);
      return data;
    } catch (error) {
      console.error('Ошибка при создании подразделения:', error);
      throw error;
    }
  },

  /**
   * Обновить подразделение
   */
  async updateDivision(id: number, divisionData: DivisionUpdateDTO): Promise<Division> {
    try {
      const { data } = await api.put(`/divisions/${id}`, divisionData);
      return data;
    } catch (error) {
      console.error(`Ошибка при обновлении подразделения с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Удалить подразделение
   */
  async deleteDivision(id: number): Promise<void> {
    try {
      await api.delete(`/divisions/${id}`);
    } catch (error) {
      console.error(`Ошибка при удалении подразделения с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Получить дочерние подразделения
   */
  async getChildDivisions(parentId: number): Promise<Division[]> {
    try {
      const { data } = await api.get('/divisions', { 
        params: { parent_id: parentId } 
      });
      return data;
    } catch (error) {
      console.error(`Ошибка при получении дочерних подразделений для ID ${parentId}:`, error);
      throw error;
    }
  }
};

export default divisionService; 