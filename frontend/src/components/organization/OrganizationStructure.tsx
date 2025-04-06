import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Space, Spin, Input, Button, Card } from 'antd';
import { SearchOutlined, FilterOutlined, CloseOutlined } from '@ant-design/icons';
import { ReactFlowProvider } from 'reactflow';
import ReactFlowGraph from './ReactFlowGraph';
import { EntityNode, EntityRelation, RelationType, Comment } from './types';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import styled from '@emotion/styled';

// Импортируем мок-данные
import { 
  mockBusinessNodes, 
  mockBusinessEdges, 
  mockLegalNodes, 
  mockLegalEdges, 
  mockTerritorialNodes, 
  mockTerritorialEdges 
} from '../../mocks/organizationStructure';

interface OrganizationStructureProps {
  type: 'business' | 'legal' | 'territorial';
}

// Стиль для LoadingOverlay
const LoadingOverlay = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(20, 20, 30, 0.7);
  z-index: 10;
  backdrop-filter: blur(5px);
`;

const OrganizationStructure: React.FC<OrganizationStructureProps> = ({ type }) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [nodes, setNodes] = useState<EntityNode[]>([]);
  const [edges, setEdges] = useState<EntityRelation[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Загрузка данных при монтировании
  useEffect(() => {
    setLoading(true);
    
    // Имитируем загрузку данных
    setTimeout(() => {
      let mockNodes: EntityNode[] = [];
      let mockEdges: EntityRelation[] = [];
      
      // Выбираем нужный набор данных в зависимости от типа
      switch (type) {
        case 'business':
          mockNodes = mockBusinessNodes;
          mockEdges = mockBusinessEdges;
          break;
        case 'legal':
          mockNodes = mockLegalNodes;
          mockEdges = mockLegalEdges;
          break;
        case 'territorial':
          mockNodes = mockTerritorialNodes;
          mockEdges = mockTerritorialEdges;
          break;
      }
      
      setNodes(mockNodes);
      setEdges(mockEdges);
      setLoading(false);
    }, 1000);
  }, [type]);

  // Основные обработчики для графа
  const handleNodeSelect = (nodeId: string | null) => {
    setSelectedNode(nodeId);
  };

  const handleNodeAdd = async (position: { x: number, y: number }) => {
    // Создание нового узла
    const newNode: EntityNode = {
      id: `node_${Date.now()}`,
      name: 'Новый сотрудник',
      type: type,
      position: 'Должность',
    };

    setNodes(prev => [...prev, newNode]);
  };

  const handleNodeDelete = (nodeId: string) => {
    setNodes(prev => prev.filter(node => node.id !== nodeId));
    setEdges(prev => prev.filter(edge => edge.from !== nodeId && edge.to !== nodeId));
  };

  const handleNodeUpdate = (updatedNode: EntityNode) => {
    setNodes(prev => prev.map(node => node.id === updatedNode.id ? updatedNode : node));
  };

  const handleEdgeAdd = (edge: { from: string, to: string, type: RelationType }) => {
    const newEdge: EntityRelation = {
      id: `edge_${Date.now()}`,
      from: edge.from,
      to: edge.to,
      type: edge.type,
    };

    setEdges(prev => [...prev, newEdge]);
  };

  const handleEdgeDelete = (edgeId: string) => {
    setEdges(prev => prev.filter(edge => edge.id !== edgeId));
  };

  // Обработчики для поиска
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleClearSearch = () => {
    setSearchTerm('');
  };

  // Фильтрация узлов по поисковому запросу
  const filteredNodes = useMemo(() => {
    if (!searchTerm) return nodes;
    
    return nodes.filter(node => 
      node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (node.position && node.position.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }, [nodes, searchTerm]);

  // Фильтрация связей по отфильтрованным узлам
  const filteredEdges = useMemo(() => {
    if (!searchTerm) return edges;
    
    const filteredNodeIds = filteredNodes.map(node => node.id);
    return edges.filter(edge => 
      filteredNodeIds.includes(edge.from) && filteredNodeIds.includes(edge.to)
    );
  }, [edges, filteredNodes, searchTerm]);

  // Рендерим граф организационной структуры
  return (
    <div style={{ width: '100%', height: 'calc(100vh - 150px)', position: 'relative' }}>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="Поиск по имени или должности"
          prefix={<SearchOutlined />}
          value={searchTerm}
          onChange={handleSearchChange}
          suffix={
            searchTerm ? (
              <CloseOutlined onClick={handleClearSearch} style={{ cursor: 'pointer' }} />
            ) : (
              <FilterOutlined />
            )
          }
          style={{ width: 300 }}
        />
      </Space>
      
      <Card style={{ width: '100%', height: 'calc(100vh - 200px)', position: 'relative' }}>
        {loading ? (
          <LoadingOverlay>
            <Spin size="large" />
          </LoadingOverlay>
        ) : (
          <ReactFlowProvider>
            <ReactFlowGraph
              type={type}
              nodes={filteredNodes}
              edges={filteredEdges}
              selectedNodeId={selectedNode}
              onNodeSelect={handleNodeSelect}
              onNodeAdd={handleNodeAdd}
              onNodeDelete={handleNodeDelete}
              onNodeUpdate={handleNodeUpdate}
              onEdgeAdd={handleEdgeAdd}
              onEdgeDelete={handleEdgeDelete}
              height={`calc(100vh - 250px)`}
            />
          </ReactFlowProvider>
        )}
      </Card>
    </div>
  );
};

// Функция для генерации моковых данных
const generateMockData = (type: string) => {
  // Примеры комментариев для демонстрации
  const ceoComments: Comment[] = [
    { text: 'Провести совещание с руководителями подразделений', completed: true, date: '2023-10-05T10:00:00Z' },
    { text: 'Подготовить отчет за квартал', completed: false, date: '2023-10-10T14:30:00Z' }
  ];
  
  const ctoComments: Comment[] = [
    { text: 'Оптимизировать инфраструктуру', completed: false, date: '2023-10-12T11:20:00Z' },
    { text: 'Обсудить новую технологию с командой разработки', completed: true, date: '2023-10-03T16:45:00Z' }
  ];

  const nodes: EntityNode[] = [
    { id: 'ceo', name: 'Иванов И.И.', type: type as any, position: 'CEO', comments: ceoComments },
    { id: 'cfo', name: 'Петров П.П.', type: type as any, position: 'CFO', manager: 'Иванов И.И.' },
    { id: 'cto', name: 'Сидоров С.С.', type: type as any, position: 'CTO', manager: 'Иванов И.И.', comments: ctoComments },
    { id: 'cmo', name: 'Николаев Н.Н.', type: type as any, position: 'CMO', manager: 'Иванов И.И.' },
    { id: 'dev_lead', name: 'Михайлов М.М.', type: type as any, position: 'Руководитель разработки', manager: 'Сидоров С.С.' },
    { id: 'dev1', name: 'Алексеев А.А.', type: type as any, position: 'Разработчик', manager: 'Михайлов М.М.' },
    { id: 'dev2', name: 'Сергеев С.С.', type: type as any, position: 'Разработчик', manager: 'Михайлов М.М.' },
    { id: 'design_lead', name: 'Дмитриев Д.Д.', type: type as any, position: 'Руководитель дизайна', manager: 'Николаев Н.Н.' },
    { id: 'designer1', name: 'Кузнецов К.К.', type: type as any, position: 'Дизайнер', manager: 'Дмитриев Д.Д.' },
    { id: 'finance1', name: 'Васильев В.В.', type: type as any, position: 'Финансовый специалист', manager: 'Петров П.П.' },
    { id: 'hr', name: 'Андреева А.А.', type: type as any, position: 'HR Менеджер', manager: 'Иванов И.И.' },
    { id: 'regional1', name: 'Романов Р.Р.', type: type as any, position: 'Региональный менеджер', manager: 'Николаев Н.Н.' }
  ];

  const edges: EntityRelation[] = [
    { id: 'e1', from: 'ceo', to: 'cfo', type: 'manager' },
    { id: 'e2', from: 'ceo', to: 'cto', type: 'manager' },
    { id: 'e3', from: 'ceo', to: 'cmo', type: 'manager' },
    { id: 'e4', from: 'ceo', to: 'hr', type: 'manager' },
    { id: 'e5', from: 'cto', to: 'dev_lead', type: 'manager' },
    { id: 'e6', from: 'dev_lead', to: 'dev1', type: 'manager' },
    { id: 'e7', from: 'dev_lead', to: 'dev2', type: 'manager' },
    { id: 'e8', from: 'cmo', to: 'design_lead', type: 'manager' },
    { id: 'e9', from: 'design_lead', to: 'designer1', type: 'manager' },
    { id: 'e10', from: 'cfo', to: 'finance1', type: 'manager' },
    { id: 'e11', from: 'cmo', to: 'regional1', type: 'manager' },
    { id: 'e12', from: 'dev1', to: 'designer1', type: 'functional', label: 'Совместная работа' },
    { id: 'e13', from: 'dev2', to: 'finance1', type: 'functional', label: 'Разработка финансовых модулей' },
    { id: 'e14', from: 'dev_lead', to: 'cmo', type: 'functional', label: 'Согласование требований' }
  ];

  return { nodes, edges };
};

export default OrganizationStructure; 