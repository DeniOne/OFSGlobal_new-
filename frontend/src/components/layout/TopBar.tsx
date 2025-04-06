import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Input, 
  Dropdown, 
  Menu, 
  Badge, 
  Avatar, 
  Space, 
  Button, 
  Typography 
} from 'antd';
import type { MenuProps } from 'antd';
import { 
  SearchOutlined, 
  BellOutlined, 
  MessageOutlined, // Пример иконки
  SettingOutlined, 
  LogoutOutlined, 
  UserOutlined,     // Иконка по умолчанию для Аватара
  CalendarOutlined, // Аналог EventIcon?
  FileTextOutlined  // Аналог AssignmentIcon?
} from '@ant-design/icons';

// TODO: Импортировать useAuth для logout
// import { useAuth } from '../../hooks/useAuth';

// Убираем стилизованные компоненты MUI
// const TopBarContainer = ...
// const SearchContainer = ...
// const SearchBox = ...
// const SearchInput = ...
// const StyledSearchIcon = ...
// const StyledIconButton = ...
// const StyledBadge = ...
// const StyledAvatar = ...
// const StyledMenu = ...

const { Text } = Typography;

const TopBar: React.FC = () => {
  const navigate = useNavigate();
  // const { logout } = useAuth(); // Получаем logout
  const [isSearchVisible, setIsSearchVisible] = useState(false);

  // Обработчик выхода
  const handleLogout = () => {
    console.log('Выход из системы...');
    // logout(); // Вызываем функцию logout из useAuth
  };

  // Элементы меню профиля
  const profileMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      label: 'Профиль',
      icon: <UserOutlined />,
      onClick: () => navigate('/profile'), // TODO: Создать страницу профиля
    },
    {
      key: 'settings',
      label: 'Настройки',
      icon: <SettingOutlined />,
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      label: 'Выход',
      icon: <LogoutOutlined />,
      onClick: handleLogout, // Используем наш обработчик
      danger: true, // Помечаем как опасное действие
    },
  ];

  // Элементы меню уведомлений
  const notificationsItems: MenuProps['items'] = [
    {
      key: 'notification-1',
      label: 'Новое назначение добавлено',
      onClick: () => console.log('Открыть уведомление 1'),
    },
    {
      key: 'notification-2',
      label: 'Обновлены данные сотрудника',
      onClick: () => console.log('Открыть уведомление 2'),
    },
    {
      key: 'notification-3',
      label: 'Задача назначена на вас',
      onClick: () => console.log('Открыть уведомление 3'),
    },
    {
      key: 'notification-4',
      label: 'Запрос на подтверждение',
      onClick: () => console.log('Открыть уведомление 4'),
    },
    {
      key: 'notification-5',
      label: 'Завершите настройку профиля',
      onClick: () => console.log('Открыть уведомление 5'),
    },
    {
      type: 'divider',
    },
    {
      key: 'view-all',
      label: <Text style={{ width: '100%', textAlign: 'center' }}>Просмотреть все</Text>,
      onClick: () => navigate('/notifications'),
    },
  ];

  // Элементы меню сообщений
  const messagesItems: MenuProps['items'] = [
    {
      key: 'message-1',
      label: 'Сообщение от Администратора',
      onClick: () => console.log('Открыть сообщение 1'),
    },
    {
      key: 'message-2',
      label: 'Новое сообщение в чате',
      onClick: () => console.log('Открыть сообщение 2'),
    },
    {
      type: 'divider',
    },
    {
      key: 'view-all-messages',
      label: <Text style={{ width: '100%', textAlign: 'center' }}>Все сообщения</Text>,
      onClick: () => navigate('/messages'),
    },
  ];

  return (
    <div 
      style={{ 
        // Стили контейнера, имитирующие старый TopBarContainer
        backgroundColor: 'rgba(20, 20, 22, 0.8)',
        backdropFilter: 'blur(10px)',
        padding: '10px 15px', // Немного уменьшил паддинги
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        gap: '15px',
        position: 'fixed',
        top: 0,
        right: 0,
        zIndex: 1100,
        borderRadius: '0 0 0 15px',
        boxShadow: '0 4px 15px -5px rgba(0, 0, 0, 0.5), 0 0 10px rgba(0, 0, 0, 0.2)',
        border: '1px solid rgba(45, 45, 55, 0.9)',
        borderRight: 'none',
        borderTop: 'none',
      }}
    >
      {/* Поиск */}
      <Space>
        {/* Показываем Input.Search при клике на иконку */} 
        {isSearchVisible && (
          <Input.Search 
            placeholder="Поиск..." 
            allowClear 
            onSearch={(value) => console.log('Search:', value)} 
            style={{ width: 250, transition: 'width 0.3s ease' }} 
            onBlur={() => setIsSearchVisible(false)} // Скрываем при потере фокуса
            autoFocus
          />
        )}
        <Button 
          type="text" 
          shape="circle" 
          icon={<SearchOutlined style={{ color: '#fff' }} />} 
          onClick={() => setIsSearchVisible(!isSearchVisible)} 
          style={{ 
            backgroundColor: isSearchVisible ? 'rgba(157, 106, 245, 0.2)' : 'transparent',
          }}
        />
      </Space>
      
      {/* Иконки действий */}
      <Space size="middle">
        {/* Уведомления с выпадающим меню */}
        <Dropdown menu={{ items: notificationsItems }} trigger={['click']} placement="bottomRight" 
          dropdownRender={(menu) => (
            <div style={{ 
              background: '#1A1A20', 
              boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.5)', 
              borderRadius: '8px',
              border: '1px solid #303030',
              padding: '8px 0',
              minWidth: '250px'
            }}>
              <div style={{ padding: '4px 12px 8px', borderBottom: '1px solid #303030' }}>
                <Text strong style={{ color: '#fff' }}>Уведомления</Text>
              </div>
              {React.cloneElement(menu as React.ReactElement)}
            </div>
          )}
        >
          <Badge count={5} size="small">
            <Button 
              type="text" 
              shape="circle" 
              icon={<BellOutlined style={{ color: '#fff' }} />} 
            />
          </Badge>
        </Dropdown>
        
        {/* Сообщения с выпадающим меню */}
        <Dropdown menu={{ items: messagesItems }} trigger={['click']} placement="bottomRight"
          dropdownRender={(menu) => (
            <div style={{ 
              background: '#1A1A20', 
              boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.5)', 
              borderRadius: '8px',
              border: '1px solid #303030',
              padding: '8px 0',
              minWidth: '250px'
            }}>
              <div style={{ padding: '4px 12px 8px', borderBottom: '1px solid #303030' }}>
                <Text strong style={{ color: '#fff' }}>Сообщения</Text>
              </div>
              {React.cloneElement(menu as React.ReactElement)}
            </div>
          )}
        >
          <Badge count={2} size="small">
            <Button 
              type="text" 
              shape="circle" 
              icon={<MessageOutlined style={{ color: '#fff' }} />} 
            />
          </Badge>
        </Dropdown>
        
        {/* Календарь */}
        <Button 
          type="text" 
          shape="circle" 
          icon={<CalendarOutlined style={{ color: '#fff' }} />} 
          onClick={() => navigate('/calendar')}
        />
        
        {/* Задачи */}
        <Button 
          type="text" 
          shape="circle" 
          icon={<FileTextOutlined style={{ color: '#fff' }} />} 
          onClick={() => navigate('/tasks')}
        />
      </Space>
      
      {/* Меню профиля */}
      <Dropdown 
        menu={{ items: profileMenuItems }} 
        trigger={['click']} 
        placement="bottomRight"
        dropdownRender={(menu) => (
          <div style={{ 
            background: '#1A1A20', 
            boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.5)', 
            borderRadius: '8px',
            border: '1px solid #303030',
            padding: '8px 0'
          }}>
            <div style={{ padding: '8px 16px', borderBottom: '1px solid #303030' }}>
              <Text strong style={{ color: '#fff' }}>Профиль</Text>
              <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.6)' }}>admin@example.com</div>
            </div>
            {React.cloneElement(menu as React.ReactElement)}
          </div>
        )}
      >
        <a onClick={(e) => e.preventDefault()} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
          <Avatar 
            size={38} 
            icon={<UserOutlined />} 
            style={{ 
              border: '2px solid rgba(157, 106, 245, 0.5)', // Пример стилизации аватара
            }}
          />
        </a>
      </Dropdown>
    </div>
  );
};

export default TopBar; 