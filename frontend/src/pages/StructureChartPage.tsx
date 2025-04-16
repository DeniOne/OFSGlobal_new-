import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Spin,
  message,
  Typography,
  Space,
  Button,
  Alert,
  Form,
  InputNumber,
  Select,
  Card,
  Row,
  Col,
  Tooltip,
  Avatar
} from 'antd';
import {
  ReloadOutlined,
  FilterOutlined,
  UserOutlined,
  MailOutlined
} from '@ant-design/icons';
import ReactFlow, {
  ReactFlowProvider,
  useNodesState,
  useEdgesState,
  Controls,
  MiniMap,
  Background,
  MarkerType,
  Position as RFPosition,
  Node,
  Edge,
  Handle
} from 'reactflow';

import 'reactflow/dist/style.css'; // Импортируем стили React Flow

// Импортируем наши сервисы
import positionsService from '../services/positionsService';
import { getAllHierarchyRelations } from '../services/hierarchyRelationsService';
import organizationService, { OrganizationDTO } from '../services/organizationService';
import staffService from '../services/staffService';

// Импортируем типы
import { HierarchyRelation } from '../types/hierarchy';
import { Position } from '../types/organization';
// Используем тип Position из types/organization
// import { Position } from '../services/positionsService'; // Assuming Position is exported there

import dagre from 'dagre';

const { Title } = Typography;

// Размеры узлов для dagre
const nodeWidth = 250;  // Увеличиваем ширину для размещения информации о сотрудниках
const nodeHeight = 150; // Увеличиваем высоту для сотрудников

// Функция для создания графа dagre и расчета позиций
const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB'): { nodes: Node[]; edges: Edge[] } => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: direction });

  const nodeIds = new Set(nodes.map(n => n.id));

  nodes.forEach((node) => {
    // Используем реальные размеры узла, если они доступны, иначе дефолтные
    // Это может потребовать рендеринга узлов для получения размеров, что сложно.
    // Пока используем фиксированные размеры для dagre.
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    if (nodeIds.has(edge.source) && nodeIds.has(edge.target)) {
      dagreGraph.setEdge(edge.source, edge.target);
    } else {
      console.warn(`[LOG:Chart] Dagre: Skipped edge ${edge.id} because source or target node not found.`);
    }
  });

  try {
    dagre.layout(dagreGraph);
  } catch (layoutError) {
    console.error("[LOG:Chart] Dagre layout error:", layoutError);
    nodes.forEach(node => {
      node.data = { ...node.data, layoutError: true };
      node.position = { x: Math.random() * 400, y: Math.random() * 400 };
    });
    message.error('Ошибка автоматической раскладки схемы.');
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
      node.data = { ...node.data, layoutError: false };
    } else {
      console.warn(`[LOG:Chart] Node ${node.id} not found in dagre graph after layout.`);
      node.position = { x: 0, y: 0 };
    }
  });

  return { nodes, edges };
};

// Функция для определения стиля узла на основе атрибута
const getNodeStyle = (attribute: string) => {
  const baseStyle = {
    border: '1px solid',
    padding: '10px 15px',
    borderRadius: '8px',
    background: 'white',
    width: nodeWidth,
    textAlign: 'center' as const,
    fontSize: '12px',
    color: '#fff', // Базовый цвет текста - белый
    fontWeight: 'bold', // Жирный текст для лучшей читаемости
    boxShadow: '0 4px 12px rgba(0,0,0,0.25)' // Добавляем тень для объема
  };

  // Стили для разных атрибутов
  switch (attribute) {
    case 'Директор Направления':
      return { ...baseStyle, borderColor: '#f5222d', background: 'linear-gradient(135deg, #cf1322 0%, #a8071a 100%)', color: '#fff' };
    case 'Руководитель Департамента':
      return { ...baseStyle, borderColor: '#fa8c16', background: 'linear-gradient(135deg, #d46b08 0%, #ad4e00 100%)', color: '#fff' };
    case 'Руководитель Отдела':
        return { ...baseStyle, borderColor: '#1890ff', background: 'linear-gradient(135deg, #096dd9 0%, #0050b3 100%)', color: '#fff' };
    case 'Специалист':
      return { ...baseStyle, borderColor: '#52c41a', background: 'linear-gradient(135deg, #389e0d 0%, #237804 100%)', color: '#fff' };
    // Добавляем остальные атрибуты
    case 'Учредитель':
      return { ...baseStyle, borderColor: '#722ed1', background: 'linear-gradient(135deg, #531dab 0%, #391085 100%)', color: '#fff' };
    case 'Директор':
      return { ...baseStyle, borderColor: '#eb2f96', background: 'linear-gradient(135deg, #c41d7f 0%, #9e1068 100%)', color: '#fff' };
    // Добавить стили для других атрибутов из Enum
    default:
      return { ...baseStyle, borderColor: '#d9d9d9', background: 'linear-gradient(135deg, #8c8c8c 0%, #595959 100%)', color: '#fff' };
  }
};

interface FilterFormValues {
  organization_id?: number;
  root_position_id?: number;
  depth?: number;
}

// Определение кастомного узла
interface CustomNodeData {
  label: string;
  attribute: string;
  db_id: number;
  staff?: {
    id: number;
    name: string;
    position?: string;
    email?: string;
  }[];
}

const CustomNode: React.FC<{ data: CustomNodeData }> = ({ data }) => {
  const style = getNodeStyle(data.attribute);
  
  const getInitials = (name: string) => {
    const parts = name.split(' ');
    if (parts.length === 1) return parts[0].charAt(0).toUpperCase();
    return (parts[0].charAt(0) + parts[1].charAt(0)).toUpperCase();
  };
  
  return (
    <div style={{
      ...style,
      minHeight: nodeHeight, // Обеспечиваем минимальную высоту
      width: nodeWidth,     // Фиксированная ширина
      boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
      border: '1px solid rgba(255,255,255,0.2)',
      padding: '15px',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between'
    }}>
      <Handle type="target" position={RFPosition.Top} />
      
      <div style={{ 
        marginBottom: '10px', 
        fontWeight: 'bold',
        fontSize: '14px',
        textAlign: 'center',
        padding: '5px',
        background: 'rgba(0,0,0,0.2)',
        borderRadius: '4px'
      }}>
        {data.label}
      </div>
      
      {data.staff && data.staff.length > 0 ? (
        <div style={{ 
          fontSize: '12px', 
          textAlign: 'left',
          marginTop: '5px',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          {data.staff.map((person, idx) => (
            <div 
              key={idx} 
              style={{ 
                padding: '8px', 
                borderRadius: '6px', 
                background: 'rgba(255,255,255,0.15)',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '10px'
              }}
            >
              <Avatar 
                style={{ 
                  backgroundColor: '#1890ff', 
                  fontSize: '11px',
                  marginTop: '2px'
                }} 
                size="small"
              >
                {getInitials(person.name)}
              </Avatar>
              <div style={{ flex: 1, overflow: 'hidden' }}>
                <div style={{ 
                  fontWeight: 'bold', 
                  marginBottom: '2px',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis'
                }}>
                  {person.name}
                </div>
                {person.position && (
                  <div style={{ 
                    fontSize: '10px', 
                    opacity: 0.8,
                    marginBottom: '3px' 
                  }}>
                    {person.position}
                  </div>
                )}
                {person.email && (
                  <Tooltip title={person.email}>
                    <div style={{ 
                      fontSize: '10px', 
                      display: 'flex', 
                      alignItems: 'center',
                      gap: '4px'
                    }}>
                      <MailOutlined style={{ fontSize: '10px' }} />
                      <span style={{ 
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis'
                      }}>
                        {person.email}
                      </span>
                    </div>
                  </Tooltip>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ 
          fontSize: '13px', 
          opacity: 0.8, 
          fontStyle: 'italic', 
          marginTop: '10px',
          padding: '8px',
          background: 'rgba(0,0,0,0.2)',
          borderRadius: '6px',
          textAlign: 'center',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flex: 1
        }}>
          <UserOutlined style={{ marginRight: '8px' }} />
          (вакансия)
        </div>
      )}
      
      <Handle type="source" position={RFPosition.Bottom} />
    </div>
  );
};

const StructureChartPage: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node[]>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [organizations, setOrganizations] = useState<OrganizationDTO[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [filters, setFilters] = useState<FilterFormValues>({});
  const [filterForm] = Form.useForm();
  const abortControllerRef = useRef<AbortController | null>(null);
  const [positionOptions, setPositionOptions] = useState<{ value: number; label: string }[]>([]);

  // Загрузка списков для фильтров
  useEffect(() => {
    const fetchFilterData = async () => {
      try {
        const [orgsData, positionsData] = await Promise.all([
          organizationService.getAllOrganizations(),
          positionsService.getAllPositions()
        ]);
        setOrganizations(orgsData);
        setPositions(positionsData);
        setPositionOptions(positionsData.map(pos => ({ value: pos.id, label: pos.name })));
      } catch (err) {
        console.error("[LOG:Chart] Error fetching filter data:", err);
        message.error('Ошибка загрузки данных для фильтров.');
      }
    };
    
    fetchFilterData();
  }, []);
  
  // Функция трансформации данных (для старого метода)
  const transformDataToFlow = useCallback((positions: Position[], relations: HierarchyRelation[]) => {
    const flowNodes: Node[] = [];
    const flowEdges: Edge[] = [];

    // 1. Создаем узлы для Должностей
    positions.forEach(pos => {
      const nodeId = `pos-${pos.id}`;
      flowNodes.push({
        id: nodeId,
        type: 'custom', // Используем кастомный тип узла
        data: { 
          label: pos.name, 
          attribute: pos.attribute,
          db_id: pos.id,
          // Временно пустой список сотрудников, можно будет загрузить в отдельном запросе
          staff: []
        },
        position: { x: 0, y: 0 }, // Позиции будут установлены dagre
      });
    });

    // 2. Создаем ребра на основе Hierarchy Relations
    relations.forEach(rel => {
      const sourceId = `pos-${rel.superior_position_id}`;
      const targetId = `pos-${rel.subordinate_position_id}`;
      // Проверяем, что оба узла существуют в нашем списке flowNodes
      if (flowNodes.some(n => n.id === sourceId) && flowNodes.some(n => n.id === targetId)) {
        flowEdges.push({
          id: `e_rel_${rel.id}`,
          source: sourceId,
          target: targetId,
          type: 'smoothstep', // Или другой тип ребра
          markerEnd: { type: MarkerType.ArrowClosed },
          style: { stroke: '#aaa' } // Базовый стиль ребра
        });
      } else {
          console.warn(`[LOG:Chart] Edge skipped: hierarchy relation ${sourceId} -> ${targetId} (one or both nodes missing in initial list)`);
      }
    });

    console.log('[LOG:Chart] Transformed Nodes:', flowNodes);
    console.log('[LOG:Chart] Transformed Edges:', flowEdges);

    // Применяем раскладку Dagre
    const layouted = getLayoutedElements(flowNodes, flowEdges);
    
    return layouted; // Возвращаем узлы и ребра с позициями

  }, []);

  // Старый метод загрузки (через отдельные запросы должностей и связей)
  const fetchLegacyData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setLoading(true);
    setError(null);
    try {
      console.log('[LOG:Chart] Fetching positions and relations...');
      // Загружаем только должности и иерархические связи
      const [positions, relations] = await Promise.all([
        positionsService.getAllPositions(/* { signal } - если сервис поддерживает AbortSignal */),
        getAllHierarchyRelations(/* { signal } */)
      ]);
      console.log('[LOG:Chart] Positions fetched:', positions);
      console.log('[LOG:Chart] Relations fetched:', relations);

      if (signal.aborted) return; // Проверяем, не был ли запрос отменен

      // Трансформируем данные и применяем layout
      const { nodes: layoutedNodes, edges: layoutedEdges } = transformDataToFlow(positions, relations);
      
      console.log('[LOG:Chart] Setting layouted nodes and edges');
      setNodes(layoutedNodes);
      setEdges(layoutedEdges);

      // Дополнительно загружаем информацию о сотрудниках для каждой должности
      try {
        // Собираем ID всех должностей
        const positionIds = positions.map(p => p.id);
        
        // Загружаем сотрудников для всех должностей
        const staffByPosition: Record<number, any[]> = {};
        
        await Promise.all(positionIds.map(async (posId) => {
          try {
            const staffData = await staffService.getStaffByPosition(posId);
            if (staffData.length > 0) {
              // Обновляем узел с информацией о сотрудниках
              setNodes(prevNodes => 
                prevNodes.map(node => {
                  if (node.id === `pos-${posId}`) {
                    // Форматируем данные сотрудников
                    const staffForNode = staffData.map(staff => {
                      const fullName = [
                        staff.last_name,
                        staff.first_name,
                        staff.middle_name
                      ].filter(Boolean).join(' ');
                      
                      return {
                        id: staff.id,
                        name: fullName,
                        position: staff.position || '',
                        email: staff.email || ''
                      };
                    });
                    
                    return {
                      ...node,
                      data: {
                        ...node.data,
                        staff: staffForNode
                      }
                    };
                  }
                  return node;
                })
              );
            }
          } catch (err) {
            console.warn(`[LOG:Chart] Failed to load staff for position ${posId}:`, err);
          }
        }));
        
        console.log('[LOG:Chart] Updated nodes with staff data');
      } catch (staffError) {
        console.warn('[LOG:Chart] Error loading staff data:', staffError);
        // Продолжаем без данных о сотрудниках
      }

    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('[LOG:Chart] Legacy fetch aborted');
        return;
      }
      console.error("[LOG:Chart] Error fetching or processing legacy data:", err);
      setError('Не удалось загрузить или обработать данные для схемы.');
      message.error('Ошибка загрузки данных для схемы.');
      setNodes([]); // Очищаем узлы при ошибке
      setEdges([]); // Очищаем ребра при ошибке
    } finally {
      if (!signal.aborted) {
        setLoading(false);
      }
    }
  }, [transformDataToFlow, setNodes, setEdges]);

  // Выбираем метод загрузки данных
  const fetchData = useCallback(() => {
    fetchLegacyData();
  }, [fetchLegacyData]);

  // Обработчик применения фильтров
  const handleFilterApply = (values: FilterFormValues) => {
    console.log('[LOG:Chart] Applying filters:', values);
    setFilters(values);
    // Закрываем панель фильтров
    setShowFilters(false);
  };

  // Обработчик сброса фильтров
  const handleFilterReset = () => {
    filterForm.resetFields();
    setFilters({});
    message.success('Фильтры сброшены');
    // Не закрываем панель фильтров
  };

  // Загрузка данных при монтировании компонента или изменении фильтров
  useEffect(() => {
    fetchData();
    // Очистка при размонтировании
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData, filters]); // Добавляем filters в зависимости

  return (
    <div style={{ height: '85vh', width: '100%', background: '#f0f2f5', padding: '20px' }}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Space style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
            <Title level={3}>Визуальная Схема Организационной Структуры</Title>
            <div>
              <Button 
                  icon={<FilterOutlined />} 
                  onClick={() => setShowFilters(!showFilters)}
                  style={{ marginRight: 10 }}
              >
                  {showFilters ? 'Скрыть фильтры' : 'Показать фильтры'}
              </Button>
              <Button 
                  icon={<ReloadOutlined />} 
                  onClick={fetchData} 
                  loading={loading}
                  disabled={loading}
              >
                  Обновить
              </Button>
            </div>
        </Space>
        
        {/* Блок фильтров */}
        {showFilters && (
          <Card title="Фильтры" style={{ width: '100%' }}>
            <Form 
              form={filterForm}
              layout="vertical" 
              onFinish={handleFilterApply}
              initialValues={filters}
            >
              <Row gutter={16}>
                <Col xs={24} sm={12} md={8}>
                  <Form.Item 
                    name="organization_id" 
                    label="Организация"
                  >
                    <Select 
                      allowClear
                      placeholder="Выберите организацию"
                      style={{ width: '100%' }}
                    >
                      {organizations.map(org => (
                        <Select.Option key={org.id} value={org.id}>
                          {org.name}
                        </Select.Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <Form.Item 
                    name="root_position_id" 
                    label="Корневая должность"
                  >
                    <Select 
                      allowClear
                      placeholder="Выберите должность"
                      style={{ width: '100%' }}
                      showSearch
                      optionFilterProp="children"
                    >
                      {positionOptions.map(pos => (
                        <Select.Option key={pos.value} value={pos.value}>
                          {pos.label}
                        </Select.Option>
                      ))}
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} sm={12} md={8}>
                  <Form.Item 
                    name="depth" 
                    label="Глубина дерева"
                    help="Оставьте пустым для отображения полного дерева"
                  >
                    <InputNumber 
                      min={0} 
                      max={10}
                      placeholder="Глубина"
                      style={{ width: '100%' }}
                    />
                  </Form.Item>
                </Col>
              </Row>
              <Row justify="end" gutter={16}>
                <Col>
                  <Button onClick={handleFilterReset}>
                    Сбросить
                  </Button>
                </Col>
                <Col>
                  <Button type="primary" htmlType="submit">
                    Применить
                  </Button>
                </Col>
              </Row>
            </Form>
          </Card>
        )}
        
        {error && <Alert message={error} type="error" showIcon closable onClose={() => setError(null)} />} 

        <div style={{ height: 'calc(85vh - 100px)', border: '1px solid #d9d9d9', background: 'white' }}>
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
              <Spin size="large" tip="Загрузка схемы..." />
            </div>
          ) : (
            <ReactFlowProvider> 
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={{ custom: CustomNode }}
                fitView
                // fitViewOptions={{ padding: 0.1 }}
              >
                <Controls />
                <MiniMap nodeStrokeWidth={3} zoomable pannable />
                <Background gap={16} />
              </ReactFlow>
            </ReactFlowProvider>
          )}
        </div>
      </Space>
    </div>
  );
};

export default StructureChartPage; 