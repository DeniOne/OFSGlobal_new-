import React from 'react';
import { Card, Typography } from 'antd';

const { Title } = Typography;

const TelegramBotPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <Card 
        style={{ 
          padding: '24px',
          background: 'linear-gradient(45deg, rgba(0,255,157,0.1), rgba(255,0,255,0.1))',
          border: '1px solid rgba(0,255,157,0.2)',
          borderRadius: '8px',
        }}
      >
        <Title className="cyber-glitch" data-text="Telegram Бот">
          Telegram Бот
        </Title>
        <Title level={4} style={{ marginTop: '16px', color: '#9D6AF5' }}>
          Управление корпоративным ботом
        </Title>
      </Card>
    </div>
  );
};

export default TelegramBotPage;
