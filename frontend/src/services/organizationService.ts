import api from './api';
import { EntityNode, EntityRelation, RelationType } from '../components/organization/types';

// Интерфейсы для данных с API
interface OrganizationDTO {
  id: number;
  name: string;
  description?: string;
  parent_id?: number | null;
  org_type: string;
  is_active: boolean;
}

interface DivisionDTO {
  id: number;
  name: string;
  code: string;
  description?: string;
  parent_id: number | null;
  level: number;
  is_active: boolean;
}

interface StaffDTO {
  id: number;
  first_name: string;
  last_name: string;
  middle_name?: string;
  position?: string;
  email?: string;
  phone?: string;
  division_id?: number;
  organization_id?: number;
  manager_id?: number | null;
  avatar_url?: string;
  is_active: boolean;
}

interface StaffRelationDTO {
  id: number;
  manager_id: number;
  subordinate_id: number;
  relation_type: string;
  description?: string;
}

// Функции конвертации данных из API в формат для ReactFlow
const mapOrganizationToEntityNode = (org: OrganizationDTO): EntityNode => ({
  id: org.id.toString(),
  name: org.name,
  type: org.org_type.toLowerCase(),
  // Другие поля будут заполняться при необходимости
});

const mapDivisionToEntityNode = (division: DivisionDTO): EntityNode => ({
  id: `div_${division.id}`,
  name: division.name,
  type: 'business',
  position: division.code,
  // Другие поля будут заполняться при необходимости
});

const mapStaffToEntityNode = (staff: StaffDTO, position?: string): EntityNode => ({
  id: `staff_${staff.id}`,
  name: `${staff.last_name} ${staff.first_name[0]}.${staff.middle_name ? ' ' + staff.middle_name[0] + '.' : ''}`,
  type: 'staff',
  position: position || staff.position || '',
  avatar: staff.avatar_url,
  // Другие поля будут заполняться при необходимости
});

const mapStaffRelationToEntityRelation = (relation: StaffRelationDTO): EntityRelation => ({
  id: relation.id.toString(),
  from: `staff_${relation.manager_id}`,
  to: `staff_${relation.subordinate_id}`,
  type: relation.relation_type.toLowerCase() as RelationType,
});

// Сервис для работы с организационной структурой
const organizationService = {
  // Получение бизнес-структуры
  async getBusinessStructure(): Promise<{ nodes: EntityNode[]; edges: EntityRelation[] }> {
    try {
      // Получаем отделы
      const divisionsResponse = await api.get('/divisions');
      const divisions: DivisionDTO[] = divisionsResponse.data;
      
      // Получаем сотрудников
      const staffResponse = await api.get('/staff');
      const staffList: StaffDTO[] = staffResponse.data;
      
      // Получаем связи
      const relationsResponse = await api.get('/functional-relations');
      const relations: StaffRelationDTO[] = relationsResponse.data;
      
      // Маппим отделы в узлы
      const divisionNodes = divisions.map(mapDivisionToEntityNode);
      
      // Маппим сотрудников в узлы
      const staffNodes = staffList.map(staff => {
        // Находим отдел сотрудника
        const division = staff.division_id 
          ? divisions.find(d => d.id === staff.division_id) 
          : undefined;
        
        // Находим руководителя сотрудника
        const manager = staff.manager_id 
          ? staffList.find(s => s.id === staff.manager_id) 
          : undefined;
        
        return mapStaffToEntityNode(staff, division?.name);
      });
      
      // Объединяем узлы
      const nodes = [...divisionNodes, ...staffNodes];
      
      // Создаем связи между отделами и между сотрудниками
      const divisionEdges = divisions
        .filter(d => d.parent_id !== null)
        .map(d => ({
          id: `div_edge_${d.id}`,
          from: `div_${d.parent_id}`,
          to: `div_${d.id}`,
          type: 'department' as RelationType
        }));
      
      // Маппим отношения в связи
      const staffEdges = relations.map(mapStaffRelationToEntityRelation);
      
      // Связи между сотрудниками и отделами
      const staffDivisionEdges = staffList
        .filter(s => s.division_id !== null)
        .map(s => ({
          id: `staff_div_${s.id}`,
          from: `div_${s.division_id}`,
          to: `staff_${s.id}`,
          type: 'department' as RelationType
        }));
      
      // Объединяем связи
      const edges = [...divisionEdges, ...staffEdges, ...staffDivisionEdges];
      
      return { nodes, edges };
    } catch (error) {
      console.error('Ошибка при получении бизнес-структуры:', error);
      throw error;
    }
  },
  
  // Получение юридической структуры
  async getLegalStructure(): Promise<{ nodes: EntityNode[]; edges: EntityRelation[] }> {
    try {
      // Получаем юридические лица
      const orgResponse = await api.get('/organizations', {
        params: { org_type: 'LEGAL_ENTITY' }
      });
      const legalEntities: OrganizationDTO[] = orgResponse.data;
      
      // Маппим в узлы
      const nodes = legalEntities.map(org => mapOrganizationToEntityNode(org));
      
      // Создаем связи
      const edges = legalEntities
        .filter(org => org.parent_id !== null)
        .map(org => ({
          id: `legal_edge_${org.id}`,
          from: org.parent_id!.toString(),
          to: org.id.toString(),
          type: 'department' as RelationType
        }));
      
      return { nodes, edges };
    } catch (error) {
      console.error('Ошибка при получении юридической структуры:', error);
      throw error;
    }
  },
  
  // Получение территориальной структуры
  async getTerritorialStructure(): Promise<{ nodes: EntityNode[]; edges: EntityRelation[] }> {
    try {
      // Получаем локации
      const orgResponse = await api.get('/organizations', {
        params: { org_type: 'LOCATION' }
      });
      const locations: OrganizationDTO[] = orgResponse.data;
      
      // Маппим в узлы
      const nodes = locations.map(org => mapOrganizationToEntityNode(org));
      
      // Создаем связи
      const edges = locations
        .filter(org => org.parent_id !== null)
        .map(org => ({
          id: `location_edge_${org.id}`,
          from: org.parent_id!.toString(),
          to: org.id.toString(),
          type: 'territorial' as RelationType
        }));
      
      return { nodes, edges };
    } catch (error) {
      console.error('Ошибка при получении территориальной структуры:', error);
      throw error;
    }
  },
  
  // Обновление узла
  async updateNode(node: EntityNode): Promise<EntityNode> {
    try {
      // Определяем тип узла и соответствующий эндпоинт
      let endpoint = '';
      let data = {};
      
      if (node.id.startsWith('staff_')) {
        endpoint = `/staff/${node.id.replace('staff_', '')}`;
        data = {
          position: node.position,
          manager_id: node.manager ? parseInt(node.manager.replace('staff_', '')) : null
        };
      } else if (node.id.startsWith('div_')) {
        endpoint = `/divisions/${node.id.replace('div_', '')}`;
        data = {
          name: node.name,
          description: node.name
        };
      } else {
        endpoint = `/organizations/${node.id}`;
        data = {
          name: node.name,
          description: node.name
        };
      }
      
      const response = await api.put(endpoint, data);
      return node; // В идеале надо обновить из ответа
    } catch (error) {
      console.error('Ошибка при обновлении узла:', error);
      throw error;
    }
  },
  
  // Добавление узла
  async addNode(node: EntityNode, parentId?: string): Promise<EntityNode> {
    try {
      // Определяем тип узла и соответствующий эндпоинт
      let endpoint = '';
      let data = {};
      
      if (node.type === 'staff') {
        endpoint = '/staff';
        data = {
          first_name: node.name.split(' ')[1] || 'Новый',
          last_name: node.name.split(' ')[0] || 'Сотрудник',
          position: node.position || '',
          division_id: parentId ? parseInt(parentId.replace('div_', '')) : null
        };
      } else if (node.type === 'business') {
        endpoint = '/divisions';
        data = {
          name: node.name,
          code: node.position || 'DIV',
          parent_id: parentId ? parseInt(parentId.replace('div_', '')) : null
        };
      } else {
        endpoint = '/organizations';
        data = {
          name: node.name,
          org_type: node.type.toUpperCase(),
          parent_id: parentId ? parseInt(parentId) : null
        };
      }
      
      const response = await api.post(endpoint, data);
      // В идеале надо вернуть данные из ответа
      return {
        ...node,
        id: response.data.id.toString()
      };
    } catch (error) {
      console.error('Ошибка при добавлении узла:', error);
      throw error;
    }
  },
  
  // Удаление узла
  async deleteNode(nodeId: string): Promise<void> {
    try {
      // Определяем тип узла и соответствующий эндпоинт
      let endpoint = '';
      
      if (nodeId.startsWith('staff_')) {
        endpoint = `/staff/${nodeId.replace('staff_', '')}`;
      } else if (nodeId.startsWith('div_')) {
        endpoint = `/divisions/${nodeId.replace('div_', '')}`;
      } else {
        endpoint = `/organizations/${nodeId}`;
      }
      
      await api.delete(endpoint);
    } catch (error) {
      console.error('Ошибка при удалении узла:', error);
      throw error;
    }
  },
  
  // Добавление связи
  async addEdge(edge: { from: string, to: string, type: RelationType }): Promise<EntityRelation> {
    try {
      let endpoint = '';
      let data = {};
      
      // Определяем тип связи и эндпоинт
      if (edge.from.startsWith('staff_') && edge.to.startsWith('staff_')) {
        endpoint = '/functional-relations';
        data = {
          manager_id: parseInt(edge.from.replace('staff_', '')),
          subordinate_id: parseInt(edge.to.replace('staff_', '')),
          relation_type: edge.type.toUpperCase()
        };
      } else {
        // Другие типы связей - реализовать при необходимости
        throw new Error('Неподдерживаемый тип связи');
      }
      
      const response = await api.post(endpoint, data);
      return {
        id: response.data.id.toString(),
        from: edge.from,
        to: edge.to,
        type: edge.type
      };
    } catch (error) {
      console.error('Ошибка при добавлении связи:', error);
      throw error;
    }
  },
  
  // Удаление связи
  async deleteEdge(edgeId: string): Promise<void> {
    try {
      await api.delete(`/functional-relations/${edgeId}`);
    } catch (error) {
      console.error('Ошибка при удалении связи:', error);
      throw error;
    }
  }
};

export default organizationService; 