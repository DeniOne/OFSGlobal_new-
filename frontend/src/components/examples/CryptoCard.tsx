import React from 'react';
import { Card, Typography, Button, Avatar, Space, Divider, Row, Col } from 'antd';
import { LineChartOutlined, WalletOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface CryptoCardProps {
  name: string;
  code: string;
  price: number;
  change: number;
  chartData?: any; // Для примера
  avatarUrl?: string;
}

const CryptoCard: React.FC<CryptoCardProps> = ({
  name,
  code,
  price,
  change,
  chartData,
  avatarUrl
}) => {
  const isPositive = change >= 0;
  
  return (
    <Card
      className="crypto-card"
      variant="borderless"
      style={{ 
        width: 300, 
        padding: '16px',
        backgroundColor: '#222228',
      }}
    >
      {/* Заголовок с иконкой и названием */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <Space>
          <Avatar 
            size={40} 
            src={avatarUrl} 
            icon={<WalletOutlined />} 
            style={{ 
              backgroundColor: '#1A1A20',
              border: '1px solid rgba(157, 106, 245, 0.3)',
            }}
          />
          <div>
            <Text style={{ color: '#9D6AF5', fontSize: 20, fontWeight: 'bold' }}>
              {name}
            </Text>
            <div>
              <Text style={{ color: '#aaa', fontSize: 12 }}>
                {code}
              </Text>
            </div>
          </div>
        </Space>
        
        <Button
          type="text"
          shape="circle"
          icon={<LineChartOutlined style={{ color: '#9D6AF5' }} />}
          style={{ 
            backgroundColor: 'rgba(157, 106, 245, 0.1)',
            border: '1px solid rgba(157, 106, 245, 0.2)'
          }}
        />
      </div>
      
      {/* Цена и изменение */}
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ color: 'white', margin: 0, marginBottom: 8 }}>
          ${price.toLocaleString()}
        </Title>
        <Space>
          {isPositive ? (
            <ArrowUpOutlined style={{ color: '#4CAF50' }} />
          ) : (
            <ArrowDownOutlined style={{ color: '#F44336' }} />
          )}
          <Text style={{ 
            color: isPositive ? '#4CAF50' : '#F44336',
            fontWeight: 'bold'
          }}>
            {isPositive ? '+' : ''}{change.toFixed(2)}%
          </Text>
        </Space>
      </div>
      
      {/* График */}
      <div className="neon-chart" style={{ height: 80, marginBottom: 20 }}>
        <svg width="100%" height="100%" style={{ display: 'block' }}>
          <defs>
            <linearGradient id="purple-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#9D6AF5" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#9D6AF5" stopOpacity="0.1" />
            </linearGradient>
          </defs>
          {/* Это просто пример свг-пути, в реальности нужно использовать библиотеку графиков */}
          <path 
            d="M0,60 C20,40 40,80 60,20 C80,40 100,10 120,30 C140,50 160,5 180,40 C200,30 220,60 240,50 C260,35 280,55 300,30" 
            fill="none" 
            stroke="#9D6AF5" 
            strokeWidth="2" 
            style={{ filter: 'drop-shadow(0 0 4px rgba(157, 106, 245, 0.7))' }}
          />
        </svg>
      </div>
      
      <Divider style={{ borderColor: 'rgba(255,255,255,0.1)', margin: '12px 0' }} />
      
      {/* Кнопки действий */}
      <Row gutter={12}>
        <Col span={12}>
          <Button
            block
            className="gradient-button"
            style={{ borderRadius: 20 }}
          >
            Buy
          </Button>
        </Col>
        <Col span={12}>
          <Button
            block
            style={{ 
              borderRadius: 20,
              borderColor: '#9D6AF5',
              color: '#9D6AF5',
              background: 'transparent'
            }}
          >
            Sell
          </Button>
        </Col>
      </Row>
    </Card>
  );
};

export default CryptoCard; 