import { useState, useCallback } from 'react';
import positionsService, { 
  PositionCreateDTO, 
  PositionUpdateDTO 
} from '../services/positionsService';
import { Position } from '../types/organization';

interface PositionFilter {
  division_id?: number;
  section_id?: number;
  is_active?: boolean;
}

interface UsePositionsResult {
  positions: Position[];
  loading: boolean;
  error: Error | null;
  fetchPositions: (filters?: PositionFilter) => Promise<Position[]>;
  fetchPositionById: (id: number) => Promise<Position | undefined>;
  getPositionById: (id: number) => Position | undefined;
  addPosition: (position: PositionCreateDTO) => Promise<Position | undefined>;
  editPosition: (id: number, position: PositionUpdateDTO) => Promise<Position | undefined>;
  removePosition: (id: number) => Promise<boolean>;
}

export const usePositions = (): UsePositionsResult => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  // Получение всех должностей с возможностью фильтрации
  const fetchPositions = useCallback(async (filters?: PositionFilter): Promise<Position[]> => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Когда бэкенд будет поддерживать фильтрацию, нужно будет передать параметры
      const data = await positionsService.getAllPositions();
      
      // Если передан фильтр, применяем его на фронтенде
      let filteredData = [...data];
      if (filters) {
        if (filters.division_id !== undefined) {
          filteredData = filteredData.filter(p => p.division_id === filters.division_id);
        }
        if (filters.section_id !== undefined) {
          filteredData = filteredData.filter(p => p.section_id === filters.section_id);
        }
        if (filters.is_active !== undefined) {
          filteredData = filteredData.filter(p => p.is_active === filters.is_active);
        }
      }
      
      setPositions(filteredData);
      return filteredData;
    } catch (err) {
      console.error('Ошибка при загрузке должностей:', err);
      setError(err instanceof Error ? err : new Error('Неизвестная ошибка при загрузке должностей'));
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Получение должности по ID из API
  const fetchPositionById = useCallback(async (id: number): Promise<Position | undefined> => {
    try {
      setLoading(true);
      setError(null);
      const data = await positionsService.getPositionById(id);
      
      // Обновляем кэш должностей, добавляя или заменяя должность
      setPositions(prevPositions => {
        const index = prevPositions.findIndex(p => p.id === id);
        if (index >= 0) {
          const newPositions = [...prevPositions];
          newPositions[index] = data;
          return newPositions;
        } else {
          return [...prevPositions, data];
        }
      });
      
      return data;
    } catch (err) {
      console.error(`Ошибка при загрузке должности с ID ${id}:`, err);
      setError(err instanceof Error ? err : new Error(`Ошибка при загрузке должности с ID ${id}`));
      return undefined;
    } finally {
      setLoading(false);
    }
  }, []);

  // Получение должности по ID из локально загруженных данных
  const getPositionById = useCallback((id: number): Position | undefined => {
    return positions.find(pos => pos.id === id);
  }, [positions]);

  // Создание новой должности
  const addPosition = useCallback(async (position: PositionCreateDTO): Promise<Position | undefined> => {
    try {
      setLoading(true);
      setError(null);
      const newPosition = await positionsService.createPosition(position);
      setPositions(prev => [...prev, newPosition]);
      return newPosition;
    } catch (err) {
      console.error('Ошибка при создании должности:', err);
      setError(err instanceof Error ? err : new Error('Ошибка при создании должности'));
      return undefined;
    } finally {
      setLoading(false);
    }
  }, []);

  // Обновление должности
  const editPosition = useCallback(async (id: number, position: PositionUpdateDTO): Promise<Position | undefined> => {
    try {
      setLoading(true);
      setError(null);
      const updatedPosition = await positionsService.updatePosition(id, position);
      
      setPositions(prev => 
        prev.map(p => p.id === id ? updatedPosition : p)
      );
      
      return updatedPosition;
    } catch (err) {
      console.error(`Ошибка при обновлении должности с ID ${id}:`, err);
      setError(err instanceof Error ? err : new Error(`Ошибка при обновлении должности с ID ${id}`));
      return undefined;
    } finally {
      setLoading(false);
    }
  }, []);

  // Удаление должности
  const removePosition = useCallback(async (id: number): Promise<boolean> => {
    try {
      setLoading(true);
      setError(null);
      await positionsService.deletePosition(id);
      
      setPositions(prev => prev.filter(p => p.id !== id));
      
      return true;
    } catch (err) {
      console.error(`Ошибка при удалении должности с ID ${id}:`, err);
      setError(err instanceof Error ? err : new Error(`Ошибка при удалении должности с ID ${id}`));
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    positions,
    loading,
    error,
    fetchPositions,
    fetchPositionById,
    getPositionById,
    addPosition,
    editPosition,
    removePosition
  };
};

export default usePositions; 