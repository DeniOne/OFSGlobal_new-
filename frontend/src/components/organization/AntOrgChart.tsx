import React, { useEffect, useState } from 'react';
import { OrganizationTreeGraph } from '@ant-design/graphs';
import { Spin, Card, Empty, Space, Typography, Radio, Dropdown, Button, Tooltip } from 'antd';
import type { RadioChangeEvent } from 'antd';
import type { MenuProps } from 'antd';
import {
  ZoomInOutlined,
  ZoomOutOutlined,
  FullscreenOutlined,
  ExpandOutlined,
  CompressOutlined,
  ReloadOutlined,
  DownOutlined,
  TeamOutlined,
  BankOutlined,
  EnvironmentOutlined
} from '@ant-design/icons';
import { API_URL } from '../../config';

const { Title, Text } = Typography;

interface OrgNode {
  id: string;
  value: {
    name: string;
    position?: string;
    title?: string;
    email?: string;
    avatar?: string;
  };
  children?: OrgNode[];
}

interface AntOrgChartProps {
  organizationId: string;
  readOnly?: boolean;
  viewMode: 'business' | 'legal' | 'territorial';
  displayMode: 'tree' | 'list';
  zoomLevel?: number;
  detailLevel?: number;
}

const AntOrgChart: React.FC<AntOrgChartProps> = ({
  organizationId,
  readOnly = false,
  viewMode,
  displayMode,
  zoomLevel = 100,
  detailLevel = 1
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [data, setData] = useState<OrgNode | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentZoom, setCurrentZoom] = useState<number>(zoomLevel);
  const [currentMode, setCurrentMode] = useState<'business' | 'legal' | 'territorial'>(viewMode);
  const [expandAll, setExpandAll] = useState<boolean>(false);
  
  // Загрузка данных организационной структуры
  useEffect(() => {
    const fetchOrgData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Для демонстрации используем таймаут, в реальном приложении здесь будет API-запрос
        // const response = await fetch(`${API_URL}/organizations/${organizationId}/structure?view=${viewMode}`);
        
        // Моковые данные
        setTimeout(() => {
          const mockData: OrgNode = {
            id: '1',
            value: {
              name: 'Иванов И.И.',
              position: 'Генеральный директор',
              avatar: 'https://xsgames.co/randomusers/assets/avatars/male/1.jpg'
            },
            children: [
              {
                id: '2',
                value: {
                  name: 'Петров П.П.',
                  position: 'Финансовый директор',
                  avatar: 'https://xsgames.co/randomusers/assets/avatars/male/2.jpg'
                },
                children: [
                  {
                    id: '5',
                    value: {
                      name: 'Смирнова А.С.',
                      position: 'Главный бухгалтер',
                      avatar: 'https://xsgames.co/randomusers/assets/avatars/female/1.jpg'
                    }
                  },
                  {
                    id: '6',
                    value: {
                      name: 'Козлов В.Г.',
                      position: 'Финансовый аналитик',
                      avatar: 'https://xsgames.co/randomusers/assets/avatars/male/3.jpg'
                    }
                  }
                ]
              },
              {
                id: '3',
                value: {
                  name: 'Сидоров С.С.',
                  position: 'Технический директор',
                  avatar: 'https://xsgames.co/randomusers/assets/avatars/male/4.jpg'
                },
                children: [
                  {
                    id: '7',
                    value: {
                      name: 'Михайлов М.М.',
                      position: 'Руководитель разработки',
                      avatar: 'https://xsgames.co/randomusers/assets/avatars/male/5.jpg'
                    },
                    children: [
                      {
                        id: '10',
                        value: {
                          name: 'Алексеев А.А.',
                          position: 'Senior Developer',
                          avatar: 'https://xsgames.co/randomusers/assets/avatars/male/6.jpg'
                        }
                      },
                      {
                        id: '11',
                        value: {
                          name: 'Сергеев С.С.',
                          position: 'Middle Developer',
                          avatar: 'https://xsgames.co/randomusers/assets/avatars/male/7.jpg'
                        }
                      }
                    ]
                  },
                  {
                    id: '8',
                    value: {
                      name: 'Дмитриева Д.Д.',
                      position: 'QA Lead',
                      avatar: 'https://xsgames.co/randomusers/assets/avatars/female/2.jpg'
                    }
                  }
                ]
              },
              {
                id: '4',
                value: {
                  name: 'Николаев Н.Н.',
                  position: 'Директор по маркетингу',
                  avatar: 'https://xsgames.co/randomusers/assets/avatars/male/8.jpg'
                },
                children: [
                  {
                    id: '9',
                    value: {
                      name: 'Романова Р.Р.',
                      position: 'SMM менеджер',
                      avatar: 'https://xsgames.co/randomusers/assets/avatars/female/3.jpg'
                    }
                  }
                ]
              }
            ]
          };
          
          setData(mockData);
          setLoading(false);
        }, 1000);
        
      } catch (err: any) {
        setError(err.message || 'Ошибка при загрузке организационной структуры');
        setLoading(false);
      }
    };
    
    fetchOrgData();
  }, [organizationId, viewMode]);
  
  // Обработчик изменения режима отображения
  const handleModeChange = (e: RadioChangeEvent) => {
    setCurrentMode(e.target.value);
  };
  
  // Обработчик увеличения масштаба
  const handleZoomIn = () => {
    setCurrentZoom(prev => Math.min(prev + 10, 200));
  };
  
  // Обработчик уменьшения масштаба
  const handleZoomOut = () => {
    setCurrentZoom(prev => Math.max(prev - 10, 50));
  };
  
  // Обработчик сброса масштаба
  const handleResetZoom = () => {
    setCurrentZoom(100);
  };
  
  // Обработчик переключения развертывания/сворачивания всех узлов
  const handleToggleExpand = () => {
    setExpandAll(prev => !prev);
  };
  
  // Пункты меню для выбора режима отображения
  const items: MenuProps['items'] = [
    {
      key: 'business',
      label: 'Бизнес-структура',
      icon: <TeamOutlined />,
    },
    {
      key: 'legal',
      label: 'Юридическая структура',
      icon: <BankOutlined />,
    },
    {
      key: 'territorial',
      label: 'Территориальная структура',
      icon: <EnvironmentOutlined />,
    },
  ];
  
  // Обработчик выбора пункта меню
  const handleMenuClick: MenuProps['onClick'] = (e) => {
    setCurrentMode(e.key as 'business' | 'legal' | 'territorial');
  };
  
  // Настройки графа
  const config = {
    data,
    autoFit: true,
    nodeCfg: {
      size: [260, 120],
      style: {
        fill: '#1A1A20',
        stroke: '#9D6AF5',
        radius: 8,
        cursor: 'pointer',
      },
      nodeStateStyles: {
        hover: {
          stroke: '#b28aff',
          lineWidth: 2,
          shadowColor: 'rgba(157, 106, 245, 0.5)',
          shadowBlur: 10,
        },
        selected: {
          stroke: '#9D6AF5',
          lineWidth: 3,
          shadowColor: 'rgba(157, 106, 245, 0.8)',
          shadowBlur: 15,
        },
      },
      label: {
        style: {
          fill: '#fff',
          fontSize: 14,
          fontWeight: 500,
        }
      },
      // Кастомный рендер для узлов
      nodeCustomRender: (item: any, group: any, cfg: any) => {
        const { id, value } = cfg;
        const { name, position, avatar } = value;
        
        const keyShape = group.addShape('rect', {
          attrs: {
            x: 0,
            y: 0,
            width: 260,
            height: 120,
            fill: '#1A1A20',
            stroke: '#9D6AF5',
            radius: 8,
            shadowColor: 'rgba(0, 0, 0, 0.3)',
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowOffsetY: 5,
          },
          name: 'key-shape',
        });
        
        // Аватар
        if (avatar) {
          group.addShape('image', {
            attrs: {
              x: 15, 
              y: 30,
              width: 60,
              height: 60,
              img: avatar,
              radius: 30,
            },
            name: 'avatar-shape',
          });
          
          // Обводка аватара
          group.addShape('circle', {
            attrs: {
              x: 45,
              y: 60,
              r: 31,
              stroke: '#9D6AF5',
              lineWidth: 2,
              lineDash: [0, 0],
            },
            name: 'avatar-border-shape',
          });
        } else {
          // Заглушка если нет аватара
          group.addShape('circle', {
            attrs: {
              x: 45,
              y: 60,
              r: 30,
              fill: 'rgba(157, 106, 245, 0.7)',
              stroke: '#9D6AF5',
              lineWidth: 2,
            },
            name: 'avatar-placeholder-shape',
          });
          
          // Инициалы
          group.addShape('text', {
            attrs: {
              x: 45,
              y: 60,
              text: name.charAt(0),
              fontSize: 24,
              fill: '#fff',
              textAlign: 'center',
              textBaseline: 'middle',
              fontWeight: 'bold',
            },
            name: 'avatar-text-shape',
          });
        }
        
        // Имя сотрудника
        group.addShape('text', {
          attrs: {
            x: 130,
            y: 40,
            text: name,
            fontSize: 14,
            fill: '#fff',
            textAlign: 'center',
            textBaseline: 'middle',
            fontWeight: 'bold',
          },
          name: 'name-shape',
        });
        
        // Должность
        if (position) {
          group.addShape('rect', {
            attrs: {
              x: 95,
              y: 60,
              width: 150,
              height: 22,
              fill: 'rgba(0, 0, 0, 0.2)',
              radius: 4,
            },
            name: 'position-bg-shape',
          });
          
          group.addShape('text', {
            attrs: {
              x: 170,
              y: 71,
              text: position,
              fontSize: 12,
              fill: '#d0d0d0',
              textAlign: 'center',
              textBaseline: 'middle',
            },
            name: 'position-shape',
          });
        }
        
        return keyShape;
      }
    },
    edgeCfg: {
      style: {
        stroke: '#9D6AF5',
        lineWidth: 2,
        endArrow: true,
      },
      edgeStateStyles: {
        hover: {
          stroke: '#b28aff',
          lineWidth: 3,
        },
      },
    },
    markerCfg: {
      show: true,
      collapsed: {
        r: 8,
        fill: '#1A1A20',
        stroke: '#9D6AF5',
      },
      expanded: {
        r: 8,
        fill: '#9D6AF5',
        stroke: '#1A1A20',
      },
    },
    behaviors: readOnly 
      ? ['zoom-canvas', 'drag-canvas'] 
      : ['zoom-canvas', 'drag-canvas', 'drag-node'],
    animate: true,
    autoResize: true,
    defaultLevel: 3,
    defaultZoom: currentZoom / 100,
    fitCenter: true,
    minimapCfg: {
      show: true,
      size: [150, 100],
      type: 'keyShape',
      delegateStyle: {
        fill: 'rgba(157, 106, 245, 0.1)',
        stroke: '#9D6AF5',
      },
      refresh: true,
    },
  };
  
  return (
    <Card 
      style={{ 
        background: 'rgba(18, 18, 24, 0.5)', 
        borderRadius: 8, 
        border: '1px solid rgba(157, 106, 245, 0.2)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
        overflow: 'hidden',
        height: '100%',
        minHeight: '500px',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      {/* Панель управления */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        padding: '8px 16px', 
        borderBottom: '1px solid rgba(157, 106, 245, 0.2)',
        background: 'rgba(26, 26, 32, 0.7)'
      }}>
        <Space>
          <Title level={5} style={{ margin: 0, color: '#fff' }}>
            Организационная структура
          </Title>
          {error && (
            <Text type="danger" style={{ marginLeft: 8 }}>
              {error}
            </Text>
          )}
        </Space>
        
        <Space>
          <Dropdown menu={{ items, onClick: handleMenuClick }} placement="bottomRight">
            <Button>
              {currentMode === 'business' && 'Бизнес-структура'}
              {currentMode === 'legal' && 'Юридическая структура'}
              {currentMode === 'territorial' && 'Территориальная структура'}
              <DownOutlined style={{ marginLeft: 8 }} />
            </Button>
          </Dropdown>
          
          <Tooltip title="Увеличить">
            <Button icon={<ZoomInOutlined />} onClick={handleZoomIn} />
          </Tooltip>
          
          <Tooltip title="Уменьшить">
            <Button icon={<ZoomOutOutlined />} onClick={handleZoomOut} />
          </Tooltip>
          
          <Tooltip title="Сбросить масштаб">
            <Button icon={<FullscreenOutlined />} onClick={handleResetZoom} />
          </Tooltip>
          
          <Tooltip title={expandAll ? "Свернуть все" : "Развернуть все"}>
            <Button 
              icon={expandAll ? <CompressOutlined /> : <ExpandOutlined />} 
              onClick={handleToggleExpand} 
            />
          </Tooltip>
          
          <Tooltip title="Обновить">
            <Button icon={<ReloadOutlined />} onClick={() => setLoading(true)} />
          </Tooltip>
        </Space>
      </div>
      
      {/* Содержимое графа */}
      <div style={{ 
        flex: 1, 
        position: 'relative',
        backgroundColor: '#121215',
        backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(157, 106, 245, 0.1) 0%, transparent 80%)',
      }}>
        {loading ? (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%',
            minHeight: '400px' 
          }}>
            <Spin size="large" />
          </div>
        ) : data ? (
          <div style={{ height: '100%', minHeight: '400px' }}>
            <OrganizationTreeGraph {...config} />
          </div>
        ) : (
          <Empty 
            description="Нет данных для отображения" 
            image={Empty.PRESENTED_IMAGE_SIMPLE} 
            style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'center', 
              alignItems: 'center', 
              height: '100%',
              color: '#fff' 
            }} 
          />
        )}
      </div>
    </Card>
  );
};

export default AntOrgChart; 