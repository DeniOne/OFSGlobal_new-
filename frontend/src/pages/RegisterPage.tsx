import React, { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { 
  Form, 
  Input, 
  Button, 
  Typography, 
  Card,
  message,
  Result // Для отображения успеха
} from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'; // Добавим иконки
import api from '../services/api'; // Импортируем наш api сервис

// Убираем стилизованные компоненты MUI

const { Title, Link } = Typography;

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  // Убираем состояния для полей, их будет хранить Form
  const [loading, setLoading] = useState(false);
  // const [error, setError] = useState<string | null>(null); // Используем message
  const [success, setSuccess] = useState(false);
  const [form] = Form.useForm(); // Получаем доступ к форме для сброса

  // Обработчик сабмита формы Ant Design
  const onFinish = async (values: any) => {
    setLoading(true);
    console.log('[LOG:Register] Отправка формы регистрации (Ant Design):', values);

    try {
      await api.post('/register', { // Используем наш api сервис
        email: values.email,
        full_name: values.fullName,
        password: values.password
      });
      console.log('[LOG:Register] Успешная регистрация (Ant Design)');
      setSuccess(true);
      // form.resetFields(); // Сброс формы происходит при смене success
    } catch (err: any) {
      console.error('[LOG:Register] Ошибка регистрации (Ant Design):', err);
      let errorMessage = 'Произошла ошибка при регистрации';
      if (err.response?.data?.detail) {
          if (typeof err.response.data.detail === 'string') {
              errorMessage = err.response.data.detail;
          } else if (Array.isArray(err.response.data.detail)) {
              // Обработка ошибок валидации от FastAPI
              errorMessage = err.response.data.detail
                  .map((e: any) => `${e.loc.join('.')}: ${e.msg}`)
                  .join('; ');
          } else if (typeof err.response.data.detail === 'object') {
            errorMessage = JSON.stringify(err.response.data.detail);
          } 
      } else if (err.request) {
          errorMessage = 'Сервер не отвечает, проверьте подключение';
      } else if (err.message) {
          errorMessage = err.message;
      }
      message.error(errorMessage);
    } finally {
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
        
        {success ? (
          <Result
            status="success"
            title="Регистрация прошла успешно!"
            subTitle="Теперь вы можете войти в систему, используя ваш email и пароль."
            style={{ color: 'white' }} // Текст результата тоже делаем светлым
            extra={[
              <Button 
                type="primary" 
                key="login"
                onClick={() => navigate('/login')}
                style={{
                    background: 'linear-gradient(45deg, #9D6AF5 30%, #7B4FE9 90%)',
                    border: 'none',
                    boxShadow: '0 3px 5px 2px rgba(157, 106, 245, .3)',
                  }}
              >
                Перейти к входу
              </Button>,
            ]}
          />
        ) : (
          <>
            <Title level={3} style={{ textAlign: 'center', color: '#fff', marginBottom: '2rem' }}>
              Регистрация
            </Title>
            <Form
              form={form} // Передаем form для возможности сброса
              name="register"
              onFinish={onFinish}
              layout="vertical"
              requiredMark={false}
            >
              <Form.Item
                name="fullName"
                rules={[{ required: true, message: 'Пожалуйста, введите полное имя!' }]}
              >
                <Input 
                  prefix={<UserOutlined style={{ color: 'rgba(255,255,255,.25)' }} />} 
                  placeholder="Полное имя" 
                  size="large"
                  disabled={loading}
                />
              </Form.Item>
              <Form.Item
                name="email"
                rules={[
                  { required: true, message: 'Пожалуйста, введите Email!' },
                  { type: 'email', message: 'Введите корректный Email!' }
                ]}
              >
                <Input 
                  prefix={<MailOutlined style={{ color: 'rgba(255,255,255,.25)' }} />} 
                  placeholder="Email" 
                  size="large"
                  disabled={loading}
                />
              </Form.Item>
              <Form.Item
                name="password"
                rules={[{ required: true, message: 'Пожалуйста, введите пароль!' }]}
                hasFeedback // Добавляет иконку валидации
              >
                <Input.Password 
                  prefix={<LockOutlined style={{ color: 'rgba(255,255,255,.25)' }} />} 
                  placeholder="Пароль" 
                  size="large"
                  disabled={loading}
                />
              </Form.Item>
              <Form.Item
                name="confirmPassword"
                dependencies={['password']} // Зависит от поля password
                hasFeedback
                rules={[
                  { required: true, message: 'Пожалуйста, подтвердите пароль!' },
                  // Функция валидации для проверки совпадения паролей
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('password') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('Пароли не совпадают!'));
                    },
                  }),
                ]}
              >
                <Input.Password 
                  prefix={<LockOutlined style={{ color: 'rgba(255,255,255,.25)' }} />} 
                  placeholder="Подтвердите пароль" 
                  size="large"
                  disabled={loading}
                />
              </Form.Item>

              {/* Отображение ошибки через message.error() в onFinish */}

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
                  Зарегистрироваться
                </Button>
              </Form.Item>
              
              <div style={{ textAlign: 'center' }}>
                <Typography.Text style={{ color: 'rgba(255, 255, 255, 0.7)' }}>Уже есть аккаунт? </Typography.Text>
                <Link 
                  href="/login"
                  onClick={(e) => { e.preventDefault(); navigate('/login'); }}
                  style={{ color: 'rgba(157, 106, 245, 0.8)' }}
                >
                  Войти
                </Link>
              </div>
            </Form>
          </>
        )}
      </Card>
    </div>
  );
};

export default RegisterPage; 