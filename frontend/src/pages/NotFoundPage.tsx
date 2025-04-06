import React from 'react';
import { Typography, Button, Result } from 'antd';
import { Link } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 16px' }}>
      <Result
        status="404"
        title="404"
        subTitle="Страница не найдена"
        extra={
          <>
            <Typography.Paragraph>
              Запрашиваемая страница не существует или была перемещена.
            </Typography.Paragraph>
            <Button 
              type="primary" 
              size="large"
              style={{ marginTop: '16px' }}
            >
              <Link to="/dashboard">Вернуться на главную</Link>
            </Button>
          </>
        }
      />
    </div>
  );
};

export default NotFoundPage; 