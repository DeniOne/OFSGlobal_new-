import React from 'react';
import { Typography, Card } from 'antd';
import PositionList from '../../components/positions/PositionList';

const { Title, Text } = Typography;

const PositionsPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Должности</Title>
        <Text type="secondary" style={{ fontSize: 16 }}>
          Управление должностями и карьерными треками
        </Text>
      </div>
      
      <Card style={{ marginTop: 16 }}>
        <PositionList />
      </Card>
    </div>
  );
};

export default PositionsPage; 