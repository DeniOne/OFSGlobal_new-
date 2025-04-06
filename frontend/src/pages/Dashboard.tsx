import React from 'react';
import { Card, Typography, Progress, Row, Col, Space, Tag, Divider } from 'antd';
import styled from '@emotion/styled';
import { PieChart, Pie, Cell, ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

const { Title, Text } = Typography;

// Стилизованные компоненты
const StyledCard = styled(Card)`
  border-radius: 16px;
  height: 100%;
  background: rgba(32, 32, 36, 0.9);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(45, 45, 55, 0.9);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4), inset 0 0 3px rgba(157, 106, 245, 0.1);
    border-color: rgba(60, 60, 70, 0.9);
  }
`;

const GradientText = styled(Text)`
  background: linear-gradient(90deg, #9D6AF5, #b350ff);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  font-weight: bold;
  text-shadow: 0 0 10px rgba(157, 106, 245, 0.5);
`;

const ProgressLabel = styled.div`
  display: flex;
  justify-content: space-between;
  width: 100%;
  color: #fff;
  margin-bottom: 8px;
  font-weight: 500;
  opacity: 0.9;
  transition: all 0.2s ease;
  
  &:hover {
    opacity: 1;
    transform: translateX(2px);
  }
`;

const GlassCard = styled.div`
  padding: 16px;
  border-radius: 8px;
  background: rgba(30, 30, 42, 0.5);
  margin-bottom: 16px;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(30, 30, 42, 0.7);
  }
`;

const ActivityCard = styled.div`
  padding: 16px;
  border-radius: 8px;
  background: rgba(30, 30, 42, 0.5);
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
`;

// Примеры данных
const pieData = [
  { name: 'Выполнено', value: 65, color: '#00e6ff' },
  { name: 'В работе', value: 25, color: '#b100ff' },
  { name: 'Отложено', value: 10, color: '#f0a202' },
];

const areaData = [
  { name: 'Янв', value: 40 },
  { name: 'Фев', value: 30 },
  { name: 'Мар', value: 45 },
  { name: 'Апр', value: 50 },
  { name: 'Май', value: 65 },
  { name: 'Июн', value: 60 },
  { name: 'Июл', value: 85 },
];

const progressData = [
  { name: 'Выполнение плана', value: 82 },
  { name: 'Эффективность', value: 76 },
  { name: 'Качество', value: 90 },
  { name: 'Удовлетворенность', value: 68 },
];

const kanbanTasks = {
  todo: [
    { id: 1, title: 'Обновить дизайн', priority: 'Высокий' },
    { id: 2, title: 'Интеграция API', priority: 'Средний' },
  ],
  inProgress: [
    { id: 3, title: 'Оптимизация БД', priority: 'Средний' },
    { id: 4, title: 'Разработка новых модулей', priority: 'Высокий' },
  ],
  completed: [
    { id: 5, title: 'Обновление документации', priority: 'Низкий' },
    { id: 6, title: 'Исправление багов', priority: 'Высокий' },
  ],
};

const Dashboard: React.FC = () => {
  return (
    <div style={{ padding: '16px 24px' }}>
      <Row gutter={[24, 24]}>
        {/* Ключевые метрики */}
        <Col xs={24} md={12}>
          <StyledCard>
            <Title level={5} style={{ 
              marginBottom: 24, 
              color: '#9D6AF5', 
              fontWeight: 500,
              textShadow: '0 0 5px rgba(157, 106, 245, 0.5)'
            }}>
              Ключевые показатели эффективности
            </Title>
            <div>
              {progressData.map((item, index) => (
                <div key={index} style={{ marginBottom: 16 }}>
                  <ProgressLabel>
                    <span>{item.name}</span>
                    <span>{item.value}%</span>
                  </ProgressLabel>
                  <Progress 
                    percent={item.value} 
                    showInfo={false}
                    strokeColor={{
                      '0%': '#9D6AF5',
                      '100%': '#b350ff',
                    }}
                    trailColor="rgba(32, 32, 36, 0.9)"
                    strokeWidth={16}
                    style={{
                      height: 16,
                      borderRadius: 8,
                      marginBottom: 12,
                      boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3), inset 0 2px 4px rgba(0, 0, 0, 0.2)',
                    }}
                  />
                </div>
              ))}
            </div>
          </StyledCard>
        </Col>

        {/* Статистика сотрудников */}
        <Col xs={24} md={12}>
          <StyledCard>
            <Title level={5} style={{ 
              marginBottom: 24, 
              color: '#9D6AF5', 
              fontWeight: 500,
              textShadow: '0 0 5px rgba(157, 106, 245, 0.5)'
            }}>
              Статистика персонала
            </Title>
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text style={{ color: 'rgba(255,255,255,0.7)' }}>
                  Общее количество сотрудников
                </Text>
                <Text strong style={{ color: '#fff' }}>
                  873
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text style={{ color: 'rgba(255,255,255,0.7)' }}>
                  Активные проекты
                </Text>
                <Text strong style={{ color: '#fff' }}>
                  42
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text style={{ color: 'rgba(255,255,255,0.7)' }}>
                  Отделы
                </Text>
                <Text strong style={{ color: '#fff' }}>
                  18
                </Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text style={{ color: 'rgba(255,255,255,0.7)' }}>
                  Новые сотрудники (месяц)
                </Text>
                <Text strong style={{ color: '#fff' }}>
                  15
                </Text>
              </div>
            </Space>
          </StyledCard>
        </Col>
        
        {/* Недавняя активность */}
        <Col xs={24}>
          <StyledCard>
            <Title level={5} style={{ 
              marginBottom: 24, 
              color: '#9D6AF5', 
              fontWeight: 500,
              textShadow: '0 0 5px rgba(157, 106, 245, 0.5)'
            }}>
              Недавняя активность
            </Title>
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              {Array.from({ length: 5 }).map((_, index) => (
                <ActivityCard key={index}>
                  <div>
                    <Text style={{ color: '#fff', fontWeight: 500 }}>
                      {index === 0 ? 'Создан новый отдел "Аналитика данных"' : 
                       index === 1 ? 'Добавлен сотрудник Иванов И.И.' :
                       index === 2 ? 'Обновлена организационная структура' :
                       index === 3 ? 'Изменены роли в проекте "Реструктуризация"' :
                       'Обновлены KPI сотрудников IT-отдела'}
                    </Text>
                    <div>
                      <Text style={{ color: 'rgba(255,255,255,0.5)', fontSize: 12 }}>
                        {index === 0 ? 'Сегодня, 10:32' : 
                         index === 1 ? 'Сегодня, 09:15' :
                         index === 2 ? 'Вчера, 16:45' :
                         index === 3 ? 'Вчера, 12:20' :
                         '21.04.2024, 14:30'}
                      </Text>
                    </div>
                  </div>
                  <Tag color={index % 2 === 0 ? '#00e6ff' : '#b100ff'} style={{ height: 'fit-content' }}>
                    {index % 2 === 0 ? 'Система' : 'HR'}
                  </Tag>
                </ActivityCard>
              ))}
            </Space>
          </StyledCard>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 