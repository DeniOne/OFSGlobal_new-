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

// Стили для кастомизации меню - ДОБАВЛЯЕМ ТЕНИ И HOVER
const menuStyles = `
  .main-layout-sider .ant-menu-item,
  .main-layout-sider .ant-menu-submenu-title {
    font-size: 15px; 
    padding: 12px 20px !important; // Увеличим отступы для "воздуха"
    height: auto; 
    line-height: normal;
    margin-bottom: 4px !important; // Небольшой отступ между кнопками
    border-radius: 6px; // Легкое скругление
    transition: background 0.2s ease, box-shadow 0.2s ease; // Плавные переходы
  }
  .main-layout-sider .ant-menu-item:hover,
  .main-layout-sider .ant-menu-submenu-title:hover {
    /* Эффект легкого "вдавливания" при наведении */
    background: rgba(255, 255, 255, 0.05) !important;
    box-shadow: inset 1px 1px 2px rgba(0,0,0,0.3), 
                inset -1px -1px 2px rgba(255,255,255,0.05);
  }
  .main-layout-sider .ant-menu-item-selected {
    /* Возвращаем фиолетовый и добавляем объем */
    box-shadow: 1px 1px 3px rgba(0,0,0,0.4), 
                -1px -1px 3px rgba(255,255,255,0.1), 
                inset 0 0 1px rgba(0,0,0,0.2); /* Легкая внутренняя тень для объема */
    font-weight: 600; /* Сделаем текст активного пункта жирнее */
  }
  .main-layout-sider .ant-menu-item .anticon,
  .main-layout-sider .ant-menu-submenu-title .anticon {
    font-size: 18px; 
    vertical-align: middle;
  }
  .main-layout-sider .ant-menu-item span,
  .main-layout-sider .ant-menu-submenu-title span {
    vertical-align: middle; 
    margin-left: 12px; // Увеличим отступ текста от иконки
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
             // Базовые стили для default кнопки
             defaultBg: '#2a2a30',
             defaultColor: 'rgba(255, 255, 255, 0.8)',
             defaultBorderColor: 'rgba(255, 255, 255, 0.15)',
             defaultHoverBg: '#333338',
             defaultHoverColor: '#fff',
             defaultHoverBorderColor: 'rgba(157, 106, 245, 0.7)', 
             defaultActiveBg: '#25252a', // Цвет при нажатии
             defaultActiveBorderColor: 'rgba(157, 106, 245, 0.9)', 
             defaultShadow: '0 1px 2px rgba(0, 0, 0, 0.3)', // Тень для default кнопки
             
             // Стили для primary кнопки
             primaryColor: '#ffffff', // Белый текст на фиолетовом
             colorPrimaryHover: '#ad7ff7', // Чуть светлее при наведении
             colorPrimaryActive: '#8e5cdb', // Темнее при нажатии
             primaryShadow: '0 2px 4px rgba(157, 106, 245, 0.4)', // Фиолетовая тень для primary
             
             // Стили для danger кнопки (будут использоваться с colorError)
             dangerColor: '#ffffff', // Белый текст на красном
             colorErrorHover: '#ff4d4f', // Ярче красный при наведении
             colorErrorActive: '#cf1322', // Темнее красный при нажатии
             dangerShadow: '0 2px 4px rgba(245, 34, 45, 0.4)', // Красная тень для danger
             
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