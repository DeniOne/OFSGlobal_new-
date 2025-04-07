import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Spin,
  Typography,
  Space,
  Button,
  Card,
  Alert,
  Divider,
  Select
} from 'antd';
import {
  ReloadOutlined
} from '@ant-design/icons';
import ReactFlow, {
  ReactFlowProvider,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  MarkerType,
  Position as RFPosition
} from 'reactflow';
import 'reactflow/dist/style.css';
import styled from '@emotion/styled';
import api from '../../services/api';
import dagre from 'dagre';

const { Title, Text } = Typography;
const { Option } = Select;

// Интерфейсы для данных с бэкенда
interface Division {
  id: number;
  name: string;
  code: string;
  parent_id?: number | null;
}

interface Position {
  id: number;
  name: string;
  code: string;
  division_id?: number | null;
  parent_id?: number | null;
  function_id?: number | null;
  is_active: boolean;
}

interface Function {
  id: number;
  name: string;
  code: string;
  is_active: boolean;
}

// Стилизованные компоненты
const ChartContainer = styled.div`
  width: 100%;
  height: calc(100vh - 240px);
  min-height: 500px;
  border-radius: 8px;
  overflow: hidden;
`;

// Размеры узлов для dagre
const nodeWidth = 200;
const nodeHeight = 60;

// Функция для создания графа dagre и расчета позиций
const getLayoutedElements = (nodes: any[], edges: any[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: direction });

  const nodeIds = new Set(nodes.map(n => n.id));

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    if (nodeIds.has(edge.source) && nodeIds.has(edge.target)) {
      dagreGraph.setEdge(edge.source, edge.target);
    } else {
      console.warn(`[LOG:PositionsChart] Skipped edge ${edge.id}: source or target not found`);
    }
  });

  try {
    dagre.layout(dagreGraph);
  } catch (error) {
    console.error("[LOG:PositionsChart] Layout error:", error);
    nodes.forEach(node => {
      node.position = { x: Math.random() * 400, y: Math.random() * 400 };
    });
    return { nodes, edges };
  }

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    if (nodeWithPosition) {
      node.targetPosition = RFPosition.Top;
      node.sourcePosition = RFPosition.Bottom;
      node.position = {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      };
    } else {
      node.position = { x: 0, y: 0 };
    }
  });

  return { nodes, edges };
};

// Стили узлов
const nodeBaseStyle = {
  padding: '10px',
  borderRadius: '8px',
  width: nodeWidth,
  textAlign: 'center' as const,
  fontSize: '12px',
  boxShadow: '0 2px 5px rgba(0, 0, 0, 0.1)',
};

const positionNodeStyle = {
  ...nodeBaseStyle,
  background: 'linear-gradient(to bottom, #ffffff, #f0f0f0)',
  border: '1px solid #52c41a',
};

const inactivePositionNodeStyle = {
  ...nodeBaseStyle,
  background: 'linear-gradient(to bottom, #f0f0f0, #e0e0e0)',
  border: '1px solid #d9d9d9',
  color: '#999',
};

const StructurePositionsPage: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [functions, setFunctions] = useState<Function[]>([]);
  const [selectedDivision, setSelectedDivision] = useState<number | undefined>(undefined);
  const [selectedFunction, setSelectedFunction] = useState<number | undefined>(undefined);
  const [includeInactive, setIncludeInactive] = useState(false);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  // Загрузка исходных данных
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        const [divResponse, funcResponse] = await Promise.all([
          api.get('/divisions/'),
          api.get('/functions/')
        ]);
        setDivisions(divResponse.data);
        setFunctions(funcResponse.data);
        setError(null);
      } catch (err: any) {
        console.error('[LOG:PositionsChart] Error loading initial data:', err);
        setError(err.message || 'Ошибка при загрузке данных');
      } finally {
        setLoading(false);
      }
    };
    
    fetchInitialData();
  }, []);

  // Загрузка позиций и создание графа
  const fetchData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setLoading(true);
    setError(null);
    
    try {
      // Создаем параметры запроса
      const params = new URLSearchParams();
      if (selectedDivision) params.append('division_id', selectedDivision.toString());
      if (selectedFunction) params.append('function_id', selectedFunction.toString());
      if (includeInactive) params.append('include_inactive', 'true');
      
      const queryString = params.toString() ? `?${params.toString()}` : '';
      
      // Загружаем позиции с фильтрацией
      const posResponse = await api.get(`/positions/${queryString}`, { signal });
      const positions: Position[] = posResponse.data;
      
      // Преобразуем данные в формат для ReactFlow
      const flowNodes: any[] = [];
      const flowEdges: any[] = [];
      const nodeIds = new Set<string>();

      // Создаем узлы для позиций
      positions.forEach(pos => {
        const nodeId = `pos-${pos.id}`;
        flowNodes.push({
          id: nodeId,
          data: { 
            label: (
              <div>
                <div style={{ fontWeight: 'bold' }}>{pos.name}</div>
                {pos.code && <div style={{ fontSize: '10px' }}>Код: {pos.code}</div>}
              </div>
            ),
            type: 'position',
            code: pos.code,
            id: pos.id,
            isActive: pos.is_active
          },
          position: { x: 0, y: 0 },
          style: pos.is_active ? positionNodeStyle : inactivePositionNodeStyle,
        });
        nodeIds.add(nodeId);
      });

      // Создаем рёбра между позициями
      positions.forEach(pos => {
        if (pos.parent_id) {
          const sourceId = `pos-${pos.parent_id}`;
          const targetId = `pos-${pos.id}`;
          if (nodeIds.has(sourceId) && nodeIds.has(targetId) && sourceId !== targetId) {
            flowEdges.push({
              id: `e_pos_${pos.parent_id}_${pos.id}`,
              source: sourceId,
              target: targetId,
              type: 'smoothstep',
              markerEnd: { type: MarkerType.ArrowClosed },
              style: { stroke: '#52c41a' }
            });
          }
        }
      });

      // Применяем автоматическое расположение элементов
      const { nodes: layoutedNodes, edges: layoutedEdges } = 
        getLayoutedElements(flowNodes, flowEdges, 'TB');

      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
      setError(null);
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('[LOG:PositionsChart] Fetch aborted');
        return;
      }
      console.error('[LOG:PositionsChart] Error loading positions:', err);
      setError(err.message || 'Ошибка при загрузке должностей');
      setNodes([]);
      setEdges([]);
    } finally {
      if (!signal.aborted) {
        setLoading(false);
        abortControllerRef.current = null;
      }
    }
  }, [selectedDivision, selectedFunction, includeInactive]);

  // Загружаем данные при изменении фильтров
  useEffect(() => {
    fetchData();
    
    return () => {
      abortControllerRef.current?.abort();
    };
  }, [fetchData]);

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Title level={2}>Структура должностей</Title>
        
        <Card>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space wrap align="center" style={{ marginBottom: 16 }}>
              <Text strong>Фильтры:</Text>
              
              <Select
                placeholder="Выберите подразделение"
                style={{ width: 200 }}
                allowClear
                value={selectedDivision}
                onChange={(value) => setSelectedDivision(value)}
              >
                {divisions.map(div => (
                  <Option key={div.id} value={div.id}>{div.name}</Option>
                ))}
              </Select>
              
              <Select
                placeholder="Выберите функцию"
                style={{ width: 200 }}
                allowClear
                value={selectedFunction}
                onChange={(value) => setSelectedFunction(value)}
              >
                {functions.map(func => (
                  <Option key={func.id} value={func.id}>{func.name}</Option>
                ))}
              </Select>
              
              <Button
                type="primary"
                onClick={() => setIncludeInactive(!includeInactive)}
              >
                {includeInactive ? 'Только активные' : 'Включить неактивные'}
              </Button>
              
              <Button 
                icon={<ReloadOutlined />} 
                onClick={fetchData}
                loading={loading}
              >
                Обновить
              </Button>
            </Space>
            
            {error && (
              <Alert
                message="Ошибка"
                description={error}
                type="error"
                showIcon
                closable
                onClose={() => setError(null)}
                style={{ marginBottom: 16 }}
              />
            )}
            
            <Divider style={{ margin: '12px 0' }} />
            
            <ChartContainer>
              <ReactFlowProvider>
                <ReactFlow
                  nodes={nodes}
                  edges={edges}
                  onNodesChange={onNodesChange}
                  onEdgesChange={onEdgesChange}
                  fitView
                  attributionPosition="bottom-left"
                >
                  <Controls />
                  <MiniMap />
                  <Background color="#f5f5f5" gap={16} />
                </ReactFlow>
              </ReactFlowProvider>
            </ChartContainer>
            
            <div style={{ marginTop: 16 }}>
              <Text type="secondary">
                * На графе показаны иерархические связи между должностями. 
                {!includeInactive && ' Неактивные должности скрыты.'}
              </Text>
            </div>
          </Space>
        </Card>
      </Space>
    </div>
  );
};

export default StructurePositionsPage; 