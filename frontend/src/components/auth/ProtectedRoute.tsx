import React, { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  useEffect(() => {
    console.log(`[LOG:ProtectedRoute] Текущий путь: ${window.location.pathname}`);
    if (!loading) {
        console.log(`[LOG:ProtectedRoute] Статус аутентификации ПОСЛЕ ЗАГРУЗКИ: ${isAuthenticated}`);
        const token = localStorage.getItem('token');
        console.log(`[LOG:ProtectedRoute] Токен в localStorage ПОСЛЕ ЗАГРУЗКИ: ${token ? 'присутствует' : 'отсутствует'}`);
        if (token) {
            console.log(`[LOG:ProtectedRoute] Начало токена ПОСЛЕ ЗАГРУЗКИ: ${token.substring(0, 15)}...`);
        }
    }
  }, [isAuthenticated, loading]);

  if (loading) {
    console.log('[LOG:ProtectedRoute] Идет проверка аутентификации (loading)...');
    return <div>Загрузка...</div>;
  }

  if (!isAuthenticated) {
    console.log('[LOG:ProtectedRoute] Пользователь не аутентифицирован ПОСЛЕ ЗАГРУЗКИ, перенаправление на /login');
    return <Navigate to="/login" replace />;
  }

  console.log('[LOG:ProtectedRoute] Пользователь аутентифицирован ПОСЛЕ ЗАГРУЗКИ, отображаем защищенный контент');
  return <>{children}</>;
};

export default ProtectedRoute; 