import React from 'react';
import { Card, Typography, Breadcrumb, Space } from 'antd';
import { HomeOutlined, ApiOutlined } from '@ant-design/icons';
import FunctionalRelationList from '../components/functional_relations/FunctionalRelationList';
import './FunctionalRelationsPage.css';

const { Title } = Typography;

const FunctionalRelationsPage: React.FC = () => {
  return (
    <div className="functional-relations-page">
      <Card className="page-header">
        <Title level={4}>Управление функциональными связями</Title>
        
        <Breadcrumb
          items={[
            {
              title: (
                <Space>
                  <HomeOutlined />
                  <a href="/">Главная</a>
                </Space>
              ),
            },
            {
              title: (
                <Space>
                  <ApiOutlined />
                  <span>Управление функциональными связями</span>
                </Space>
              ),
            },
          ]}
        />
      </Card>
      
      <Card className="page-content">
        <FunctionalRelationList />
      </Card>
    </div>
  );
};

export default FunctionalRelationsPage; 