import api from './api';
import { MarkerType } from 'reactflow';

// Типы данных для узлов и ребер (соответствуют формату из API)
export interface OrgTreeNode {
  id: string;
  type?: string;
  data: {
    label: string;
    attribute: string;
    db_id: number;
    staff?: {
      id: number;
      name: string;
      position?: string;
      email?: string;
    }[];
  };
  position: {
    x: number;
    y: number;
  };
}

export interface OrgTreeEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  style?: Record<string, any>;
  markerEnd?: {
    type: MarkerType;
  };
}

export interface OrgTreeResponse {
  nodes: OrgTreeNode[];
  edges: OrgTreeEdge[];
}

// Параметры для запроса
export interface OrgTreeParams {
  root_position_id?: number; // ID корневой должности для построения частичного дерева
  organization_id?: number; // ID организации для фильтрации
  depth?: number; // Максимальная глубина дерева
}

// Сервис для работы с API организационной структуры
const orgTreeService = {
  /**
   * Получает организационную структуру в виде узлов и ребер,
   * готовых для отображения в react-flow
   * 
   * @param params Параметры запроса:
   *   - root_position_id - ID корневой должности для построения частичного дерева
   *   - organization_id - ID организации для фильтрации должностей
   *   - depth - Максимальная глубина дерева (0 - только корневой узел)
   */
  async getOrgTree(params: OrgTreeParams = {}): Promise<OrgTreeResponse> {
    try {
      const response = await api.get('/org-structure/hierarchy-flow', { params });
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении дерева организационной структуры:', error);
      throw error;
    }
  }
};

export default orgTreeService; 