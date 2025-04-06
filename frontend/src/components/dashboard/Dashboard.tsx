import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Typography, Space, Avatar, Statistic, Progress, Divider, List, Button } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, UserOutlined, TeamOutlined, BarChartOutlined, PlusOutlined } from '@ant-design/icons';
import { gradients } from '../../theme';
import { Line } from '@ant-design/charts';
import { useQuery } from '@tanstack/react-query';
import api from '../../services/api';

const { Title, Text } = Typography;

interface EmployeeData {
  id: number;
  full_name: string;
  email: string;
  position: string;
}

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('departments');
  
  const { data: employees, isLoading } = useQuery({
    queryKey: ['employees'],
    queryFn: async () => {
      const response = await api.get('/employees/?skip=0&limit=5');
      return response.data;
    }
  });

  // Мок данных для графика активности
  const activityData = [
    { date: 'Пн', active: 38 },
    { date: 'Вт', active: 52 },
    { date: 'Ср', active: 61 },
    { date: 'Чт', active: 45 },
    { date: 'Пт', active: 48 },
    { date: 'Сб', active: 23 },
    { date: 'Вс', active: 18 },
  ];
  
  // График активности
  const activityConfig = {
    data: activityData,
    height: 200,
    xField: 'date',
    yField: 'active',
    point: {
      size: 5,
      shape: 'circle',
    },
    smooth: true,
    color: '#9D6AF5',
    areaStyle: {
      fill: 'l(270) 0:#9D6AF580 1:#9D6AF500',
    },
  };

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={[24, 24]}>
        <Col span={24}>
          <Title level={4} style={{ margin: 0, marginBottom: 24 }}>Аналитика организации</Title>
        </Col>

        {/* Статистические карточки */}
        <Col xs={24} md={12} lg={6}>
          <Card 
            style={{ 
              borderRadius: 16, 
              background: gradients.secondaryGradient,
              height: '100%' 
            }}
            bodyStyle={{ padding: 20 }}
          >
            <Statistic 
              title={<Text style={{ color: '#9D6AF5' }}>Сотрудники</Text>}
              value={182} 
              precision={0} 
              valueStyle={{ color: '#fff', fontSize: 28, fontWeight: 'bold' }} 
              prefix={<TeamOutlined style={{ marginRight: 8 }} />}
            />
            <div style={{ display: 'flex', alignItems: 'center', marginTop: 16 }}>
              <div style={{ flexGrow: 1 }}>
                <Progress 
                  percent={78} 
                  size="small" 
                  showInfo={false}
                  strokeColor={{
                    '0%': '#9D6AF5',
                    '100%': '#7947c2',
                  }}
                />
              </div>
              <Text style={{ color: '#52C41A', marginLeft: 10 }}>
                <ArrowUpOutlined /> +7.5%
              </Text>
            </div>
            <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>Прирост за квартал</Text>
          </Card>
        </Col>
        
        <Col xs={24} md={12} lg={6}>
          <Card 
            style={{ 
              borderRadius: 16, 
              background: gradients.secondaryGradient,
              height: '100%' 
            }}
            bodyStyle={{ padding: 20 }}
          >
            <Statistic 
              title={<Text style={{ color: '#9D6AF5' }}>Отделы</Text>}
              value={14} 
              precision={0} 
              valueStyle={{ color: '#fff', fontSize: 28, fontWeight: 'bold' }} 
              prefix={<BarChartOutlined style={{ marginRight: 8 }} />}
            />
            <div style={{ display: 'flex', alignItems: 'center', marginTop: 16 }}>
              <div style={{ flexGrow: 1 }}>
                <Progress 
                  percent={42} 
                  size="small" 
                  showInfo={false}
                  strokeColor={{
                    '0%': '#9D6AF5',
                    '100%': '#7947c2',
                  }}
                />
              </div>
              <Text style={{ color: '#FF5252', marginLeft: 10 }}>
                <ArrowDownOutlined /> -2.3%
              </Text>
            </div>
            <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>Оптимизация структуры</Text>
          </Card>
        </Col>
        
        <Col xs={24} md={12} lg={6}>
          <Card 
            style={{ 
              borderRadius: 16, 
              background: gradients.secondaryGradient,
              height: '100%' 
            }}
            bodyStyle={{ padding: 20 }}
          >
            <Statistic 
              title={<Text style={{ color: '#9D6AF5' }}>Активность</Text>}
              value={76.8} 
              precision={1} 
              valueStyle={{ color: '#fff', fontSize: 28, fontWeight: 'bold' }} 
              suffix="%"
            />
            <div style={{ display: 'flex', alignItems: 'center', marginTop: 16 }}>
              <div style={{ flexGrow: 1 }}>
                <Progress 
                  percent={76.8} 
                  size="small" 
                  showInfo={false}
                  strokeColor={{
                    '0%': '#9D6AF5',
                    '100%': '#7947c2',
                  }}
                />
              </div>
              <Text style={{ color: '#52C41A', marginLeft: 10 }}>
                <ArrowUpOutlined /> +12.4%
              </Text>
            </div>
            <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>В сравнении с прошлым месяцем</Text>
          </Card>
        </Col>
        
        <Col xs={24} md={12} lg={6}>
          <Card 
            style={{ 
              borderRadius: 16, 
              background: gradients.secondaryGradient,
              height: '100%' 
            }}
            bodyStyle={{ padding: 20 }}
          >
            <Statistic 
              title={<Text style={{ color: '#9D6AF5' }}>Эффективность</Text>}
              value={92.3} 
              precision={1} 
              valueStyle={{ color: '#fff', fontSize: 28, fontWeight: 'bold' }} 
              suffix="%"
            />
            <div style={{ display: 'flex', alignItems: 'center', marginTop: 16 }}>
              <div style={{ flexGrow: 1 }}>
                <Progress 
                  percent={92.3} 
                  size="small" 
                  showInfo={false}
                  strokeColor={{
                    '0%': '#9D6AF5',
                    '100%': '#7947c2',
                  }}
                />
              </div>
              <Text style={{ color: '#52C41A', marginLeft: 10 }}>
                <ArrowUpOutlined /> +3.7%
              </Text>
            </div>
            <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>KPI организации</Text>
          </Card>
        </Col>

        {/* Графики и таблицы */}
        <Col xs={24} lg={16}>
          <Card 
            title="Активность по дням недели"
            style={{ borderRadius: 16 }}
            bodyStyle={{ padding: '12px 20px' }}
            headStyle={{ borderBottom: '1px solid #383842' }}
          >
            <Line {...activityConfig} />
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 16 }}>
              <Text type="secondary">Средняя активность: <Text strong style={{ color: '#9D6AF5' }}>45.3%</Text></Text>
              <Text type="secondary">Пик активности: <Text strong style={{ color: '#9D6AF5' }}>Среда, 61%</Text></Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={8}>
          <Card 
            title="Последние назначения"
            style={{ borderRadius: 16, height: '100%' }}
            bodyStyle={{ padding: '0' }}
            headStyle={{ borderBottom: '1px solid #383842' }}
            extra={<Button type="text" icon={<PlusOutlined />} style={{ color: '#9D6AF5' }}>Добавить</Button>}
          >
            <List
              dataSource={isLoading ? [] : employees}
              renderItem={(item: EmployeeData) => (
                <List.Item 
                  style={{ 
                    padding: '12px 20px', 
                    borderBottom: '1px solid #383842',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer',
                  }}
                  className="employee-list-item"
                >
                  <List.Item.Meta
                    avatar={
                      <Avatar 
                        style={{ 
                          background: gradients.primaryGradient,
                          color: '#fff',
                        }}
                      >
                        {item.full_name ? item.full_name[0] : <UserOutlined />}
                      </Avatar>
                    }
                    title={<Text strong>{item.full_name}</Text>}
                    description={<Text type="secondary">{item.position || 'Сотрудник'}</Text>}
                  />
                </List.Item>
              )}
              loading={isLoading}
              locale={{ emptyText: 'Нет данных о сотрудниках' }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 