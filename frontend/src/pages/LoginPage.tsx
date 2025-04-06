import React, { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { 
  Form, 
  Input, 
  Button, 
  Checkbox, 
  Typography, 
  Alert, 
  Space, 
  Card,
  message
} from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '../hooks/useAuth';

const { Title, Link, Text } = Typography;

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    setLoading(true);
    console.log('[LOG:Login] Отправка формы логина (Ant Design):', values);

    try {
      await login(values.username, values.password);
    } catch (err) {
      console.error('[LOG:Login] Ошибка входа:', err);
      message.error('Неверное имя пользователя или пароль'); 
      setLoading(false);
    }
  };

  return (
    <div 
      style={{ 
        minHeight: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: 'radial-gradient(circle at 10% 10%, rgba(20, 20, 35, 0.95) 0%, rgba(10, 10, 18, 0.98) 100%)',
      }}
    >
      <Card 
        style={{
          width: 400,
          padding: '20px',
          backgroundColor: 'rgba(26, 26, 32, 0.95)',
          border: '1px solid rgba(157, 106, 245, 0.2)',
          borderRadius: '16px',
          boxShadow: '0 8px 32px rgba(157, 106, 245, 0.1)',
        }}
        bordered={false}
      >
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <img src="/images/Logo_NEW2.png" alt="Photomatrix" style={{ width: '200px', filter: 'drop-shadow(0 0 8px rgba(157, 106, 245, 0.4))' }} />
        </div>
        <Title level={3} style={{ textAlign: 'center', color: '#fff', marginBottom: '2rem' }}>
          Вход в систему
        </Title>
        <Form
          name="normal_login"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          layout="vertical"
          requiredMark={false}
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Пожалуйста, введите имя пользователя!' }]}
          >
            <Input 
              prefix={<UserOutlined style={{ color: 'rgba(255,255,255,.25)' }} />} 
              placeholder="Имя пользователя (email)" 
              size="large"
              disabled={loading}
            />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Пожалуйста, введите пароль!' }]}
          >
            <Input.Password 
              prefix={<LockOutlined style={{ color: 'rgba(255,255,255,.25)' }} />} 
              placeholder="Пароль" 
              size="large"
              disabled={loading}
            />
          </Form.Item>
          
          <Form.Item>
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox style={{ color: 'rgba(255, 255, 255, 0.7)' }}>Запомнить меня</Checkbox>
            </Form.Item>
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading} 
              block
              size="large"
              style={{
                background: 'linear-gradient(45deg, #9D6AF5 30%, #7B4FE9 90%)',
                border: 'none',
                boxShadow: '0 3px 5px 2px rgba(157, 106, 245, .3)',
              }}
            >
              Войти
            </Button>
          </Form.Item>
          
          <div style={{ textAlign: 'center' }}>
            <Text style={{ color: 'rgba(255, 255, 255, 0.7)' }}>Нет аккаунта? </Text>
            <Link 
              href="/register"
              onClick={(e) => { e.preventDefault(); navigate('/register'); }}
              style={{ color: 'rgba(157, 106, 245, 0.8)' }}
            >
              Зарегистрироваться
            </Link>
          </div>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage; 