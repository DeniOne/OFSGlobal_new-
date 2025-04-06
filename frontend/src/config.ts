/**
 * Конфигурационные параметры приложения
 */

/// <reference types="vite/client" />

// Расширяем тип ImportMeta для TypeScript
interface ImportMetaEnv {
  VITE_API_URL?: string;
  // Добавьте здесь другие переменные окружения при необходимости
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Меняем порт на 8001, так как бэкенд теперь работает там
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

// Настройки загрузки файлов
export const UPLOAD_MAX_SIZE = 5 * 1024 * 1024; // 5MB
export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif'];
export const ALLOWED_DOCUMENT_TYPES = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];

// Константы для использования в компонентах формы
export const MAX_FILE_SIZE = UPLOAD_MAX_SIZE;
export const ALLOWED_FILE_TYPES = ALLOWED_IMAGE_TYPES;

// Параметры пагинации по умолчанию
export const DEFAULT_PAGE_SIZE = 10;
export const DEFAULT_PAGE = 1;

// Интервал автоматического обновления данных (в миллисекундах)
export const AUTO_REFRESH_INTERVAL = 60000; // 1 минута

// Текст ошибок
export const ERROR_MESSAGES = {
  fileTooLarge: 'Размер файла превышает максимально допустимый (5 MB)',
  fileTypeNotAllowed: 'Неподдерживаемый тип файла',
  defaultError: 'Произошла ошибка при обработке запроса',
  networkError: 'Ошибка сети. Проверьте подключение к интернету'
};

// Настройки для организационной структуры
export const ORG_STRUCTURE_CONFIG = {
  maxLevels: 10,
  levelColors: [
    '#3f51b5', // Уровень 1 - высший
    '#4527a0',
    '#673ab7',
    '#7b1fa2',
    '#9c27b0',
    '#c2185b',
    '#d32f2f',
    '#e64a19',
    '#f57c00',
    '#ffa000'  // Уровень 10 - низший
  ]
};

// Экспорт всех конфигурационных параметров в одном объекте
export const config = {
  apiUrl: API_URL,
  upload: {
    maxSize: UPLOAD_MAX_SIZE,
    allowedImageTypes: ALLOWED_IMAGE_TYPES,
    allowedDocumentTypes: ALLOWED_DOCUMENT_TYPES,
    maxFileSize: MAX_FILE_SIZE,
    allowedFileTypes: ALLOWED_FILE_TYPES,
  },
  pagination: {
    defaultPageSize: DEFAULT_PAGE_SIZE,
    defaultPage: DEFAULT_PAGE,
  },
  autoRefreshInterval: AUTO_REFRESH_INTERVAL,
  errorMessages: ERROR_MESSAGES,
  orgStructure: ORG_STRUCTURE_CONFIG,
  visualization: {
    colors: {
      legal: { primary: '#1976d2', secondary: '#42a5f5' },      // Синие оттенки для юридической структуры
      physical: { primary: '#2e7d32', secondary: '#66bb6a' },   // Зеленые оттенки для физической структуры
      functional: { primary: '#ed6c02', secondary: '#ff9800' }, // Оранжевые оттенки для функциональной структуры
    },
    zoomLevels: {
      min: 0.5,
      max: 2,
      default: 1,
      step: 0.1
    }
  },
  telegramBot: {
    statusCheckInterval: 30000, // 30 секунд
    approvalTimeout: 24 * 60 * 60 * 1000, // 24 часа
    autoRejectTime: 72 * 60 * 60 * 1000, // 72 часа
  }
}; 