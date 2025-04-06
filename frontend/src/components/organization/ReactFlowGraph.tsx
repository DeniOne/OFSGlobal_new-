import React, { useState, useCallback, useRef, useEffect, Suspense } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeTypes,
  EdgeTypes,
  NodeMouseHandler,
  NodeChange,
  EdgeChange,
  ConnectionLineType,
  Panel,
  MarkerType,
  useReactFlow,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Card, Modal, Input, Button, List, Checkbox, Tooltip, Typography, Space, Spin, FloatButton } from 'antd';
import { DeleteOutlined, PlusOutlined, EditOutlined, UserOutlined, CommentOutlined, SaveOutlined } from '@ant-design/icons';
import styled from '@emotion/styled';

// Импортируем типы
import { EntityType, RelationType, EntityNode, EntityRelation, Comment } from './types';

// Кастомный компонент узла (локальный импорт)
import CustomNode from './CustomNode';

// Тип данных для кастомного узла
interface CustomNodeData {
  label: string;
  position?: string;
  manager?: string;
  avatar?: string;
  comments?: Comment[];
  activeComments: number;
  borderColor: string;
  type: string;
}

// Стилизованный контейнер для графа
const GraphContainer = styled.div`
  width: 100%;
  height: 500px;
  background-color: rgba(26, 26, 30, 0.7);
  border-radius: 12px;
  border: 1px solid rgba(157, 106, 245, 0.2);
  overflow: hidden;
  position: relative;
  backdrop-filter: blur(4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
`;

// Цвета для разных типов связей
const RELATION_COLORS = {
  manager: '#ff8a00', // оранжевый
  department: '#ffffff', // белый
  functional: '#00b3ff', // голубой
  other: '#9D6AF5', // фиолетовый (по умолчанию)
};

// Интерфейс для пропсов компонента
export interface ReactFlowGraphProps {
  type: 'business' | 'legal' | 'territorial';
  nodes: EntityNode[];
  edges: EntityRelation[];
  selectedNodeId?: string | null;
  onNodeSelect?: (nodeId: string | null) => void;
  onNodeAdd?: (position: { x: number, y: number }) => void;
  onNodeDelete?: (nodeId: string) => void;
  onNodeUpdate?: (updatedNode: EntityNode) => void;
  onEdgeAdd?: (edge: { from: string, to: string, type: RelationType }) => void;
  onEdgeDelete?: (edgeId: string) => void;
  readOnly?: boolean;
  height?: number | string;
}

// Функция для сохранения комментариев узла
const saveNodeComments = (nodeId: string, type: string, comments: Comment[]) => {
  try {
    const key = `node_comments_${type}_${nodeId}`;
    localStorage.setItem(key, JSON.stringify(comments));
    console.log(`Комментарии для узла ${nodeId} сохранены в localStorage`);
  } catch (error) {
    console.error('Ошибка при сохранении комментариев в localStorage:', error);
  }
};

// Функция для загрузки комментариев узла
const loadNodeComments = (nodeId: string, type: string): Comment[] | null => {
  try {
    const key = `node_comments_${type}_${nodeId}`;
    const savedComments = localStorage.getItem(key);
    if (savedComments) {
      return JSON.parse(savedComments);
    }
  } catch (error) {
    console.error('Ошибка при загрузке комментариев из localStorage:', error);
  }
  return null;
};

// Функция для сохранения позиций узлов
const saveNodePositions = (nodes: Node[], type: string) => {
  try {
    const positions = nodes.map(node => ({
      id: node.id,
      position: node.position
    }));
    const key = `node_positions_${type}`;
    localStorage.setItem(key, JSON.stringify(positions));
    console.log(`Позиции узлов для типа ${type} сохранены в localStorage`);
  } catch (error) {
    console.error('Ошибка при сохранении позиций узлов в localStorage:', error);
  }
};

// Функция для загрузки позиций узлов
const loadNodePositions = (type: string): Record<string, { x: number; y: number }> => {
  try {
    const key = `node_positions_${type}`;
    const savedPositions = localStorage.getItem(key);
    if (savedPositions) {
      const positions = JSON.parse(savedPositions);
      const positionsMap: Record<string, { x: number; y: number }> = {};
      positions.forEach((item: { id: string; position: { x: number; y: number } }) => {
        positionsMap[item.id] = item.position;
      });
      console.log(`Позиции узлов для типа ${type} загружены из localStorage`);
      return positionsMap;
    }
  } catch (error) {
    console.error('Ошибка при загрузке позиций узлов из localStorage:', error);
  }
  return {};
};

// Функция для преобразования EntityNode в Node для ReactFlow
const entityNodeToReactFlowNode = (node: EntityNode, allEdges: EntityRelation[]): Node => {
  // Загружаем комментарии из localStorage, если они есть
  const savedComments = loadNodeComments(node.id, node.type);
  if (savedComments && (!node.comments || node.comments.length === 0)) {
    node.comments = savedComments;
  }
  
  // Если комментарии в старом формате (строки), конвертируем в новый формат (объекты)
  if (node.comments && typeof node.comments[0] === 'string') {
    node.comments = (node.comments as unknown as string[]).map(text => ({
      text,
      completed: false,
      date: new Date().toISOString()
    }));
  }
  
  // Определяем цвет на основе входящих связей
  const incomingEdge = allEdges.find(edge => edge.to === node.id);
  const borderColor = !incomingEdge ? '#9D6AF5' : 
    RELATION_COLORS[incomingEdge.type] || RELATION_COLORS.other;
  
  // Считаем количество активных комментариев
  const activeComments = node.comments ? 
    node.comments.filter(c => !c.completed).length : 0;
  
  return {
    id: node.id,
    position: { x: 0, y: 0 }, // Начальная позиция, будет изменена позже
    type: 'customNode',
    data: {
      label: node.name,
      position: node.position,
      staff: node.manager,
      avatar: node.avatar,
      comments: node.comments,
      activeComments,
      borderColor,
      type: node.type
    }
  };
};

// Функция для преобразования EntityRelation в Edge для ReactFlow
const entityRelationToReactFlowEdge = (relation: EntityRelation): Edge => {
  const edgeColor = RELATION_COLORS[relation.type] || RELATION_COLORS.other;
  const dashed = relation.type === 'functional';
  
  return {
    id: relation.id,
    source: relation.from,
    target: relation.to,
    type: 'smoothstep',
    animated: relation.type === 'functional',
    style: { 
      stroke: edgeColor, 
      strokeWidth: 2,
      strokeDasharray: dashed ? '5 5' : undefined 
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 15,
      height: 15,
      color: edgeColor,
    },
    label: relation.label,
    labelStyle: { 
      fill: '#fff', 
      fontWeight: 500, 
      fontSize: 10,
      filter: 'drop-shadow(0px 0px 1px rgba(0,0,0,0.7))'
    },
    labelBgStyle: { 
      fill: 'rgba(0,0,0,0.5)', 
      fillOpacity: 0.7,
    },
    data: { type: relation.type }
  };
};

// Реализация для экспорта графа как изображение
const exportGraphAsImage = async (reactFlowInstance: any) => {
  try {
    // Загружаем библиотеку html2canvas динамически
    const html2canvas = await import('html2canvas');
    
    // Получаем DOM-элемент с графом
    const nodesBounds = reactFlowInstance.getNodes().reduce(
      (bounds: any, node: Node) => {
        const nodeBounds = {
          x: node.position.x,
          y: node.position.y,
          width: 250, // приблизительная ширина узла
          height: 100, // приблизительная высота узла
        };
        
        bounds.left = Math.min(bounds.left, nodeBounds.x);
        bounds.top = Math.min(bounds.top, nodeBounds.y);
        bounds.right = Math.max(bounds.right, nodeBounds.x + nodeBounds.width);
        bounds.bottom = Math.max(bounds.bottom, nodeBounds.y + nodeBounds.height);
        
        return bounds;
      },
      { left: Infinity, top: Infinity, right: -Infinity, bottom: -Infinity }
    );
    
    // Получаем viewport
    const viewport = reactFlowInstance.getViewport();
    
    // Экспортируем изображение
    const flowElement = document.querySelector('.react-flow');
    if (flowElement) {
      const canvas = await html2canvas.default(flowElement as HTMLElement);
      const dataUrl = canvas.toDataURL('image/png');
      
      // Создаем ссылку для скачивания
      const a = document.createElement('a');
      a.href = dataUrl;
      a.download = 'organization-chart.png';
      a.click();
    }
  } catch (error) {
    console.error('Ошибка при экспорте графа:', error);
  }
};

// Кастомные типы узлов - ВЫНЕСЕНЫ ЗА ПРЕДЕЛЫ КОМПОНЕНТА
const nodeTypes: NodeTypes = {
  customNode: CustomNode,
};

const ReactFlowGraph: React.FC<ReactFlowGraphProps> = ({
  type,
  nodes: initialNodes,
  edges: initialEdges,
  selectedNodeId,
  onNodeSelect,
  onNodeAdd,
  onNodeDelete,
  onNodeUpdate,
  onEdgeAdd,
  onEdgeDelete,
  readOnly = false,
  height = 500,
}) => {
  // Состояние для узлов и связей
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isLoading, setIsLoading] = useState(true);
  
  // Состояние для редактирования узла
  const [nodeEditDialogOpen, setNodeEditDialogOpen] = useState(false);
  const [currentEditNode, setCurrentEditNode] = useState<EntityNode | null>(null);
  const [editNodeName, setEditNodeName] = useState('');
  const [editNodePosition, setEditNodePosition] = useState('');
  const [editNodeManager, setEditNodeManager] = useState('');
  
  // Состояние для комментариев
  const [commentDialogOpen, setCommentDialogOpen] = useState(false);
  const [newComment, setNewComment] = useState('');
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const reactFlowInstance = useReactFlow();

  // Инициализация графа при изменении входных данных
  useEffect(() => {
    if (initialNodes && initialEdges) {
      // Преобразуем узлы
      const flowNodes = initialNodes.map(node => 
        entityNodeToReactFlowNode(node, initialEdges)
      );
      
      // Загружаем сохраненные позиции из localStorage
      const savedPositions = loadNodePositions(type);
      
      // Устанавливаем позиции узлов, используя сохраненные или дефолтные
      const positionedNodes = flowNodes.map((node, index) => {
        if (savedPositions[node.id]) {
          // Используем сохраненную позицию
          return {
            ...node,
            position: savedPositions[node.id]
          };
        } else {
          // Используем дефолтную позицию в виде сетки
          return {
            ...node,
            position: { 
              x: 100 + (index % 3) * 300, 
              y: 100 + Math.floor(index / 3) * 180 
            }
          };
        }
      });
      
      // Преобразуем связи
      const flowEdges = initialEdges.map(edge => 
        entityRelationToReactFlowEdge(edge)
      );
      
      setNodes(positionedNodes);
      setEdges(flowEdges);
      setIsLoading(false);
    }
  }, [initialNodes, initialEdges, type, setNodes, setEdges]);
  
  // Выделение узла
  useEffect(() => {
    if (selectedNodeId) {
      setNodes(nds => 
        nds.map(node => ({
          ...node,
          selected: node.id === selectedNodeId,
        }))
      );
    }
  }, [selectedNodeId, setNodes]);
  
  // Сохраняем позиции при изменении узлов
  const handleNodesChange = useCallback((changes: NodeChange[]) => {
    onNodesChange(changes);
    
    // Сохраняем позиции с небольшой задержкой, чтобы избежать частых записей при перетаскивании
    setTimeout(() => {
      const currentNodes = reactFlowInstance.getNodes();
      saveNodePositions(currentNodes, type);
    }, 500);
  }, [onNodesChange, reactFlowInstance, type]);
  
  // Обработчик клика по узлу
  const onNodeClick: NodeMouseHandler = useCallback((event, node) => {
    if (onNodeSelect) {
      onNodeSelect(node.id);
    }
  }, [onNodeSelect]);
  
  // Обработчик двойного клика по узлу
  const onNodeDoubleClick: NodeMouseHandler = useCallback((event, node) => {
    const entityNode = initialNodes.find(n => n.id === node.id);
    if (entityNode) {
      setCurrentEditNode(entityNode);
      setEditNodeName(entityNode.name);
      setEditNodePosition(entityNode.position || '');
      setEditNodeManager(entityNode.manager || '');
      setNodeEditDialogOpen(true);
    }
  }, [initialNodes]);
  
  // Обработчик добавления связи
  const onConnect = useCallback((params: Connection) => {
    if (params.source && params.target && onEdgeAdd) {
      const newEdge = {
        from: params.source,
        to: params.target,
        type: 'other' as RelationType
      };
      
      onEdgeAdd(newEdge);
    }
  }, [onEdgeAdd]);
  
  // Обработчик удаления узла
  const handleDeleteNode = useCallback(() => {
    if (currentEditNode && onNodeDelete) {
      onNodeDelete(currentEditNode.id);
      setNodeEditDialogOpen(false);
      setCurrentEditNode(null);
    }
  }, [currentEditNode, onNodeDelete]);
  
  // Обработчик сохранения изменений узла
  const handleSaveNodeEdit = useCallback(() => {
    if (currentEditNode && onNodeUpdate) {
      const updatedNode: EntityNode = {
        ...currentEditNode,
        name: editNodeName,
        position: editNodePosition,
        manager: editNodeManager
      };
      
      onNodeUpdate(updatedNode);
      setNodeEditDialogOpen(false);
      setCurrentEditNode(null);
    }
  }, [currentEditNode, editNodeName, editNodePosition, editNodeManager, onNodeUpdate]);
  
  // Обработчик клика по пустому месту для добавления нового узла
  const onPaneClick = useCallback((event: any) => {
    if (!readOnly && reactFlowWrapper.current && onNodeAdd) {
      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });
      onNodeAdd(position);
    }
  }, [readOnly, reactFlowInstance, onNodeAdd]);

  // Обработчик клика на кнопку добавления узла
  const handleAddNodeBtnClick = useCallback(() => {
    if (onNodeAdd) {
      // Добавляем узел в центр видимой области
      const viewport = reactFlowInstance.getViewport();
      const center = reactFlowInstance.project({
        x: reactFlowWrapper.current ? reactFlowWrapper.current.clientWidth / 2 : 300,
        y: reactFlowWrapper.current ? reactFlowWrapper.current.clientHeight / 2 : 200,
      });
      onNodeAdd(center);
    }
  }, [reactFlowInstance, onNodeAdd]);
  
  // Обработчик открытия диалога комментариев
  const handleOpenCommentDialog = (node: EntityNode) => {
    setCurrentEditNode(node);
    setCommentDialogOpen(true);
    setNewComment('');
  };
  
  // Обработчик добавления комментария
  const handleAddComment = () => {
    if (currentEditNode && newComment.trim() && onNodeUpdate) {
      const newCommentObj: Comment = {
        text: newComment.trim(),
        completed: false,
        date: new Date().toISOString()
      };
      
      const updatedComments = currentEditNode.comments 
        ? [...currentEditNode.comments, newCommentObj] 
        : [newCommentObj];
      
      const updatedNode: EntityNode = {
        ...currentEditNode,
        comments: updatedComments
      };
      
      // Сохраняем комментарии в localStorage
      saveNodeComments(currentEditNode.id, currentEditNode.type, updatedComments);
      
      // Обновляем узел
      onNodeUpdate(updatedNode);
      setNewComment('');
    }
  };
  
  // Обработчик изменения статуса комментария
  const handleToggleCommentStatus = (commentIndex: number) => {
    if (currentEditNode && currentEditNode.comments && onNodeUpdate) {
      const updatedComments = [...currentEditNode.comments];
      updatedComments[commentIndex] = {
        ...updatedComments[commentIndex],
        completed: !updatedComments[commentIndex].completed
      };
      
      const updatedNode: EntityNode = {
        ...currentEditNode,
        comments: updatedComments
      };
      
      // Сохраняем комментарии в localStorage
      saveNodeComments(currentEditNode.id, currentEditNode.type, updatedComments);
      
      // Обновляем узел
      onNodeUpdate(updatedNode);
    }
  };
  
  return (
    <GraphContainer ref={reactFlowWrapper} style={{ height: height }}>
      {isLoading ? (
        <Space 
          style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%' 
          }}
        >
          <Spin />
        </Space>
      ) : (
        <>
          {/* Основной граф */}
          <Space style={{ height: '100%' }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={handleNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              nodeTypes={nodeTypes}
              onNodeClick={onNodeClick}
              onNodeDoubleClick={onNodeDoubleClick}
              fitView
              snapToGrid
              snapGrid={[15, 15]}
              defaultViewport={{ x: 0, y: 0, zoom: 1 }}
              onPaneClick={onPaneClick}
              zoomOnDoubleClick={false}
              connectionLineType={ConnectionLineType.SmoothStep}
              connectionLineStyle={{ stroke: '#9D6AF5', strokeWidth: 2 }}
              defaultEdgeOptions={{ 
                type: 'smoothstep',
                markerEnd: { type: MarkerType.ArrowClosed }, 
                style: { stroke: '#9D6AF5', strokeWidth: 2 }
              }}
            >
              <Background color="#1a1a1e" gap={20} />
              <Controls 
                showInteractive={false} 
                position="bottom-right"
                style={{ 
                  display: 'flex', 
                  flexDirection: 'column',
                  background: 'rgba(26, 26, 34, 0.9)',
                  borderRadius: '8px',
                  border: '1px solid rgba(157, 106, 245, 0.3)',
                  padding: '8px' 
                }}
              />
              
              {!readOnly && (
                <Panel position="top-right" style={{ display: 'flex', gap: '10px' }}>
                  <FloatButton
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={handleAddNodeBtnClick}
                    tooltip="Добавить узел"
                    style={{
                      background: 'linear-gradient(45deg, #9D6AF5, #b350ff)',
                      boxShadow: '0 4px 10px rgba(157, 106, 245, 0.5)',
                    }}
                    onMouseEnter={(e) => {
                      const target = e.currentTarget as HTMLButtonElement;
                      target.style.background = 'linear-gradient(45deg, #a478f5, #c070ff)';
                    }}
                    onMouseLeave={(e) => {
                      const target = e.currentTarget as HTMLButtonElement;
                      target.style.background = 'linear-gradient(45deg, #9D6AF5, #b350ff)';
                    }}
                  />
                  
                  <FloatButton
                    type="primary"
                    icon={<SaveOutlined />}
                    onClick={() => exportGraphAsImage(reactFlowInstance)}
                    tooltip="Экспортировать как изображение"
                    style={{
                      background: 'linear-gradient(45deg, #3a8af5, #50a0ff)',
                      boxShadow: '0 4px 10px rgba(58, 138, 245, 0.5)',
                    }}
                    onMouseEnter={(e) => {
                      const target = e.currentTarget as HTMLButtonElement;
                      target.style.background = 'linear-gradient(45deg, #4a95f5, #60b0ff)';
                    }}
                    onMouseLeave={(e) => {
                      const target = e.currentTarget as HTMLButtonElement;
                      target.style.background = 'linear-gradient(45deg, #3a8af5, #50a0ff)';
                    }}
                  />
                </Panel>
              )}
            </ReactFlow>
          </Space>
        </>
      )}
      
      {/* Диалог редактирования узла */}
      <Modal
        open={nodeEditDialogOpen}
        onCancel={() => setNodeEditDialogOpen(false)}
        footer={null}
      >
        <Space direction="vertical" size={16}>
          <Space direction="horizontal" size={16}>
            <Input
              placeholder="Имя"
              value={editNodeName}
              onChange={(e) => setEditNodeName(e.target.value)}
            />
            <Input
              placeholder="Должность"
              value={editNodePosition}
              onChange={(e) => setEditNodePosition(e.target.value)}
            />
            <Input
              placeholder="Руководитель"
              value={editNodeManager}
              onChange={(e) => setEditNodeManager(e.target.value)}
            />
          </Space>
          
          {currentEditNode && (
            <Space direction="horizontal" size={16}>
              <Button 
                icon={<CommentOutlined />}
                onClick={() => {
                  if (currentEditNode) {
                    handleOpenCommentDialog(currentEditNode);
                    setNodeEditDialogOpen(false);
                  }
                }}
              >
                Управление комментариями
              </Button>
            </Space>
          )}
        </Space>
        <Space direction="horizontal" size={16} style={{ marginTop: 16 }}>
          {!readOnly && (
            <Button 
              icon={<DeleteOutlined />}
              onClick={handleDeleteNode}
              danger
            >
              Удалить
            </Button>
          )}
          <Button onClick={() => setNodeEditDialogOpen(false)}>Отмена</Button>
          <Button onClick={handleSaveNodeEdit} type="primary">Сохранить</Button>
        </Space>
      </Modal>
      
      {/* Диалог управления комментариями */}
      <Modal
        open={commentDialogOpen}
        onCancel={() => setCommentDialogOpen(false)}
        footer={null}
        width={600}
      >
        <Space direction="vertical" size={16}>
          <Space direction="horizontal" size={16}>
            <Input.TextArea
              placeholder="Новый комментарий"
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              rows={4}
            />
            <Button 
              onClick={handleAddComment} 
              type="primary"
              disabled={!newComment.trim()}
            >
              Добавить
            </Button>
          </Space>
          
          <Space direction="horizontal" size={16}>
            <Typography.Text>
              Список комментариев:
            </Typography.Text>
          </Space>
          
          <List>
            {currentEditNode?.comments?.map((comment, index) => (
              <List.Item 
                key={index}
                style={{
                  backgroundColor: 'rgba(26, 26, 30, 0.7)',
                  marginBottom: 8,
                  borderRadius: 4,
                  border: '1px solid rgba(157, 106, 245, 0.2)'
                }}
              >
                <Space direction="horizontal" size={8}>
                  <Checkbox
                    checked={comment.completed}
                    onChange={() => handleToggleCommentStatus(index)}
                  />
                  <Typography.Text
                    style={{
                      textDecoration: comment.completed ? 'line-through' : 'none',
                      color: comment.completed ? 'text.disabled' : 'text.primary'
                    }}
                  >
                    {comment.text}
                  </Typography.Text>
                </Space>
              </List.Item>
            ))}
            
            {(!currentEditNode?.comments || currentEditNode.comments.length === 0) && (
              <Space direction="horizontal" size={16} style={{ padding: 16, backgroundColor: 'rgba(26, 26, 30, 0.7)' }}>
                <Typography.Text>
                  Нет комментариев
                </Typography.Text>
              </Space>
            )}
          </List>
        </Space>
        <Space direction="horizontal" size={16} style={{ marginTop: 16 }}>
          <Button onClick={() => setCommentDialogOpen(false)}>Закрыть</Button>
        </Space>
      </Modal>
    </GraphContainer>
  );
};

export default ReactFlowGraph; 
