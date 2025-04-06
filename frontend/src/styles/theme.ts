// Тема для Ant Design
import type { ThemeConfig } from 'antd';

// Определяем основные цвета
const primaryColor = '#9D6AF5';
const secondaryColor = '#ff00ff';
const backgroundColor = '#1a1a1a';
const surfaceColor = '#2a2a2a';
const textColor = '#ffffff';

// Создаем тему для Ant Design
export const theme: ThemeConfig = {
  token: {
    colorPrimary: primaryColor,
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorInfo: '#1890ff',
    colorTextBase: textColor,
    colorBgBase: backgroundColor,
    colorBgLayout: backgroundColor,
    colorBgContainer: surfaceColor,
    borderRadius: 6,
    wireframe: false,
    fontFamily: '"Rajdhani", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    Button: {
      borderRadius: 4,
      colorPrimary: primaryColor,
      algorithm: true, // Enable algorithm
    },
    Menu: {
      colorItemBg: surfaceColor,
      colorItemText: textColor,
      colorItemTextSelected: primaryColor,
      colorItemBgSelected: `${primaryColor}20`,
      colorItemTextHover: primaryColor,
      colorItemBgHover: `${primaryColor}10`,
    },
    Card: {
      colorBgContainer: surfaceColor,
      borderRadius: 8,
    },
    Input: {
      colorBgContainer: backgroundColor,
      colorBorder: `${primaryColor}40`,
      colorPrimaryHover: primaryColor,
    },
    Table: {
      colorBgContainer: surfaceColor,
      headerBg: backgroundColor,
    },
    Tabs: {
      inkBarColor: primaryColor,
      colorTextHeading: textColor,
    },
  },
};

export default theme; 