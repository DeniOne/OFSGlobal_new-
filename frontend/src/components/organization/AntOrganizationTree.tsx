import React, { useEffect, useState } from 'react';
import { Spin, Card, Empty, Space, Typography, message } from 'antd';
import { TeamOutlined, BankOutlined, EnvironmentOutlined } from '@ant-design/icons';
import { API_URL } from '../../config';

// Динамический импорт с обработкой ошибок для работы без установленного пакета
let OrganizationTreeGraph: any = null;
try {
  // Пытаемся импортировать библиотеку
  ({ OrganizationTreeGraph } = require('@ant-design/graphs'));
} catch (error) {
  console.error('Failed to load @ant-design/graphs:', error);
}

const { Title } = Typography;

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

interface AntOrganizationTreeProps {
  organizationId: string;
  readOnly?: boolean;
  viewMode: 'business' | 'legal' | 'territorial';
  displayMode: 'tree' | 'list';
  zoomLevel?: number;
  detailLevel?: number;
}

const AntOrganizationTree: React.FC<AntOrganizationTreeProps> = ({
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
  
  // Загрузка данных организационной структуры
  useEffect(() => {
    const fetchOrgData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // В реальном проекте здесь будет API-запрос
        // const response = await fetch(`${API_URL}/organizations/${organizationId}/structure?view=${viewMode}`);
        
        // Моковые данные для демонстрации
        setTimeout(() => {
          const mockData: OrgNode = {
            id: '1',
            value: {
              name: 'Генеральный директор',
              position: 'CEO',
              avatar: 'https://xsgames.co/randomusers/assets/avatars/male/1.jpg'
            },
            children: [
              {
                id: '2',
                value: {
                  name: 'Финансовый директор',
                  position: 'CFO',
                  avatar: 'https://xsgames.co/randomusers/assets/avatars/male/2.jpg'
                },
                children: [
                  {
                    id: '5',
                    value: {
                      name: 'Главный бухгалтер',
                      position: 'Chief Accountant',
                      avatar: 'https://xsgames.co/randomusers/assets/avatars/female/1.jpg'
                    }
                  }
                ]
              },
              {
                id: '3',
                value: {
                  name: 'Технический директор',
                  position: 'CTO',
                  avatar: 'https://xsgames.co/randomusers/assets/avatars/male/4.jpg'
                },
                children: [
                  {
                    id: '7',
                    value: {
                      name: 'Руководитель разработки',
                      position: 'Head of Development',
                      avatar: 'https://xsgames.co/randomusers/assets/avatars/male/5.jpg'
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
    defaultZoom: zoomLevel / 100,
    fitCenter: true,
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
        ) : !OrganizationTreeGraph ? (
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column',
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%',
            color: '#fff',
            padding: '20px',
            textAlign: 'center'
          }}>
            <Title level={4} style={{ color: '#fff' }}>
              Ошибка загрузки графика
            </Title>
            <p>Не удалось загрузить компонент графика. Пожалуйста, установите пакет @ant-design/graphs:</p>
            <div style={{ 
              background: '#000', 
              padding: '12px 16px', 
              borderRadius: '4px',
              marginTop: '16px',
              fontFamily: 'monospace'
            }}>
              npm install @ant-design/graphs
            </div>
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

export default AntOrganizationTree; 