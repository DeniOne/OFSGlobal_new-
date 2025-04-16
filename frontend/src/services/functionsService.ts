import api from './api';
import { 
    Function, 
    FunctionCreateDTO, 
    FunctionFilters,
    FunctionalAssignment,
    FunctionalAssignmentCreateDTO,
    FunctionalAssignmentFilters
} from '../types/function';

/**
 * Сервис для работы с функциями и функциональными назначениями
 */
const functionsService = {
    // =========== Методы для работы с функциями ===========
    
    /**
     * Получить список функций
     */
    async getFunctions(filters?: FunctionFilters): Promise<Function[]> {
        try {
            // Формируем параметры запроса из фильтров
            const params = new URLSearchParams();
            if (filters) {
                if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
                if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
                if (filters.is_active !== undefined) params.append('is_active', filters.is_active.toString());
            }

            const { data } = await api.get(`/functions/?${params.toString()}`);
            return data;
        } catch (error) {
            console.error('Ошибка при получении функций:', error);
            throw error;
        }
    },

    /**
     * Получить функцию по ID
     */
    async getFunction(id: number): Promise<Function> {
        try {
            const { data } = await api.get(`/functions/${id}`);
            return data;
        } catch (error) {
            console.error(`Ошибка при получении функции с ID ${id}:`, error);
            throw error;
        }
    },

    /**
     * Создать новую функцию
     */
    async createFunction(functionData: FunctionCreateDTO): Promise<Function> {
        try {
            const { data } = await api.post('/functions/', functionData);
            return data;
        } catch (error) {
            console.error('Ошибка при создании функции:', error);
            throw error;
        }
    },

    /**
     * Обновить существующую функцию
     */
    async updateFunction(id: number, functionData: FunctionCreateDTO): Promise<Function> {
        try {
            const { data } = await api.put(`/functions/${id}`, functionData);
            return data;
        } catch (error) {
            console.error(`Ошибка при обновлении функции с ID ${id}:`, error);
            throw error;
        }
    },

    /**
     * Удалить функцию
     */
    async deleteFunction(id: number): Promise<void> {
        try {
            await api.delete(`/functions/${id}`);
        } catch (error) {
            console.error(`Ошибка при удалении функции с ID ${id}:`, error);
            throw error;
        }
    },

    // =========== Методы для работы с функциональными назначениями ===========
    
    /**
     * Получить список функциональных назначений
     */
    async getFunctionalAssignments(filters?: FunctionalAssignmentFilters): Promise<FunctionalAssignment[]> {
        try {
            // Формируем параметры запроса из фильтров
            const params = new URLSearchParams();
            if (filters) {
                if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
                if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
                if (filters.position_id !== undefined) params.append('position_id', filters.position_id.toString());
                if (filters.function_id !== undefined) params.append('function_id', filters.function_id.toString());
                if (filters.is_primary !== undefined) params.append('is_primary', filters.is_primary.toString());
            }

            const { data } = await api.get(`/functional-assignments/?${params.toString()}`);
            return data;
        } catch (error) {
            console.error('Ошибка при получении функциональных назначений:', error);
            throw error;
        }
    },

    /**
     * Получить функциональные назначения по ID должности
     */
    async getFunctionalAssignmentsByPosition(positionId: number): Promise<FunctionalAssignment[]> {
        try {
            const { data } = await api.get(`/functional-assignments/?position_id=${positionId}`);
            return data;
        } catch (error) {
            console.error(`Ошибка при получении функциональных назначений для должности с ID ${positionId}:`, error);
            throw error;
        }
    },

    /**
     * Получить функциональные назначения по ID функции
     */
    async getFunctionalAssignmentsByFunction(functionId: number): Promise<FunctionalAssignment[]> {
        try {
            const { data } = await api.get(`/functional-assignments/?function_id=${functionId}`);
            return data;
        } catch (error) {
            console.error(`Ошибка при получении функциональных назначений для функции с ID ${functionId}:`, error);
            throw error;
        }
    },

    /**
     * Получить функциональное назначение по ID
     */
    async getFunctionalAssignment(id: number): Promise<FunctionalAssignment> {
        try {
            const { data } = await api.get(`/functional-assignments/${id}`);
            return data;
        } catch (error) {
            console.error(`Ошибка при получении функционального назначения с ID ${id}:`, error);
            throw error;
        }
    },

    /**
     * Создать новое функциональное назначение
     */
    async createFunctionalAssignment(assignmentData: FunctionalAssignmentCreateDTO): Promise<FunctionalAssignment> {
        try {
            const { data } = await api.post('/functional-assignments/', assignmentData);
            return data;
        } catch (error) {
            console.error('Ошибка при создании функционального назначения:', error);
            throw error;
        }
    },

    /**
     * Обновить существующее функциональное назначение
     */
    async updateFunctionalAssignment(id: number, assignmentData: FunctionalAssignmentCreateDTO): Promise<FunctionalAssignment> {
        try {
            const { data } = await api.put(`/functional-assignments/${id}`, assignmentData);
            return data;
        } catch (error) {
            console.error(`Ошибка при обновлении функционального назначения с ID ${id}:`, error);
            throw error;
        }
    },

    /**
     * Удалить функциональное назначение
     */
    async deleteFunctionalAssignment(id: number): Promise<void> {
        try {
            await api.delete(`/functional-assignments/${id}`);
        } catch (error) {
            console.error(`Ошибка при удалении функционального назначения с ID ${id}:`, error);
            throw error;
        }
    }
};

export default functionsService; 