import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
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
} from '@ant-design/icons';

// Новая структура меню для ОФС модуля
const menuItemsData = [
  {
    key: "/dashboard",
    icon: <PieChartOutlined />,
    label: "Dashboard",
    path: "/dashboard",
  },
  {
    key: "/structure", // Уникальный ключ для родительского элемента
    icon: <AppstoreOutlined />,
    label: "Структура компании",
    children: [
      {
        key: "/structure/chart", // Уникальный ключ
        icon: <PieChartOutlined />,
        label: "Визуальная схема",
        path: "/structure/chart", // Путь для Link (уже правильный)
      },
      {
        key: "/structure/divisions",
        icon: <PartitionOutlined />,
        label: "Департаменты/Отделы",
        path: "/structure/divisions", // Меняем путь
      },
      {
        key: "/structure/functions",
        icon: <FunctionOutlined />,
        label: "Функции",
        path: "/structure/functions", // Меняем путь
      },
      {
        key: "/structure/positions",
        icon: <IdcardOutlined />,
        label: "Должности",
        path: "/structure/positions", // Меняем путь
      },
      {
        key: "/structure/relations",
        icon: <ShareAltOutlined />,
        label: "Функц. связи",
        path: "/structure/relations", // Меняем путь
      },
    ],
  },
  {
    key: "/admin/organizations", 
    icon: <DeploymentUnitOutlined />,
    label: "Организации", 
    path: "/admin/organizations", // Путь для Link
  },
  {
    key: "/admin/staff-assignments",
    icon: <UserSwitchOutlined />,
    label: "Назначения сотрудников",
    path: "/admin/staff-assignments",
  },
  {
    type: 'divider',
  },
  {
    key: "/my-settings",
    icon: <UserOutlined />,
    label: "Мои настройки",
    path: "/my-settings", // TODO: Создать
  },
  {
    key: "/settings", 
    icon: <SettingOutlined />,
    label: "Настройки модуля",
    path: "/settings",
  },
  {
    type: 'divider',
  },
  {
    key: "logout",
    icon: <LogoutOutlined />,
    label: "Выход",
    // path не нужен
  },
];

// Функция для преобразования структуры меню
const processMenuItems = (items: any[], isCollapsed: boolean): MenuProps['items'] => {
  // const { logout } = useAuth(); 
  const handleLogout = () => {
    console.log('Выход...');
    // logout(); 
  };

  return items.map(item => {
    if (item.type === 'divider') {
      return { type: 'divider' };
    }
    
    const targetPath = item.path || item.key; // Используем path, если есть, иначе key
    const labelContent = item.label;
    
    // Создаем элемент label: либо Link, либо span для выхода, либо просто текст для SubMenu
    let labelElement: React.ReactNode;
    if (item.key === 'logout') {
      labelElement = <span onClick={handleLogout}>{labelContent}</span>;
    } else if (item.children) {
      labelElement = labelContent; // Для SubMenu просто текст
    } else {
      labelElement = <Link to={targetPath}>{labelContent}</Link>; // Для обычных Item - Link
    }

    // Создаем основной объект элемента меню
    const menuItem: any = {
      key: item.key,
      icon: item.icon,
      label: isCollapsed ? (
        <Tooltip title={labelContent} placement="right">
          {/* В свернутом виде: если есть path - иконка-ссылка, иначе просто иконка */} 
          {item.path && item.key !== 'logout' ? 
            <Link to={item.path} style={{ display: 'block' }}>{item.icon}</Link> 
            : 
            <div>{item.icon}</div>
          }
        </Tooltip>
      ) : labelElement, // В развернутом виде
    };

    // Рекурсивно обрабатываем дочерние элементы
    if (item.children) {
      menuItem.children = processMenuItems(item.children, false); 
    }
    
    // Добавляем onClick только для кнопки выхода
    if (item.key === 'logout') {
      menuItem.onClick = handleLogout; 
    }

    return menuItem;
  });
};

interface MenuListItemsProps {
  isCollapsed: boolean;
}

const MenuListItems: React.FC<MenuListItemsProps> = ({ isCollapsed }) => {
  const location = useLocation();
  // const { logout } = useAuth();

  const [openKeys, setOpenKeys] = useState<string[]>([]);
  const [selectedKeys, setSelectedKeys] = useState<string[]>([location.pathname]);

  // Эффект для обновления selectedKeys и openKeys при смене URL
  useEffect(() => {
    const currentPath = location.pathname;
    setSelectedKeys([currentPath]);

    // Автоматически открываем родительское подменю при загрузке страницы
    // Проверяем, соответствует ли текущий путь какому-либо дочернему элементу
    const findParentKey = (items: any[], childPath: string): string | null => {
        for (const item of items) {
            if (item.children) {
                if (item.children.some((child: any) => child.path === childPath)) {
                    return item.key; // Возвращаем ключ родителя
                }
                // Рекурсивный поиск (если будет больше уровней вложенности)
                // const foundKey = findParentKey(item.children, childPath);
                // if (foundKey) return foundKey;
            }
        }
        return null;
    };

    const parentKey = findParentKey(menuItemsData, currentPath);
    if (parentKey && !openKeys.includes(parentKey)) {
        // Устанавливаем только родительский ключ, чтобы не хранить лишнее
        // Если нужно сохранять все открытые, используй: setOpenKeys(prev => [...new Set([...prev, parentKey])]);
        setOpenKeys([parentKey]); 
    } else if (!parentKey && !currentPath.startsWith('/structure')) {
         // Если перешли на пункт верхнего уровня, не являющийся структурой, закрываем подменю
         setOpenKeys([]);
    }
    // Не меняем openKeys, если мы уже внутри того же подменю

  }, [location.pathname]); // Убрал openKeys из зависимостей

  // Обработчик для контролируемого открытия/закрытия подменю
  const handleOpenChange: MenuProps['onOpenChange'] = (keys) => {
    setOpenKeys(keys); // Просто сохраняем текущие открытые ключи
  };

  // Обработчик клика (нужен в основном только для выхода)
  const handleMenuClick: MenuProps['onClick'] = (e) => {
    if (e.key === 'logout') {
      console.log('Выход...');
      // logout();
    } 
    // Навигация выполняется через <Link>
  };

  const processedItems = processMenuItems(menuItemsData, isCollapsed);

  return (
    <Menu
      theme="dark"
      mode="inline"
      selectedKeys={selectedKeys}
      // Контролируем открытые ключи только когда меню развернуто
      openKeys={isCollapsed ? undefined : openKeys}
      onOpenChange={handleOpenChange}
      onClick={handleMenuClick} 
      inlineCollapsed={isCollapsed}
      items={processedItems}
      style={{ 
        backgroundColor: '#1A1A20', 
        borderRight: 0, 
        padding: '0 8px',
      }}
    />
  );
};

export default MenuListItems; 