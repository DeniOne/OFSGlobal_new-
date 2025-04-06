import React from 'react';
import StaffList from '../components/staff/StaffList';
import MainLayout from '../components/layout/MainLayout';

const StaffPage: React.FC = () => {
  return (
    <div style={{ padding: '24px' }}>
      <StaffList />
    </div>
  );
};

export default StaffPage; 