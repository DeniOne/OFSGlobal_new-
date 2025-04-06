import React from 'react';
import { Typography, Card } from 'antd';
import DivisionList from '../../components/divisions/DivisionList';

const { Title, Text } = Typography;

const DivisionsPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>Структура организации</Title>
        <Text type="secondary" style={{ fontSize: 16 }}>
          Управление отделами, департаментами и подразделениями
        </Text>
      </div>
      
      <Card style={{ marginTop: 16 }}>
        <DivisionList />
      </Card>
    </div>
  );
};

export default DivisionsPage; 