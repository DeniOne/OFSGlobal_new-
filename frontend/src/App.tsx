import React from 'react';
import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import './styles/App.css';
import { App as AntApp } from 'antd';

import MainLayout from './components/layout/MainLayout';
import LandingPage from './pages/LandingPage';
import OrganizationStructurePage from './pages/OrganizationStructurePage';
import FunctionalRelationsPage from './pages/FunctionalRelationsPage';
import DivisionsPage from './pages/divisions/DivisionsPage';
import PositionsPage from './pages/positions/PositionsPage';
import StaffList from './components/staff/StaffList';
import StaffForm from './components/staff/StaffForm';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';

// Новые страницы для новой структуры ОФС
import DashboardPage from './pages/DashboardPage';
import TelegramBotPage from './pages/TelegramBotPage';
import NotFoundPage from './pages/NotFoundPage';

// Новые страницы администрирования с использованием роутера
import AdminOrganizationsPage from './pages/AdminOrganizationsPage';
import AdminStaffPage from './pages/AdminStaffPage';
import AdminDivisionsPage from './pages/AdminDivisionsPage';
import AdminPositionsPage from './pages/AdminPositionsPage';
import AdminFunctionsPage from './pages/AdminFunctionsPage';
import AdminSectionsPage from './pages/AdminSectionsPage';
import FunctionsPage from './pages/FunctionsPage';
import StructureChartPage from './pages/StructureChartPage';
import DemoPage from './pages/DemoPage';

// Новые страницы структуры
import StructurePositionsPage from './pages/structure/StructurePositionsPage';
import StructureFunctionsPage from './pages/structure/StructureFunctionsPage';

// Placeholder компоненты для других страниц
function Reports() { return <div>Reports Page</div>; }
function Profile() { return <div>Profile Page</div>; }
function Settings() { return <div>Settings Page</div>; }

// Добавляем более детальные компоненты для настроек
function MySettingsPage() {
  return (
    <div style={{ color: 'white', padding: '20px' }}>
      <h1>Мои настройки</h1>
      <p>Здесь будут личные настройки пользователя</p>
    </div>
  );
}

function ModuleSettingsPage() {
  return (
    <div style={{ color: 'white', padding: '20px' }}>
      <h1>Настройки модуля</h1>
      <p>Здесь будут настройки модуля системы</p>
    </div>
  );
}

import { AuthProvider } from './hooks/useAuth';

const AppContent: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/landing" element={<LandingPage />} />
      <Route path="/ping" element={<div>Pong!</div>} />
      <Route path="/demo" element={<DemoPage />} />
      
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="structure">
          <Route index element={<Navigate to="/structure/chart" replace />} />
          <Route path="chart" element={<ProtectedRoute><StructureChartPage /></ProtectedRoute>} />
          <Route path="positions" element={<ProtectedRoute><StructurePositionsPage /></ProtectedRoute>} />
          <Route path="functions" element={<ProtectedRoute><StructureFunctionsPage /></ProtectedRoute>} />
          <Route path="divisions" element={<ProtectedRoute><div>Просмотр Подразделений</div></ProtectedRoute>} />
        </Route>
        <Route path="admin">
          <Route index element={<Navigate to="/admin/organizations" replace />} />
          <Route path="organizations" element={<ProtectedRoute><AdminOrganizationsPage /></ProtectedRoute>} />
          <Route path="divisions" element={<ProtectedRoute><AdminDivisionsPage /></ProtectedRoute>} />
          <Route path="sections" element={<ProtectedRoute><AdminSectionsPage /></ProtectedRoute>} />
          <Route path="positions" element={<ProtectedRoute><AdminPositionsPage /></ProtectedRoute>} />
          <Route path="staff-assignments" element={<ProtectedRoute><AdminStaffPage /></ProtectedRoute>} />
          <Route path="functions" element={<ProtectedRoute><AdminFunctionsPage /></ProtectedRoute>} />
        </Route>
        <Route path="my-settings" element={<ProtectedRoute><MySettingsPage /></ProtectedRoute>} />
        <Route path="settings" element={<ProtectedRoute><ModuleSettingsPage /></ProtectedRoute>} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <AntApp>
      <AppContent />
    </AntApp>
  );
};

export default App;