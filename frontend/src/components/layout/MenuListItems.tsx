import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Menu, Tooltip } from 'antd';
import type { MenuProps } from 'antd';
import {
  AppstoreOutlined,
  ApartmentOutlined,
  DeploymentUnitOutlined,
  TeamOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  PartitionOutlined,
  FunctionOutlined,
  IdcardOutlined,
  NodeExpandOutlined,
  PieChartOutlined,
  ShareAltOutlined,
  UserSwitchOutlined,
  LayoutOutlined,
  DatabaseOutlined,
  BankOutlined,
  // AimOutlined, // Раскомментировать, когда понадобится ЦКП
} from '@ant-design/icons';

// Новая структура меню для ОФС модуля
const menuItemsData = [
  // 1. Dashboard
  {
    key: "/dashboard",
    icon: <PieChartOutlined />,
    label: "Dashboard",
    path: "/dashboard",
  },
  // 2. Раздел ПРОСМОТРА структуры
  {
    key: "/structure",
    icon: <AppstoreOutlined />,
    label: "Структура компании",
    children: [
      {
        key: "/structure/chart",
        icon: <NodeExpandOutlined />,
        label: "Визуальная схема",
        path: "/structure/chart",
      },
      {
        key: "/structure/divisions",
        icon: <ApartmentOutlined />,
        label: "Подразделения",
        path: "/structure/divisions",
      },
      {
        key: "/structure/functions",
        icon: <FunctionOutlined />,
        label: "Функции",
        path: "/structure/functions",
      },
      {
        key: "/structure/positions",
        icon: <IdcardOutlined />,
        label: "Должности",
        path: "/structure/positions",
      },
    ],
  },
  // 3. Раздел УПРАВЛЕНИЯ данными (CRUD)
  {
    key: "/admin",
    icon: <SettingOutlined />,
    label: "Управление данными",
    children: [
      {
        key: '/admin/organizations',
        label: 'Организации',
        path: '/admin/organizations',
        icon: <BankOutlined />,
      },
      {
        key: '/admin/divisions',
        label: 'Департаменты',
        path: '/admin/divisions',
        icon: <ApartmentOutlined />,
      },
      {
        key: '/admin/sections',
        label: 'Отделы',
        path: '/admin/sections',
        icon: <PartitionOutlined />,
      },
      {
        key: '/admin/functions',
        label: 'Функции',
        path: '/admin/functions',
        icon: <FunctionOutlined />,
      },
      {
        key: "/admin/positions",
        icon: <IdcardOutlined />,
        label: "Должности",
        path: "/admin/positions", // Ссылка на управление здесь
      },
      {
        key: "/admin/staff-assignments",
        icon: <TeamOutlined />,
        label: "Сотрудники",
        path: "/admin/staff-assignments",
      },
    ],
  },
  // 4. Разделитель
  { type: 'divider' },
  // 5. Личные настройки и настройки модуля
  {
    key: "/my-settings",
    icon: <UserOutlined />,
    label: "Мои настройки",
    path: "/my-settings",
  },
  {
    key: "/settings",
    icon: <SettingOutlined />, // Можно другую иконку
    label: "Настройки модуля",
    path: "/settings",
  },
  // 6. Разделитель
  { type: 'divider' },
  // 7. Выход
  {
    key: "logout",
    icon: <LogoutOutlined />,
    label: "Выход",
  },
];

// Функция для преобразования структуры меню
const processMenuItems = (items: any[], isCollapsed: boolean, level: number = 0): MenuProps['items'] => {
  // const { logout } = useAuth(); 
  const handleLogout = () => {
    console.log('Выход...');
    // logout(); 
  };

  return items.map(item => {
    if (item.type === 'divider') {
      return { type: 'divider' };
    }
    
    // Убираем targetPath, он больше не нужен для Link
    const labelContent = item.label;
    
    // Стили для элементов (применяем к span)
    const itemStyle: React.CSSProperties = {};
    if (level > 0 && !isCollapsed) {
      itemStyle.fontSize = '13px'; 
      itemStyle.borderLeft = '3px solid #555'; 
      itemStyle.paddingLeft = '11px'; 
      // Добавим display: block, чтобы span занимал всю ширину и бордер рисовался корректно
      itemStyle.display = 'block'; 
      itemStyle.lineHeight = 'normal'; // Сброс высоты строки на всякий случай
    }

    let labelElement: React.ReactNode;
    if (item.key === 'logout') {
      labelElement = <span onClick={handleLogout} style={itemStyle}>{labelContent}</span>;
    } else {
      // Для всех остальных пунктов (включая SubMenu) просто текст в span со стилем
      labelElement = <span style={itemStyle}>{labelContent}</span>; 
    }

    const menuItem: any = {
      key: item.key, // Ключ теперь используется для навигации в onClick
      icon: item.icon,
      label: isCollapsed ? (
        <Tooltip title={labelContent} placement="right">
          {/* В свернутом виде для обычных пунктов нужна будет обертка для клика? */}
          {/* Пока оставляем просто иконку, клик будет обрабатывать Menu */} 
           <div>{item.icon}</div> 
        </Tooltip>
      ) : labelElement,
    };

    if (item.children) {
      menuItem.children = processMenuItems(item.children, false, level + 1);
    }
    
    // onClick для выхода добавляется ниже, в основном компоненте

    return menuItem;
  });
};

interface MenuListItemsProps {
  isCollapsed: boolean;
}

const MenuListItems: React.FC<MenuListItemsProps> = ({ isCollapsed }) => {
  const location = useLocation();
  const navigate = useNavigate(); // Используем хук навигации
  // const { logout } = useAuth();

  const [openKeys, setOpenKeys] = useState<string[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<string[]>([location.pathname]);

  useEffect(() => {
    const currentPath = location.pathname;
    setSelectedKeys([currentPath]);
    const findParentKey = (items: any[], childPath: string): string | null => {
        for (const item of items) {
            if (item.children) {
                if (item.children.some((child: any) => child.path === childPath || child.key === childPath)) { // Проверяем и path и key
                    return item.key;
                }
            }
        }
        return null;
    };
    const parentKey = findParentKey(menuItemsData, currentPath);
    if (parentKey && !openKeys.includes(parentKey) && !isCollapsed) { // Не открываем автоматом, если свернуто
         setOpenKeys([parentKey]);
    } else if (!parentKey && !menuItemsData.some(item => item.key === currentPath && item.children)) {
         setOpenKeys([]);
    }
  }, [location.pathname, isCollapsed]); // Добавляем isCollapsed в зависимости

  // Обработчик открытия/закрытия подменю
  const handleOpenChange: MenuProps['onOpenChange'] = (keys) => {
    const latestOpenKey = keys.find(key => !openKeys.includes(key));
    if (latestOpenKey) {
      setOpenKeys([latestOpenKey]);
    } else {
      setOpenKeys([]);
    }
  };

  // Обработчик клика для навигации и выхода
  const handleMenuClick: MenuProps['onClick'] = (e) => {
    const key = e.key;
    
    if (key === 'logout') {
      console.log('Выход...');
      // logout();
      return; // Выходим из обработчика
    }

    // Проверяем, является ли ключ путем (начинается с /) и не является ли ключом подменю
    const isPath = key.startsWith('/');
    const isSubMenuKey = menuItemsData.some(item => item.key === key && item.children);
    
    if (isPath && !isSubMenuKey) {
      navigate(key); // Используем navigate для перехода
    }
    // Если кликнули по заголовку подменю, ничего не делаем (открытие/закрытие обрабатывает onOpenChange)
  };

  const processedItems = processMenuItems(menuItemsData, isCollapsed, 0);

  return (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={selectedKeys}
      openKeys={isCollapsed ? [] : openKeys} // В свернутом режиме всегда пусто
      onOpenChange={handleOpenChange}
      onClick={handleMenuClick} // Используем наш обработчик клика
      inlineCollapsed={isCollapsed}
      items={processedItems}
      inlineIndent={36} 
      style={{ 
        backgroundColor: '#1A1A20', 
        borderRight: 0, 
        padding: '0', 
      }}
    />
  );
};

export default MenuListItems; 