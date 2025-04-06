import api from './api';

// Интерфейсы для работы с API сотрудников
export interface StaffMember {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone?: string;
  position: string;
  description?: string;
  is_active: boolean;
  organization_id: number;
  division_id?: number;
  location_id?: number;
  created_at: string;
  updated_at: string;
}

export interface StaffCreateDTO {
  email: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone?: string;
  position: string;
  description?: string;
  is_active?: boolean;
  organization_id: number;
  division_id?: number;
  location_id?: number;
}

export interface StaffUpdateDTO {
  email?: string;
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  phone?: string;
  position?: string;
  description?: string;
  is_active?: boolean;
  organization_id?: number;
  division_id?: number;
  location_id?: number;
}

export interface StaffFilter {
  organization_id?: number;
  legal_entity_id?: number;
  location_id?: number;
  division?: string;
  skip?: number;
  limit?: number;
}

const staffService = {
  /**
   * Получить всех сотрудников с возможностью фильтрации
   */
  async getStaff(filters: StaffFilter = {}): Promise<StaffMember[]> {
    try {
      const { data } = await api.get('/staff', { params: filters });
      return data;
    } catch (error) {
      console.error('Ошибка при получении списка сотрудников:', error);
      throw error;
    }
  },

  /**
   * Получить иерархию сотрудников
   */
  async getStaffHierarchy(): Promise<StaffMember[]> {
    try {
      const { data } = await api.get('/staff/hierarchy');
      return data;
    } catch (error) {
      console.error('Ошибка при получении иерархии сотрудников:', error);
      throw error;
    }
  },

  /**
   * Получить сотрудников по юридическому лицу
   */
  async getStaffByLegalEntity(legalEntityId: number, skip = 0, limit = 100): Promise<StaffMember[]> {
    try {
      const { data } = await api.get(`/staff/by-legal-entity/${legalEntityId}`, {
        params: { skip, limit }
      });
      return data;
    } catch (error) {
      console.error(`Ошибка при получении сотрудников по юрлицу ${legalEntityId}:`, error);
      throw error;
    }
  },

  /**
   * Получить сотрудников по локации
   */
  async getStaffByLocation(locationId: number, skip = 0, limit = 100): Promise<StaffMember[]> {
    try {
      const { data } = await api.get(`/staff/by-location/${locationId}`, {
        params: { skip, limit }
      });
      return data;
    } catch (error) {
      console.error(`Ошибка при получении сотрудников по локации ${locationId}:`, error);
      throw error;
    }
  },

  /**
   * Создать нового сотрудника
   */
  async createStaff(staffData: StaffCreateDTO): Promise<StaffMember> {
    try {
      const { data } = await api.post('/staff', staffData);
      return data;
    } catch (error) {
      console.error('Ошибка при создании сотрудника:', error);
      throw error;
    }
  },

  /**
   * Получить сотрудника по ID
   */
  async getStaffById(id: number): Promise<StaffMember> {
    try {
      const { data } = await api.get(`/staff/${id}`);
      return data;
    } catch (error) {
      console.error(`Ошибка при получении сотрудника с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Обновить данные сотрудника
   */
  async updateStaff(id: number, staffData: StaffUpdateDTO): Promise<StaffMember> {
    try {
      const { data } = await api.put(`/staff/${id}`, staffData);
      return data;
    } catch (error) {
      console.error(`Ошибка при обновлении сотрудника с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Удалить сотрудника
   */
  async deleteStaff(id: number): Promise<void> {
    try {
      await api.delete(`/staff/${id}`);
    } catch (error) {
      console.error(`Ошибка при удалении сотрудника с ID ${id}:`, error);
      throw error;
    }
  }
};

export default staffService; 