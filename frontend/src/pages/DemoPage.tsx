import React from 'react';
import { Row, Col, Typography, Space, Button, Card } from 'antd';
import { PlusOutlined, AreaChartOutlined, WalletOutlined, SettingOutlined } from '@ant-design/icons';
import CryptoCard from '../components/examples/CryptoCard';

const { Title } = Typography;

const DemoPage: React.FC = () => {
  const cryptos = [
    {
      name: 'Bitcoin',
      code: 'BTC/USD',
      price: 48320.91,
      change: 2.14,
      avatarUrl: '/images/crypto/btc.png',
    },
    {
      name: 'Ethereum',
      code: 'ETH/USD',
      price: 2860.23,
      change: -1.28,
      avatarUrl: '/images/crypto/eth.png',
    },
    {
      name: 'Litecoin',
      code: 'LTC/USD',
      price: 183.7,
      change: 0.43,
      avatarUrl: '/images/crypto/ltc.png',
    },
  ];

  return (
    <div style={{ 
      background: 'linear-gradient(135deg, #30154E 0%, #160c25 100%)',
      minHeight: '100vh',
      padding: '40px 20px'
    }}>
      <Row gutter={[24, 24]} justify="center">
        <Col xs={24} style={{ textAlign: 'center', marginBottom: 20 }}>
          <Title 
            level={2} 
            className="neon-text"
            style={{ 
              color: 'white',
              textShadow: '0 0 10px rgba(157, 106, 245, 0.7)',
              fontWeight: 'bold',
              marginBottom: 0
            }}
          >
            CRYPTONITE
          </Title>
          <Typography.Text style={{ color: '#aaa' }}>
            Cryptocurrency Dashboard
          </Typography.Text>
        </Col>

        {/* Навигационные кнопки */}
        <Col xs={24} style={{ textAlign: 'center', marginBottom: 16 }}>
          <Space size="large">
            <Button 
              type="text" 
              icon={<WalletOutlined />}
              style={{ color: '#9D6AF5' }}
            >
              Wallets
            </Button>
            <Button 
              className="gradient-button"
              icon={<AreaChartOutlined />}
              style={{ borderRadius: 20 }}
            >
              Dashboard
            </Button>
            <Button 
              type="text" 
              icon={<SettingOutlined />}
              style={{ color: '#9D6AF5' }}
            >
              Settings
            </Button>
          </Space>
        </Col>

        {/* Карточки криптовалют */}
        <Col xs={24}>
          <Row gutter={[24, 24]} justify="center">
            {cryptos.map((crypto, index) => (
              <Col key={index} xs={24} sm={12} md={8} lg={7}>
                <CryptoCard {...crypto} />
              </Col>
            ))}
            
            {/* Добавить карточку */}
            <Col xs={24} sm={12} md={8} lg={7}>
              <Card 
                bordered={false}
                style={{ 
                  width: 300, 
                  height: 350,
                  background: 'rgba(34, 34, 40, 0.5)', 
                  borderRadius: 16,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px dashed rgba(157, 106, 245, 0.3)',
                  cursor: 'pointer'
                }}
                hoverable
              >
                <div style={{ textAlign: 'center' }}>
                  <Button 
                    type="primary" 
                    shape="circle" 
                    icon={<PlusOutlined />} 
                    style={{ 
                      backgroundColor: 'rgba(157, 106, 245, 0.2)',
                      borderColor: '#9D6AF5',
                      marginBottom: 16
                    }} 
                    size="large"
                  />
                  <Typography.Text style={{ display: 'block', color: '#9D6AF5' }}>
                    Add New Currency
                  </Typography.Text>
                </div>
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
    </div>
  );
};

export default DemoPage; 