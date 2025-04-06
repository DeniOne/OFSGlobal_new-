import React, { createContext, useCallback, useContext, useEffect, useState, ReactNode } from 'react';
import api from '../services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

// Создаем контекст
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Хук для использования контекста
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Провайдер контекста
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  const checkAuth = useCallback(async () => {
    setLoading(true);
    // Не проверяем авторизацию на странице логина или регистрации
    if (window.location.pathname.includes('/login') || window.location.pathname.includes('/register')) {
      console.log('[LOG:Auth:checkAuth] Страница логина/регистрации, пропускаем проверку авторизации');
      setLoading(false);
      return;
    }

    try {
      // Для проверки аутентификации используем FastAPI эндпоинт GET /users/me
      const token = localStorage.getItem('token');
      console.log(`[LOG:Auth:checkAuth] Перед запросом /users/me, токен: ${token ? 'присутствует' : 'отсутствует'}`);

      if (!token) {
        console.log('[LOG:Auth:checkAuth] Токен отсутствует, пользователь не аутентифицирован');
        setIsAuthenticated(false);
        setLoading(false);
        return;
      }

      // Axios интерцептор уже должен добавлять токен
      // api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      const response = await api.get('/users/me');
      setIsAuthenticated(true);
      console.log('[LOG:Auth:checkAuth] Успешная проверка через /users/me, пользователь аутентифицирован', response.data);
    } catch (error) {
      setIsAuthenticated(false);
      localStorage.removeItem('token'); // Удаляем невалидный токен
      console.log('[LOG:Auth:checkAuth] Ошибка проверки токена, пользователь не аутентифицирован', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    console.log("[LOG:Auth:useEffect] Вызов checkAuth из useEffect");
    checkAuth();
  }, [checkAuth]);

  const login = async (username: string, password: string) => {
    try {
      setLoading(true);
      console.log(`[LOG:Auth] Попытка входа для пользователя: ${username}`);

      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);

      const response = await api.post('/login/access-token', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      console.log('[LOG:Auth] Ответ на запрос логина:', response.data);
      const { access_token } = response.data;

      if (!access_token) {
        console.error('[LOG:Auth] Ошибка: токен отсутствует в ответе!');
        throw new Error('Token missing in response');
      }

      localStorage.removeItem('token'); // На всякий случай
      localStorage.setItem('token', access_token);
      console.log('[LOG:Auth] Успешный вход, токен сохранен');

      setIsAuthenticated(true);
      setLoading(false); // Устанавливаем loading в false после успешного логина

      // Редирект
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 100);

    } catch (error) {
      setLoading(false);
      console.error('[LOG:Auth] Ошибка входа:', error);
      // Здесь можно добавить показ ошибки пользователю
      throw new Error('Login failed');
    }
  };

  const logout = async () => {
    try {
      setLoading(true); // Можно добавить индикатор загрузки при выходе
      console.log('[LOG:Auth] Выход из системы');
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      window.location.href = '/login';
    } catch (error) {
      console.error('[LOG:Auth] Ошибка при выходе:', error);
    } finally {
      setLoading(false);
    }
  };

  const value = {
    isAuthenticated,
    loading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
