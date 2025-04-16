import { useState, useCallback } from 'react';
import staffService, { StaffMember } from '../services/staffService';

interface UseStaffResult {
  staff: StaffMember[];
  staffByPosition: Record<number, StaffMember[]>;
  loading: boolean;
  error: Error | null;
  fetchStaff: (filters?: any) => Promise<StaffMember[]>;
  fetchStaffByPosition: (positionId: number) => Promise<StaffMember[]>;
  fetchStaffByPositions: (positionIds: number[]) => Promise<Record<number, StaffMember[]>>;
}

export const useStaff = (): UseStaffResult => {
  const [staff, setStaff] = useState<StaffMember[]>([]);
  const [staffByPosition, setStaffByPosition] = useState<Record<number, StaffMember[]>>({});
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  // Получить сотрудников с применением фильтров
  const fetchStaff = useCallback(async (filters = {}) => {
    try {
      setLoading(true);
      setError(null);
      const data = await staffService.getStaff(filters);
      setStaff(data);
      return data;
    } catch (err) {
      console.error('Ошибка при загрузке сотрудников:', err);
      setError(err instanceof Error ? err : new Error('Неизвестная ошибка при загрузке сотрудников'));
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Получить сотрудников по ID должности
  const fetchStaffByPosition = useCallback(async (positionId: number): Promise<StaffMember[]> => {
    try {
      setLoading(true);
      setError(null);
      const data = await staffService.getStaffByPosition(positionId);
      
      // Обновляем состояние только для этой должности
      setStaffByPosition(prev => ({
        ...prev,
        [positionId]: data
      }));
      
      return data;
    } catch (err) {
      console.error(`Ошибка при загрузке сотрудников по должности ${positionId}:`, err);
      setError(err instanceof Error ? err : new Error(`Ошибка при загрузке сотрудников по должности ${positionId}`));
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  // Получить сотрудников по массиву ID должностей
  const fetchStaffByPositions = useCallback(async (positionIds: number[]): Promise<Record<number, StaffMember[]>> => {
    try {
      setLoading(true);
      setError(null);
      const data = await staffService.getStaffForOrgChart(positionIds);
      setStaffByPosition(prev => ({
        ...prev,
        ...data
      }));
      return data;
    } catch (err) {
      console.error('Ошибка при загрузке сотрудников по должностям:', err);
      setError(err instanceof Error ? err : new Error('Ошибка при загрузке сотрудников по должностям'));
      return {};
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    staff,
    staffByPosition,
    loading,
    error,
    fetchStaff,
    fetchStaffByPosition,
    fetchStaffByPositions
  };
};

export default useStaff; 