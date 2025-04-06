import React from "react";
import { Route, Routes } from "react-router-dom";
import ProtectedRoute from "../components/auth/ProtectedRoute";
import DashboardPage from "../pages/DashboardPage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import AdminOrganizationsPage from "../pages/AdminOrganizationsPage";
import StaffPage from "../pages/StaffPage";
import StaffFormPage from "../pages/StaffFormPage";
import FunctionalRelationsPage from "../pages/FunctionalRelationsPage";
import AdminFunctionalRelationsPage from "../pages/AdminFunctionalRelationsPage";
import OrganizationStructurePage from "../pages/OrganizationStructurePage";
import AdminPositionsPage from "../pages/AdminPositionsPage";
import AdminDivisionsPage from "../pages/AdminDivisionsPage";
import AdminStaffPage from "../pages/AdminStaffPage";
import NotFoundPage from "../pages/NotFoundPage";
import MainLayout from "../components/layout/MainLayout";

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Публичные маршруты */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      
      {/* Маршрут по умолчанию - дашборд */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      
      {/* Dashboard */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      
      {/* Админские маршруты */}
      <Route
        path="/admin/organizations"
        element={
          <ProtectedRoute>
            <AdminOrganizationsPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/admin/staff-assignments"
        element={
          <ProtectedRoute>
            <AdminStaffPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/admin/positions"
        element={
          <ProtectedRoute>
            <AdminPositionsPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/admin/divisions"
        element={
          <ProtectedRoute>
            <AdminDivisionsPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/admin/functional-relations"
        element={
          <ProtectedRoute>
            <AdminFunctionalRelationsPage />
          </ProtectedRoute>
        }
      />
      
      {/* Старые или временные маршруты */}
      <Route
        path="/staff"
        element={
          <ProtectedRoute>
            <StaffPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/staff/new"
        element={
          <ProtectedRoute>
            <StaffFormPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/staff/:id/edit"
        element={
          <ProtectedRoute>
            <StaffFormPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/functional-relations"
        element={
          <ProtectedRoute>
            <FunctionalRelationsPage />
          </ProtectedRoute>
        }
      />
      
      <Route
        path="/organization-structure"
        element={
          <ProtectedRoute>
            <OrganizationStructurePage />
          </ProtectedRoute>
        }
      />
      
      {/* Маршрут для страниц, которые не найдены */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export default AppRoutes; 