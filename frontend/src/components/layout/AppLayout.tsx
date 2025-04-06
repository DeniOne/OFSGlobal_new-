import React from 'react';
import TopPanel from './TopPanel';

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div style={{ 
      minHeight: '100vh',
      display: 'flex',
      backgroundColor: '#0a0a0a',
      backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(33, 150, 243, 0.05) 0%, transparent 100%)',
    }}>
      {/* Левая панель с лого */}
      <div style={{
        width: '280px',
        backgroundColor: 'rgba(17, 25, 40, 0.95)',
        borderRight: '1px solid rgba(255, 255, 255, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        padding: '24px 16px',
      }}>
        <div style={{
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
          marginBottom: '24px'
        }}>
          <img src="/images/Logo_NEW2.png" alt="ОФС" style={{ height: '60px' }} />
        </div>
      </div>

      {/* Основной контент */}
      <div style={{ 
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
      }}>
        <TopPanel />
        <div style={{ 
          flex: 1,
          padding: '24px',
        }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default AppLayout; 