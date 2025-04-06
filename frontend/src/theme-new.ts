// frontend/src/theme.ts
import { theme } from 'antd';
const { darkAlgorithm } = theme;

// Базовая конфигурация темы для Ant Design
export const antdTheme = {
  token: {
    // Фиолетовый акцентный цвет как на картинке
    colorPrimary: '#9D6AF5',
    
    // Скругление углов (как на карточках с картинке)
    borderRadius: 8,
    
    // Основные цвета фона и текста
    colorBgLayout: '#121215',      // Темный фон приложения
    colorBgContainer: '#1A1A20',   // Цвет фона контейнеров/карточек
    colorBgElevated: '#222228',    // Цвет приподнятых элементов
    
    // Цвета текста
    colorText: '#ffffff',          // Основной цвет текста
    colorTextSecondary: '#aaaaaa', // Вторичный цвет текста
    
    // Тени и эффекты
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.5)',
    boxShadowSecondary: '0 8px 16px rgba(157, 106, 245, 0.15)',
    
    // Градиенты можно применять через CSS
    
    // Основной шрифт
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    // Настройки для карточек
    Card: {
      colorBgContainer: '#222228',
      borderRadiusLG: 12,
    },
    // Настройки для кнопок
    Button: {
      borderRadius: 20,  // Круглые кнопки как на дизайне
      controlHeight: 40, // Высота кнопок
    },
    // Настройки для таблиц
    Table: {
      colorBgContainer: '#1A1A20',
      colorText: '#ffffff',
    },
    // Настройки для графиков
    Layout: {
      colorBgHeader: 'transparent',
      colorBgBody: '#121215',
      colorBgTrigger: '#1A1A20',
    },
    Menu: {
      colorItemBg: 'transparent',
      colorItemText: '#ffffff',
      colorItemTextSelected: '#9D6AF5',
      colorItemBgSelected: 'rgba(157, 106, 245, 0.15)',
      colorItemTextHover: '#ffffff',
      colorBgContainer: '#1A1A20',
    },
  },
  algorithm: darkAlgorithm, // Используем темный алгоритм расчета цветов
};

// Добавляем стили для фиолетовых градиентов, которые можно подключить к CSS
export const gradients = {
  primaryGradient: 'linear-gradient(135deg, #9D6AF5 0%, #b28aff 100%)',
  accentGradient: 'linear-gradient(45deg, #9D6AF5 0%, #7048bb 100%)',
  cardGradient: 'linear-gradient(180deg, rgba(157, 106, 245, 0.2) 0%, rgba(117, 66, 205, 0.1) 100%)',
}; 