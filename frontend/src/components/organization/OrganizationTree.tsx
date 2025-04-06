import React, { useEffect, useRef, useState } from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
// Базовый шаблон для последующей реализации с vis.js

interface OrganizationTreeProps {
  organizationId: string;
  readOnly?: boolean;
  viewMode: 'business' | 'legal' | 'territorial';
  displayMode: 'tree' | 'list';
  zoomLevel?: number;
  detailLevel?: number;
}

// Пустой компонент для последующей реализации
const OrganizationTree: React.FC<OrganizationTreeProps> = ({
  organizationId,
  readOnly = false,
  viewMode,
  displayMode,
  zoomLevel = 100,
  detailLevel = 1
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Здесь будет инициализация vis.js Network
    const timer = setTimeout(() => {
      setLoading(false);
    }, 500);

    return () => {
      clearTimeout(timer);
      // Здесь будет очистка ресурсов vis.js
    };
  }, [organizationId, viewMode, displayMode]);

  const antIcon = <LoadingOutlined style={{ fontSize: 60, color: '#9D6AF5' }} spin />;

  return (
    <div style={{ 
      width: '100%', 
      height: '100%', 
      minHeight: '500px',
      backgroundColor: '#121212',
      backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(157, 106, 245, 0.1) 0%, transparent 80%)',
      borderRadius: '8px',
      overflow: 'hidden',
      position: 'relative',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      {loading ? (
        <Spin indicator={antIcon} />
      ) : (
        <div 
          ref={containerRef}
          style={{ 
            width: '100%', 
            height: '100%',
            position: 'relative'
          }}
          className="vis-container"
        >
          {/* Здесь будет рендериться граф vis.js Network */}
        </div>
      )}
    </div>
  );
};

export default OrganizationTree; 