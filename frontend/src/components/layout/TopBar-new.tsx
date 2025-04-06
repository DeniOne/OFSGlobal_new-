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
        <Badge count={5} size="small">
          <Button 
            type="text" 
            shape="circle" 
            icon={<BellOutlined style={{ color: '#fff' }} />} 
            // onClick для уведомлений
          />
        </Badge>
        <Badge count={2} size="small">
          <Button 
            type="text" 
            shape="circle" 
            icon={<MessageOutlined style={{ color: '#fff' }} />} 
            // onClick для сообщений
          />
        </Badge>
        {/* Можно добавить другие иконки по аналогии */}
        <Button 
          type="text" 
          shape="circle" 
          icon={<CalendarOutlined style={{ color: '#fff' }} />} 
          // onClick для календаря?
        />
        <Button 
          type="text" 
          shape="circle" 
          icon={<FileTextOutlined style={{ color: '#fff' }} />} 
          // onClick для задач?
        />
      </Space>
      
      {/* Меню профиля */}
      <Dropdown menu={{ items: profileMenuItems }} trigger={['click']} placement="bottomRight">
        <a onClick={(e) => e.preventDefault()} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
          <Avatar 
            size={38} 
            icon={<UserOutlined />} 
            style={{ 
              border: '2px solid rgba(157, 106, 245, 0.5)', // Пример стилизации аватара
              marginRight: 8 
            }}
          />
          {/* Можно добавить имя пользователя */}
          {/* <Text style={{ color: '#fff', fontWeight: 500 }}>Admin</Text> */}
        </a>
      </Dropdown>
    </div>
  );
};

export default TopBar; 