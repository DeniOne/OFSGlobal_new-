import axios from 'axios';
import { API_URL } from '../config';

// Создаем инстанс axios с базовыми настройками
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    // Добавляем больше информации для отладки
    'X-Requested-With': 'XMLHttpRequest',
  },
  withCredentials: false  // Отключаем для работы без сессий
});

// !!! ОТЛАДОЧНЫЙ ЛОГ: Проверяем реальный baseURL
console.log(`[LOG:API_CONFIG] Используемый baseURL для axios: ${api.defaults.baseURL}`);

// Логи запросов
api.interceptors.request.use(
  config => {
    console.log(`[LOG:API] Отправка ${config.method?.toUpperCase()} запроса на ${config.url}`);
    
    // Проверка токена при каждом запросе
    const token = localStorage.getItem('token');
    if (token) {
      console.log(`[LOG:API] Токен найден: ${token.substring(0, 15)}...`);
      
      // Явно выставляем заголовок авторизации
      config.headers['Authorization'] = `Bearer ${token}`;
      
      // Проверяем, что заголовок установлен
      console.log(`[LOG:API] Заголовок Authorization установлен: ${config.headers['Authorization']}`);
    } else {
      console.log('[LOG:API] Токен не найден в localStorage. Запрос будет отправлен без авторизации.');
      
      // Проверяем URL, требующие авторизации
      const urlRequiresAuth = config.url && 
        !['/login/access-token', '/register', '/health', '/organizations'].includes(config.url);
      
      if (urlRequiresAuth) {
        console.warn(`[LOG:API] Запрос на ${config.url} может требовать авторизации, но токен отсутствует!`);
      }
    }
    
    // Устанавливаем таймаут для всех запросов
    config.timeout = config.timeout || 15000;
    
    return config;
  },
  error => {
    console.error('[LOG:API] Ошибка при отправке запроса:', error);
    return Promise.reject(error);
  }
);

// Перехватчик для обработки ошибок
api.interceptors.response.use(
  response => {
    console.log(`[LOG:API] Успешный ответ от ${response.config.url}`);
    return response;
  },
  error => {
    // Детальное логирование ошибок
    if (error.response) {
      // Сервер вернул ответ с кодом ошибки
      console.error('[API ERROR] Ошибка ответа сервера:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        url: error.response.config.url,
        method: error.response.config.method
      });
    } else if (error.request) {
      // Запрос был сделан, но ответ не получен
      console.error('[API ERROR] Нет ответа от сервера:', {
        request: error.request,
        url: error.config?.url,
        method: error.config?.method
      });
    } else {
      // Что-то пошло не так при настройке запроса
      console.error('[API ERROR] Ошибка настройки запроса:', error.message);
    }
    
    // Возвращаем ошибку для дальнейшей обработки
    return Promise.reject(error);
  }
);

// Вспомогательная функция для добавления задержки между запросами
// и предотвращения конфликтов/гонок запросов
export const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Функция для проверки работоспособности API
export const checkApiHealth = async () => {
  try {
    console.log('[LOG:API] Проверка доступности API');
    
    // Используем обычный запрос с таймстампом для предотвращения кеширования
    const timestamp = new Date().getTime();
    const response = await api.get(`/organizations?_=${timestamp}`, {
      timeout: 5000 // 5 секунд таймаут
    });
    
    console.log('[LOG:API] API доступно, получен ответ');
    return { 
      success: true, 
      data: response.data,
      message: 'API доступно'
    };
  } catch (error: any) {
    console.error('[LOG:API] Ошибка проверки API:', error);
    return {
      success: false,
      status: error.response?.status || 'unknown',
      message: error.message || 'Неизвестная ошибка'
    };
  }
};

export default api; 