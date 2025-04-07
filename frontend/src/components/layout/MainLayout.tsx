import React, { useState, useEffect } from 'react';
import { useNavigate, Outlet, useLocation } from 'react-router-dom';
import { Layout, Button, Tooltip, Flex, Menu, Typography, Grid, theme, ConfigProvider, App } from 'antd';
import { MenuFoldOutlined, MenuUnfoldOutlined, HomeOutlined, UserOutlined } from '@ant-design/icons';
import TopBar from './TopBar';
import MenuListItems from './MenuListItems';

const { Sider, Content, Header, Footer } = Layout;
const { Title } = Typography;
const { useBreakpoint } = Grid;

// Стили для логотипа (можно вынести в CSS)
const logoStyleBase: React.CSSProperties = {
  display: 'block',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  filter: 'drop-shadow(0 0 5px rgba(157, 106, 245, 0.3))',
};

const logoStyleCollapsed: React.CSSProperties = {
  ...logoStyleBase,
  height: '35px',
  width: '35px',
  margin: '25px auto 20px',
  objectFit: 'contain',
};

const logoStyleExpanded: React.CSSProperties = {
  ...logoStyleBase,
  height: '40px',
  width: 'auto',
  margin: '25px auto 30px',
  objectFit: 'unset',
};

const logoHoverStyle: React.CSSProperties = {
  transform: 'scale(1.05)',
  filter: 'drop-shadow(0 0 8px rgba(157, 106, 245, 0.5))',
};

// Стили для основного контента (можно вынести в CSS)
const contentStyle: React.CSSProperties = {
  margin: '24px 16px',
  padding: 24,
  minHeight: 280, // Оставляем как есть или сделаем динамическим?
  background: '#121215', // Темный фон контента
  overflow: 'auto',
  position: 'relative', // Для псевдоэлементов, если они нужны
  // Добавим стили скроллбара, похожие на MUI
  scrollbarWidth: 'thin', /* Firefox */
  scrollbarColor: 'rgba(157, 106, 245, 0.5) rgba(0,0,0,0.2)', /* Firefox */
};

// Псевдоэлементы и стили скроллбара для Webkit лучше добавить через CSS-файл или styled-components
// Примерно так в CSS:
// .main-content::-webkit-scrollbar { width: 6px; }
// .main-content::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
// .main-content::-webkit-scrollbar-thumb { background: rgba(157, 106, 245, 0.5); border-radius: 3px; }
// .main-content::-webkit-scrollbar-thumb:hover { background: rgba(157, 106, 245, 0.7); box-shadow: 0 0 6px rgba(157, 106, 245, 0.5); }

// Стили для кастомизации меню - ПЫТАЕМСЯ ВНЕСТИ NEOMORPHISM (Попытка №2 с !important)
const menuStyles = `
  /* Базовый вид пункта меню (немного выпуклый) */
  .main-layout-sider .ant-menu-item,
  .main-layout-sider .ant-menu-submenu-title {
    font-size: 15px;
    padding: 12px 20px !important;
    height: auto;
    line-height: normal;
    margin-bottom: 8px !important; /* Чуть больше отступ */
    border-radius: var(--neo-border-radius, 6px);
    transition: background 0.2s ease, box-shadow 0.2s ease, color 0.2s ease;
    background: transparent !important; /* Убедимся, что фон прозрачный */
    /* Применяем базовую нео-тень с !important */
    box-shadow:
      calc(var(--neo-shadow-offset, 4px) * -1) calc(var(--neo-shadow-offset, 4px) * -1) var(--neo-shadow-blur, 8px) rgba(255, 255, 255, 0.08), /* Светлая чуть ярче */
      var(--neo-shadow-offset, 4px) var(--neo-shadow-offset, 4px) var(--neo-shadow-blur, 8px) rgba(0, 0, 0, 0.5) !important; /* Темная чуть темнее */
    color: var(--neo-text-color, rgba(255, 255, 255, 0.8));
    border: none; /* Убираем возможные границы antd */
    position: relative; /* Для z-index при hover */
  }

  /* Эффект при наведении (вдавленный) */
  .main-layout-sider .ant-menu-item:hover,
  .main-layout-sider .ant-menu-submenu-title:hover {
    background: rgba(255, 255, 255, 0.03) !important; /* Легкий фон при наведении */
    /* Применяем вдавленную нео-тень с !important */
    box-shadow:
      inset calc(var(--neo-shadow-offset, 4px) * -1) calc(var(--neo-shadow-offset, 4px) * -1) var(--neo-shadow-blur, 8px) rgba(0, 0, 0, 0.6), /* Темная сверху-слева */
      inset var(--neo-shadow-offset, 4px) var(--neo-shadow-offset, 4px) var(--neo-shadow-blur, 8px) rgba(255, 255, 255, 0.06) !important; /* Светлая снизу-справа */
    color: var(--neo-text-color-light, #ffffff) !important; /* Яркий текст при наведении */
    z-index: 1; /* Чтобы тень не обрезалась соседями */
  }

  /* Активный/выбранный пункт меню (основной цвет + выпуклая тень) */
  .main-layout-sider .ant-menu-item-selected {
    background: var(--neo-primary-bg, #9D6AF5) !important; /* Основной цвет оставляем */
    color: var(--neo-text-color-light, #ffffff) !important; /* Белый текст */
    font-weight: 600;
    /* Применяем тень как у primary кнопки с !important */
    box-shadow:
      calc(var(--neo-shadow-offset, 4px) * -1) calc(var(--neo-shadow-offset, 4px) * -1) var(--neo-shadow-blur, 8px) rgba(255, 255, 255, 0.15), /* Светлая тень для цветного фона */
      var(--neo-shadow-offset, 4px) var(--neo-shadow-offset, 4px) var(--neo-shadow-blur, 8px) rgba(0, 0, 0, 0.6) !important; /* Темная тень для цветного фона */
    z-index: 2; /* Выше чем hover */
  }

  /* Убираем стандартную левую рамку у активного элемента, если она есть */
  .main-layout-sider .ant-menu-item-selected::after {
      border-right: none !important;
  }

  /* Стили для иконок и текста внутри пунктов */
  .main-layout-sider .ant-menu-item .anticon,
  .main-layout-sider .ant-menu-submenu-title .anticon {
    font-size: 18px;
    vertical-align: middle;
    transition: color 0.2s ease;
  }
  .main-layout-sider .ant-menu-item span,
  .main-layout-sider .ant-menu-submenu-title span {
    vertical-align: middle;
    margin-left: 12px;
    transition: color 0.2s ease;
  }
`;

const MainLayout: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isLogoHovered, setIsLogoHovered] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname;
  const screens = useBreakpoint();
  const { token } = theme.useToken();

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const logoStyleBase = {
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      height: 'auto',
      display: 'block',
      margin: '16px auto',
  };

  const logoStyleExpanded = {
      ...logoStyleBase,
      maxWidth: '180px',
      opacity: 1,
  };

  const logoStyleCollapsed = {
      ...logoStyleBase,
      maxWidth: '40px',
      opacity: 0.9,
  };

  const logoStyleHover = {
      transform: 'scale(1.05)',
      opacity: 1,
  };

  const finalLogoStyle = {
      ...(isCollapsed ? logoStyleCollapsed : logoStyleExpanded),
      ...(isLogoHovered ? logoStyleHover : {})
  };

  // Стили для основного контента
  const contentStyle = {
    padding: 24,
    margin: 0,
    minHeight: 280,
    background: token.colorBgContainer,
    overflow: 'auto', // Добавляем скролл для контента
  };

  return (
    <ConfigProvider 
      theme={{
        token: {
           colorPrimary: '#9D6AF5', // Основной фиолетовый
           borderRadius: 6, // Глобальное скругление для всех компонентов (включая кнопки)
           colorError: '#f5222d', // Стандартный красный для ошибок/удаления
           // Добавляем тени для объемности
           boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)', // Базовая тень
           boxShadowSecondary: '0 1px 3px rgba(0, 0, 0, 0.3), 0 0 1px rgba(0, 0, 0, 0.1)', // Тень для объемных элементов
        },
        components: {
          Layout: {
            siderBg: '#1A1A20', 
            headerBg: '#1F1F24',
            headerPadding: '0 24px'
          },
          Menu: {
            darkItemBg: 'transparent', // Убираем фон по умолчанию
            darkItemSelectedBg: '#9D6AF5', // Возвращаем фиолетовый для активного!
            darkItemColor: 'rgba(255, 255, 255, 0.7)', // Немного светлее неактивный текст
            darkItemHoverBg: 'transparent', // Убираем стандартный фон при наведении (управляем через CSS)
            darkItemHoverColor: '#fff', // Белый текст при наведении
            darkItemSelectedColor: '#ffffff', // Белый текст для активного
            darkSubMenuItemBg: 'rgba(255, 255, 255, 0.02)' // Легкий фон для подменю
          },
          Button: {
             // Используем наши CSS переменные для базовых стилей default кнопки
             defaultColor: 'var(--neo-text-color)',
             defaultBg: 'var(--neo-default-bg)', 
             defaultBorderColor: 'transparent', // Убираем границу
             defaultShadow: 'none', // Убираем стандартную тень antd
             
             // Используем наши CSS переменные для hover/active default кнопки
             defaultHoverColor: 'var(--neo-text-color-light)',
             defaultHoverBg: 'var(--neo-default-bg-hover)',
             defaultHoverBorderColor: 'transparent', // Убираем границу
             defaultActiveColor: 'rgba(255, 255, 255, 0.6)', // Из нашего CSS
             defaultActiveBg: 'var(--neo-default-bg-active)', 
             defaultActiveBorderColor: 'transparent', // Убираем границу
             
             // Стили для primary кнопки (цвет фона уже задан через token.colorPrimary)
             primaryColor: 'var(--neo-text-color-light)', 
             primaryShadow: 'none', // Убираем стандартную тень antd
             colorPrimaryBorder: 'transparent', // Попробуем убрать границу, если она есть
             colorPrimaryHover: 'var(--neo-primary-bg-hover)',
             colorPrimaryActive: 'var(--neo-primary-bg-active)', 
             
             // Стили для danger кнопки (цвет фона задан через token.colorError)
             dangerColor: 'var(--neo-text-color-light)',
             dangerShadow: 'none', // Убираем стандартную тень antd
             colorErrorBorder: 'transparent', // Попробуем убрать границу
             colorErrorHover: 'var(--neo-danger-bg-hover)',
             colorErrorActive: 'var(--neo-danger-bg-active)', 
             
             // Общие
             borderRadius: 6, // Явно задаем скругление и для кнопок
             borderRadiusLG: 8,
             borderRadiusSM: 4,
             controlHeight: 36, // Немного увеличим высоту кнопок
             fontSize: 15, // Шрифт как в меню
          }
        }
      }}
    >
      <Layout style={{ minHeight: '100vh' }}>
        <style>{menuStyles}</style> { /* Добавляем наши стили */ }
        <Sider 
          collapsible 
          collapsed={isCollapsed} 
          onCollapse={setIsCollapsed} 
          breakpoint="lg"
          collapsedWidth={screens?.xs ? 0 : 80}
          trigger={null}
          width={260}
          style={{
            background: token.Layout?.siderBg || '#1A1A20', // Используем токен или дефолт
            position: 'relative',
            overflow: 'auto',
            scrollbarWidth: 'thin',
            scrollbarColor: 'rgba(157, 106, 245, 0.5) rgba(0,0,0,0.2)',
          }}
          className="main-layout-sider"
        >
           {/* Разделитель */}
           <div style={{
              position: 'absolute',
              right: 0,
              top: 0,
              bottom: 0,
              width: '1px',
              background: 'linear-gradient(to bottom, transparent, rgba(157, 106, 245, 0.3), transparent)',
              opacity: 0.8,
              zIndex: 1,
           }}></div>
          {/* Логотип */}
          <Flex justify="center" align="middle" style={{ padding: '0 10px' }}>
            <img
              style={finalLogoStyle}
              src={isCollapsed ? "/images/logo-icon.png" : "/images/Logo_NEW2.png"}
              alt="OFS Global Logo"
              onClick={() => navigate('/')}
              onMouseEnter={() => setIsLogoHovered(true)}
              onMouseLeave={() => setIsLogoHovered(false)}
            />
          </Flex>
          {/* Меню - Возвращаем компонент MenuListItems */}
          <MenuListItems isCollapsed={isCollapsed} /> 
          
          {/* Кнопка сворачивания - ПЕРЕМЕЩАЕМ ВНИЗ */}
          <div style={{ 
            position: 'sticky', // Прилипает к низу при скролле
            bottom: 0, 
            padding: '16px 0', // Отступы сверху/снизу
            textAlign: 'center',
            background: token.Layout?.siderBg || '#1A1A20', // Фон как у сайдбара
            borderTop: `1px solid ${token.colorBorderSecondary || 'rgba(255, 255, 255, 0.1)'}` // Линия сверху
           }}>
            <Tooltip title={isCollapsed ? "Развернуть" : "Свернуть"} placement="right">
               <Button
                 type="text" // Сделаем текстовой для лучшего вида внизу
                 shape="circle"
                 icon={isCollapsed ? <MenuUnfoldOutlined style={{fontSize: '18px'}} /> : <MenuFoldOutlined style={{fontSize: '18px'}}/>}
                 onClick={toggleSidebar}
                 style={{ 
                   color: 'rgba(255, 255, 255, 0.65)', // Цвет иконки
                 }}
               />
            </Tooltip>
           </div>
        </Sider>
        <Layout className="site-layout">
          <Header 
            style={{
              padding: token.Layout?.headerPadding || '0 24px',
              background: token.Layout?.headerBg || '#1F1F24',
              display: 'flex',
              alignItems: 'center'
            }}
          >
            <TopBar />
          </Header>
          <Content style={contentStyle} className="main-content">
            <App>
              <Outlet />
            </App>
          </Content>
          <Footer style={{ textAlign: 'center', background: token.colorBgContainer }}> 
             ©{new Date().getFullYear()} OFS Global. Все права защищены.
          </Footer>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
};

export default MainLayout;