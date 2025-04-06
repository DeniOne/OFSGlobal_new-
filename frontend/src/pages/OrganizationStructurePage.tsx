import React, { useState, useEffect, useCallback } from 'react';
import styled from '@emotion/styled';
import { ReactFlowProvider } from 'reactflow';
import AntOrganizationTree from '../components/organization/AntOrganizationTree';
import OrgTreeControls from '../components/organization/OrgTreeControls';
import { useNavigate, useLocation, useParams } from 'react-router-dom';
import { EntityNode, EntityRelation, RelationType } from '../components/organization/types';
import ReactFlowGraph from '../components/organization/ReactFlowGraph';
import organizationService from '../services/organizationService';
import { Spin, Card } from 'antd';

// Стилизованные компоненты
const PageContainer = styled.div`
  max-width: 100%;
  padding-top: 24px;
  padding-bottom: 24px;
  position: relative;
`;

const ControlsContainer = styled.div`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 16px;
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(26, 26, 30, 0.7);
  z-index: 10;
  border-radius: 12px;
  backdrop-filter: blur(4px);
`;

// Временные моковые данные для наших графов
/*
const mockNodes: Record<string, EntityNode[]> = {
  business: [
    { id: '1', name: 'Генеральный директор', type: 'business', position: 'CEO' },
    { id: '2', name: 'Финансовый отдел', type: 'business' },
    { id: '3', name: 'Бухгалтерия', type: 'business' },
    { id: '4', name: 'Финансовый директор', type: 'business', position: 'CFO', manager: 'Генеральный директор' },
    { id: '5', name: 'Главный бухгалтер', type: 'business', position: 'Chief Accountant' },
    { id: '6', name: 'IT отдел', type: 'business' },
    { id: '7', name: 'Разработка', type: 'business' },
    { id: '8', name: 'Поддержка', type: 'business' },
    { id: '9', name: 'CTO', type: 'business', position: 'CTO', manager: 'Генеральный директор' },
  ],
  legal: [
    { id: 'l1', name: 'ООО "Компания"', type: 'legal' },
    { id: 'l2', name: 'ЗАО "Филиал 1"', type: 'legal' },
    { id: 'l3', name: 'ООО "Дочерняя компания"', type: 'legal' },
    { id: 'l4', name: 'ИП Иванов', type: 'legal' },
  ],
  territorial: [
    { id: 't1', name: 'Головной офис', type: 'territorial', position: 'Москва' },
    { id: 't2', name: 'Филиал Санкт-Петербург', type: 'territorial' },
    { id: 't3', name: 'Филиал Новосибирск', type: 'territorial' },
    { id: 't4', name: 'Филиал Казань', type: 'territorial' },
    { id: 't5', name: 'Региональный директор', type: 'territorial', position: 'Директор СПб филиала' },
  ],
};
*/

const mockEdges: Record<string, EntityRelation[]> = {
  business: [
    { id: 'e1', from: '1', to: '2', type: 'department' },
    { id: 'e2', from: '1', to: '6', type: 'department' },
    { id: 'e3', from: '2', to: '3', type: 'department' },
    { id: 'e4', from: '1', to: '4', type: 'manager' },
    { id: 'e5', from: '4', to: '5', type: 'manager' },
    { id: 'e6', from: '6', to: '7', type: 'department' },
    { id: 'e7', from: '6', to: '8', type: 'department' },
    { id: 'e8', from: '1', to: '9', type: 'manager' },
    { id: 'e9', from: '9', to: '6', type: 'functional' },
  ],
  legal: [
    { id: 'le1', from: 'l1', to: 'l2', type: 'department' },
    { id: 'le2', from: 'l1', to: 'l3', type: 'department' },
    { id: 'le3', from: 'l3', to: 'l4', type: 'functional' },
  ],
  territorial: [
    { id: 'te1', from: 't1', to: 't2', type: 'department' },
    { id: 'te2', from: 't1', to: 't3', type: 'department' },
    { id: 'te3', from: 't1', to: 't4', type: 'department' },
    { id: 'te4', from: 't2', to: 't5', type: 'manager' },
  ],
};

const OrganizationStructurePage: React.FC = () => {
  const { type = 'business' } = useParams<{ type?: 'business' | 'legal' | 'territorial' }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [nodes, setNodes] = useState<EntityNode[]>([]);
  const [edges, setEdges] = useState<EntityRelation[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [displayMode, setDisplayMode] = useState<'tree' | 'list'>('tree');
  
  // Загрузка данных при изменении типа структуры
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        let result;
        switch (type) {
          case 'business':
            result = await organizationService.getBusinessStructure();
            break;
          case 'legal':
            result = await organizationService.getLegalStructure();
            break;
          case 'territorial':
            result = await organizationService.getTerritorialStructure();
            break;
          default:
            result = { nodes: [], edges: [] };
        }
        
        setNodes(result.nodes);
        setEdges(result.edges);
      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
        // При ошибке используем пустые массивы
        setNodes([]);
        setEdges([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [type]);
  
  // Обработчики для работы с узлами и связями
  const handleNodeSelect = useCallback((nodeId: string | null) => {
    setSelectedNode(nodeId);
  }, []);
  
  const handleNodeAdd = useCallback(async (position: { x: number, y: number }) => {
    try {
      // Создаем базовый узел в зависимости от типа структуры
      const newNode: EntityNode = {
        id: `temp_${Date.now()}`, // Временный ID
        name: 'Новый элемент',
        type: type,
        position: type === 'territorial' ? 'Новая локация' : 'Новая должность'
      };
      
      // Добавляем узел через API
      const addedNode = await organizationService.addNode(newNode);
      
      // Обновляем состояние - учитываем что position в EntityNode это строка
      setNodes(prev => [...prev, { 
        ...addedNode,
        // position уже определен в addedNode как строка
      }]);
    } catch (error) {
      console.error('Ошибка при добавлении узла:', error);
    }
  }, [type]);
  
  const handleNodeDelete = useCallback(async (nodeId: string) => {
    try {
      // Удаляем узел через API
      await organizationService.deleteNode(nodeId);
      
      // Обновляем состояние
      setNodes(prev => prev.filter(node => node.id !== nodeId));
      setEdges(prev => prev.filter(edge => edge.from !== nodeId && edge.to !== nodeId));
    } catch (error) {
      console.error('Ошибка при удалении узла:', error);
    }
  }, []);
  
  const handleNodeUpdate = useCallback(async (updatedNode: EntityNode) => {
    try {
      // Обновляем узел через API
      await organizationService.updateNode(updatedNode);
      
      // Обновляем состояние
      setNodes(prev => prev.map(node => 
        node.id === updatedNode.id ? updatedNode : node
      ));
    } catch (error) {
      console.error('Ошибка при обновлении узла:', error);
    }
  }, []);
  
  const handleEdgeAdd = useCallback(async (edge: { from: string, to: string, type: RelationType }) => {
    try {
      // Добавляем связь через API
      const addedEdge = await organizationService.addEdge(edge);
      
      // Обновляем состояние
      setEdges(prev => [...prev, addedEdge]);
    } catch (error) {
      console.error('Ошибка при добавлении связи:', error);
    }
  }, []);
  
  const handleEdgeDelete = useCallback(async (edgeId: string) => {
    try {
      // Удаляем связь через API
      await organizationService.deleteEdge(edgeId);
      
      // Обновляем состояние
      setEdges(prev => prev.filter(edge => edge.id !== edgeId));
    } catch (error) {
      console.error('Ошибка при удалении связи:', error);
    }
  }, []);
  
  // Обработчик изменения типа структуры
  const handleTypeChange = (event: React.SyntheticEvent, newType: 'business' | 'legal' | 'territorial') => {
    if (newType) {
      navigate(`/organization-structure/${newType}`);
    }
  };

  // Обработчик изменения режима отображения
  const handleDisplayModeChange = (mode: 'tree' | 'list') => {
    setDisplayMode(mode);
  };

  return (
    <PageContainer>
      <ControlsContainer>
        {/* Переключатель дерево/список теперь слева */}
        <OrgTreeControls
          displayMode={displayMode}
          onDisplayModeChange={handleDisplayModeChange}
        />
        {/* Пустое пространство справа */}
      </ControlsContainer>

      <Card 
        style={{ 
          height: 'calc(100vh - 180px)',
          padding: '16px',
          backgroundColor: 'rgba(26, 26, 30, 0.7)',
          borderRadius: '12px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.5)',
          border: '1px solid rgba(157, 106, 245, 0.2)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <div style={{ height: '100%', width: '100%', animation: !loading ? 'fadeIn 0.5s' : undefined }}>
          {/* Используем новый компонент с ReactFlow */}
          {displayMode === 'tree' ? (
            <ReactFlowProvider>
              {loading ? (
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 'calc(100vh - 200px)' }}>
                  <Spin size="large" />
                </div>
              ) : (
                <ReactFlowGraph
                  type={type}
                  nodes={nodes}
                  edges={edges}
                  selectedNodeId={selectedNode}
                  onNodeSelect={handleNodeSelect}
                  onNodeAdd={handleNodeAdd}
                  onNodeDelete={handleNodeDelete}
                  onNodeUpdate={handleNodeUpdate}
                  onEdgeAdd={handleEdgeAdd}
                  onEdgeDelete={handleEdgeDelete}
                  height="calc(100vh - 200px)"
                />
              )}
            </ReactFlowProvider>
          ) : (
            <AntOrganizationTree
              organizationId="1"
              viewMode={type}
              displayMode={displayMode}
              zoomLevel={100}
              detailLevel={1}
            />
          )}
        </div>
        
        {loading && (
          <LoadingOverlay>
            <Spin 
              size="large" 
              style={{ color: '#9D6AF5' }}
            />
          </LoadingOverlay>
        )}
      </Card>
    </PageContainer>
  );
};

export default OrganizationStructurePage; 