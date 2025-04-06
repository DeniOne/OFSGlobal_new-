import React from 'react';

const TopPanel: React.FC = () => {
  return (
    <div
      style={{
        height: '64px',
        backgroundColor: 'transparent',
        display: 'flex',
        alignItems: 'center',
        padding: '0 24px',
        justifyContent: 'flex-end', // Элементы будут справа
      }}
    >
      {/* Здесь будет поиск и другие элементы */}
    </div>
  );
};

export default TopPanel; 