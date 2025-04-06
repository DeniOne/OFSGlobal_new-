import React, { useState, useEffect, useCallback, useRef, useLayoutEffect } from 'react';
import {
  Spin,
  message,
  Typography,
  Space,
  Button,
  Alert
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
// Если @react-flow/core не экспортирует ReactFlow и т.д., пробуем @react-flow/react-renderer
// import ReactFlow, {
//   ReactFlowProvider,
//   useNodesState,
//   useEdgesState,
//   Controls,
//   MiniMap,
//   Background,
// } from '@react-flow/react-renderer';

import api from '../services/api';
import dagre from 'dagre';

const { Title } = Typography;

// Интерфейсы для данных с бэкенда (можно взять из других страниц)
interface Division { id: number; name: string; parent_id?: number | null; code?: string; /* ... другие поля */ }
interface Position { id: number; name: string; division_id?: number | null; parent_id?: number | null; code?: string; /* ... */ }
interface Staff { id: number; last_name: string; first_name: string; /* ... */ }
interface FunctionalRelation { 
    id: number; 
    source_type: string; source_id: number; 
    target_type: string; target_id: number; 
    relation_type: string; 
    /* ... */ 
}

// Размеры узлов для dagre
const nodeWidth = 172;
const nodeHeight = 50;

// Функция для создания графа dagre и расчета позиций
const getLayoutedElements = (nodes: any[], edges: any[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({ rankdir: direction });

  const nodeIds = new Set(nodes.map(n => n.id)); // Сохраняем ID всех узлов

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    // Добавляем ребро в dagre только если оба узла существуют
    if (nodeIds.has(edge.source) && nodeIds.has(edge.target)) {
      dagreGraph.setEdge(edge.source, edge.target);
    } else {
        console.warn(`[LOG:Chart] Dagre: Skipped edge ${edge.id} because source or target node not found.`);
    }
  });

  // Оборачиваем layout в try...catch
  try {
      dagre.layout(dagreGraph);
  } catch (layoutError) {
      console.error("[LOG:Chart] Dagre layout error:", layoutError);
      // Возвращаем узлы без позиций или с дефолтными, чтобы избежать падения дальше
      // Можно добавить маркер ошибки в данные узла
       nodes.forEach(node => {
           node.data.layoutError = true; 
           node.position = { x: Math.random() * 400, y: Math.random() * 400 }; // Случайные позиции для отладки
       });
       message.error('Ошибка автоматической раскладки схемы.');
      return { nodes, edges }; // Возвращаем исходные ребра и узлы с ошибкой
  }
  
  // Расчет позиций узлов react-flow
  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    if (nodeWithPosition) { // Проверяем, что узел найден в графе dagre
        node.targetPosition = RFPosition.Top;
        node.sourcePosition = RFPosition.Bottom;
        node.position = {
            x: nodeWithPosition.x - nodeWidth / 2,
            y: nodeWithPosition.y - nodeHeight / 2,
        };
        delete node.data.layoutError; // Удаляем маркер ошибки, если был
    } else {
        // Если узел не найден в dagre (не должно случиться при правильной логике)
        console.warn(`[LOG:Chart] Node ${node.id} not found in dagre graph after layout.`);
        node.position = { x: 0, y: 0 }; 
    }
    return node;
  });

  return { nodes, edges };
};

// Стили узлов
const baseNodeStyle = {
    border: '1px solid',
    padding: '10px 15px',
    borderRadius: '4px',
    background: 'white',
    width: nodeWidth,
    // height: nodeHeight, // Высота может меняться
    textAlign: 'center' as const,
    fontSize: '12px'
};

const divisionNodeStyle = { ...baseNodeStyle, borderColor: '#1890ff' };
const positionNodeStyle = { ...baseNodeStyle, borderColor: '#52c41a' };

const StructureChartPage: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Функция трансформации данных
  const transformDataToFlow = useCallback((divisions: Division[], positions: Position[]) => {
      const flowNodes: any[] = [];
      const flowEdges: any[] = [];
      const nodeIds = new Set<string>(); // Для проверки существования узлов перед добавлением ребер

      // 1. Создаем узлы для Подразделений
      divisions.forEach(div => {
          const nodeId = `div-${div.id}`;
          flowNodes.push({
              id: nodeId,
              data: { label: div.name, type: 'division', code: div.code },
              position: { x: 0, y: 0 }, 
              style: divisionNodeStyle,
          });
          nodeIds.add(nodeId);
      });

      // 2. Создаем узлы для Должностей
      positions.forEach(pos => {
          const nodeId = `pos-${pos.id}`;
          flowNodes.push({
              id: nodeId,
              data: { label: pos.name, type: 'position', code: pos.code },
              position: { x: 0, y: 0 }, 
              style: positionNodeStyle,
          });
           nodeIds.add(nodeId);
      });
      
      // 3. Создаем ребра для Подразделений (после создания всех узлов)
      divisions.forEach(div => {
           if (div.parent_id) {
              const sourceId = `div-${div.parent_id}`;
              const targetId = `div-${div.id}`;
              // Проверяем существование узлов и отсутствие петли
              if (nodeIds.has(sourceId) && nodeIds.has(targetId) && sourceId !== targetId) {
                  flowEdges.push({
                      id: `e_div_${div.parent_id}_${div.id}`,
                      source: sourceId,
                      target: targetId,
                      type: 'smoothstep',
                      markerEnd: { type: MarkerType.ArrowClosed },
                      style: { stroke: '#aaa' }
                  });
              } else {
                   console.warn(`[LOG:Chart] Edge skipped: div parent relation ${sourceId} -> ${targetId} (nodes exist: ${nodeIds.has(sourceId)}, ${nodeIds.has(targetId)})`);
              }
          }
      });
      
       // 4. Создаем ребра для Должностей (после создания всех узлов)
       positions.forEach(pos => {
           // Ребро к родительской должности
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
                } else {
                    console.warn(`[LOG:Chart] Edge skipped: pos parent relation ${sourceId} -> ${targetId} (nodes exist: ${nodeIds.has(sourceId)}, ${nodeIds.has(targetId)})`);
                }
            }
            // Ребро к подразделению
            if (pos.division_id) {
                 const sourceId = `div-${pos.division_id}`;
                 const targetId = `pos-${pos.id}`;
                 if (nodeIds.has(sourceId) && nodeIds.has(targetId) && sourceId !== targetId) {
                     flowEdges.push({
                        id: `e_div_${pos.division_id}_pos_${pos.id}`,
                        source: sourceId,
                        target: targetId,
                        type: 'smoothstep',
                        markerEnd: { type: MarkerType.ArrowClosed, color: '#1890ff' },
                        style: { stroke: '#1890ff' } 
                    });
                 } else {
                     console.warn(`[LOG:Chart] Edge skipped: pos division relation ${sourceId} -> ${targetId} (nodes exist: ${nodeIds.has(sourceId)}, ${nodeIds.has(targetId)})`);
                 }
            }
        });

      // TODO: Можно добавить обработку functional_relations для других типов связей

      return { nodes: flowNodes, edges: flowEdges };

  }, []);

  // Загрузка и обработка данных
  const fetchData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setLoading(true);
    try {
      // Загружаем все необходимые данные
      const [divResponse, posResponse, staffResponse, relResponse] = await Promise.all([
        api.get('/divisions/', { signal }),
        api.get('/positions/', { signal }),
        api.get('/staff/', { signal }),
        api.get('/functional-relations/', { signal })
      ]);
      
      const divisions: Division[] = divResponse.data;
      const positions: Position[] = posResponse.data;
      const staff: Staff[] = staffResponse.data;
      const relations: FunctionalRelation[] = relResponse.data;

      console.log('[LOG:Chart] Data loaded:', { divisions, positions, staff, relations });

      // Трансформируем данные
      const { nodes: initialNodes, edges: initialEdges } = transformDataToFlow(divisions, positions);

      if (initialNodes.length === 0) {
          message.info('Нет данных для отображения схемы (подразделения или должности отсутствуют).');
           setNodes([{ id: 'empty', position: { x: 0, y: 0 }, data: { label: 'Нет данных' }, style: baseNodeStyle }]);
           setEdges([]);
           return; // Выходим, если данных нет
      }

      // Рассчитываем позиции с помощью dagre
      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        initialNodes,
        initialEdges
      );

      // Проверяем, была ли ошибка в layout
      const layoutHasError = layoutedNodes.some(node => node.data.layoutError);
      
      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
      
      // Показываем success только если не было ошибки layout
      if (!layoutHasError) {
          message.success('Схема структуры построена.');
      } 
      // message.error об ошибке layout покажется внутри getLayoutedElements

    } catch (error: any) {
      // Игнорируем ошибки отмены запроса
      if (error.name !== 'AbortError') {
          console.error('[LOG:Chart] Ошибка при загрузке или обработке данных:', error);
          message.error('Ошибка при построении схемы.');
           setNodes([{ id: 'error', position: { x: 0, y: 0 }, data: { label: 'Ошибка построения схемы' }, style: { ...baseNodeStyle, borderColor: 'red' } }]);
           setEdges([]);
      } else {
          console.log('[LOG:Chart] Fetch aborted, ignoring.'); // Логируем отмену
      }
    } finally {
       if (!signal.aborted) {
          setLoading(false);
          abortControllerRef.current = null;
      }
    }
  }, [setNodes, setEdges, transformDataToFlow]);

  // Используем useLayoutEffect для запуска fitView после рендера и расчета layout
  useLayoutEffect(() => {
      // Тут можно было бы вызвать fitView, но react-flow v11 делает это автоматически при initial Nodes/Edges
      // Если авто-масштабирование не сработает, можно будет добавить instance.fitView()
  }, [nodes, edges]); // Зависит от nodes и edges

  useEffect(() => {
    fetchData();
    return () => {
      abortControllerRef.current?.abort();
    };
  }, [fetchData]);

  return (
    <Space direction="vertical" style={{ width: '100%', height: 'calc(100vh - 150px)', display: 'flex', flexDirection: 'column' }}>
      <Title level={2}>Визуальная схема структуры</Title>
      <Space style={{ marginBottom: 16 }}>
        <Button icon={<ReloadOutlined />} onClick={fetchData} loading={loading}>
          Обновить данные
        </Button>
         {/* Можно добавить кнопки для управления раскладкой, если будем использовать dagre */} 
      </Space>

       <Alert 
          message="Информация"
          description="Отображены подразделения (синие) и должности (зеленые). Связи: родительское подразделение (серое), родительская должность (зеленое), принадлежность должности к подразделению (синее)."
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />
        
      <div style={{ flexGrow: 1, width: '100%', height: '800px', position: 'relative' }}>
        {loading && (
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            background: 'rgba(255, 255, 255, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10
          }}>
            <Spin size="large" />
          </div>
        )}
        <ReactFlowProvider> 
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            style={{ width: '100%', height: '100%', background: '#f9f9f9' }}
            proOptions={{ hideAttribution: true }}
          >
            <Controls />
            <MiniMap nodeStrokeWidth={3} zoomable pannable />
            <Background gap={16} />
          </ReactFlow>
        </ReactFlowProvider>
      </div>
    </Space>
  );
};

export default StructureChartPage; 