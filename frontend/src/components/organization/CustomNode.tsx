import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Typography, Badge, Avatar } from 'antd';
import { CommentOutlined } from '@ant-design/icons';
import { Comment } from './types';

interface CustomNodeData {
  label: string;      // Название сущности
  position?: string;  // Должность
  staff?: string;     // Сотрудник на должности (вместо manager)
  avatar?: string;    // Аватар
  comments?: Comment[];
  activeComments: number;
  borderColor: string;
  type: string;
}

const { Text, Title } = Typography;

const CustomNode: React.FC<NodeProps<CustomNodeData>> = ({ data, selected }) => {
  const { label, position, staff, avatar, activeComments, borderColor, type } = data;
  
  return (
    <div
      style={{
        width: '240px',
        padding: '10px 12px',
        backgroundColor: 'rgba(18, 18, 24, 0.9)',
        borderRadius: '6px',
        border: `2px solid ${borderColor}`,
        boxShadow: selected 
          ? `0 0 10px 2px ${borderColor}` 
          : '0 4px 12px rgba(0, 0, 0, 0.3)',
        transition: 'all 0.2s ease',
        position: 'relative',
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#ffffff',
        cursor: 'pointer'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = 'rgba(25, 25, 35, 0.95)';
        e.currentTarget.style.transform = 'translateY(-2px)';
        e.currentTarget.style.boxShadow = `0 6px 16px rgba(0, 0, 0, 0.4), 0 0 0 1px ${borderColor}`;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'rgba(18, 18, 24, 0.9)';
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = selected 
          ? `0 0 10px 2px ${borderColor}` 
          : '0 4px 12px rgba(0, 0, 0, 0.3)';
      }}
    >
      {/* Коннекторы для входящих и исходящих связей */}
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: borderColor, width: '12px', height: '12px', top: '-6px' }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: borderColor, width: '12px', height: '12px', bottom: '-6px' }}
      />
      
      {/* Аватар сотрудника (если есть) */}
      <div style={{ marginRight: '16px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Avatar
          src={avatar}
          style={{
            width: 48,
            height: 48,
            backgroundColor: avatar ? undefined : 'rgba(157, 106, 245, 0.7)',
            border: `2px solid ${borderColor}`,
            boxShadow: '0 0 8px rgba(0, 0, 0, 0.3)'
          }}
        >
          {!avatar && label.substring(0, 1).toUpperCase()}
        </Avatar>
      </div>
      
      {/* Текстовая информация - выравнивание по центру вертикально */}
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'center',
        alignItems: 'center',
        flex: 1,
        minHeight: '60px',
        width: '100%'
      }}>
        {/* Название сущности */}
        <Text
          strong
          style={{
            marginBottom: '4px',
            color: '#ffffff',
            fontSize: '0.9rem',
            textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            width: '100%',
            textAlign: 'center'
          }}
        >
          {label}
        </Text>
        
        {/* Должность */}
        {position && (
          <Text
            style={{
              marginBottom: position && staff ? '4px' : 0,
              color: '#d0d0d0',
              fontFamily: 'monospace',
              fontWeight: 400,
              fontSize: '0.75rem',
              backgroundColor: 'rgba(0, 0, 0, 0.2)',
              paddingLeft: '8px',
              paddingRight: '8px',
              paddingTop: '3px',
              paddingBottom: '3px',
              borderRadius: '4px',
              width: '95%',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              textAlign: 'center'
            }}
          >
            {position}
          </Text>
        )}
        
        {/* Сотрудник на должности */}
        {staff && (
          <Text
            italic
            style={{
              color: '#aaaaaa',
              fontSize: '0.7rem',
              fontWeight: 400,
              width: '95%',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              textAlign: 'center'
            }}
          >
            {staff}
          </Text>
        )}
      </div>
      
      {/* Индикатор комментариев */}
      {activeComments > 0 && (
        <Badge
          count={activeComments}
          style={{
            position: 'absolute',
            top: '5px',
            right: '5px',
          }}
        >
          <CommentOutlined style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '1.2rem' }} />
        </Badge>
      )}
    </div>
  );
};

export default CustomNode; 