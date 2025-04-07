import React, { ButtonHTMLAttributes, useState } from 'react';
import '../../styles/neomorphism.css';
import classNames from 'classnames';
import { LoadingOutlined } from '@ant-design/icons';

// Типы, которые соответствуют основным типам кнопок Ant Design
type ButtonType = 'default' | 'primary' | 'danger';

// Пропсы для нашей кнопки (расширяем от HTML-кнопки)
interface NeoButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  buttonType?: ButtonType;
  className?: string;
  icon?: React.ReactNode;
  loading?: boolean;
  size?: 'small' | 'middle' | 'large';
}

export const NeoButton: React.FC<NeoButtonProps> = ({
  children,
  buttonType = 'default',
  className = '',
  icon,
  onClick,
  disabled,
  loading = false,
  style,
  size = 'middle',
  ...restProps
}) => {
  // Состояния для отслеживания hover и active
  const [isHovered, setIsHovered] = useState(false);
  const [isActive, setIsActive] = useState(false);
  
  // Индикатор загрузки
  const loadingIcon = <LoadingOutlined style={{ marginRight: '8px' }} spin />;

  // Получаем размеры в зависимости от параметра size
  const getPadding = (): string => {
    switch (size) {
      case 'small':
        return '6px 12px';
      case 'large':
        return '16px 32px';
      case 'middle':
      default:
        return '12px 24px';
    }
  };

  const getFontSize = (): string => {
    switch (size) {
      case 'small':
        return '0.85rem';
      case 'large':
        return '1.15rem';
      case 'middle':
      default:
        return '1rem';
    }
  };

  // Определяем цвета и тени напрямую в JSX
  const getButtonColor = (): string => {
    if (buttonType === 'primary') {
      if (disabled || loading) return '#1890ff';
      if (isActive) return '#096dd9';
      if (isHovered) return '#40a9ff';
      return '#1890ff';
    } else if (buttonType === 'danger') {
      if (disabled || loading) return '#ff4d4f';
      if (isActive) return '#cf1322';
      if (isHovered) return '#ff7875';
      return '#ff4d4f';
    } else {
      // default
      if (disabled || loading) return '#2a2a2a';
      if (isActive) return '#202020';
      if (isHovered) return '#323232';
      return '#2a2a2a';
    }
  };

  // Получаем цвет текста в зависимости от типа кнопки
  const getTextColor = (): string => {
    if (buttonType === 'primary' || buttonType === 'danger') {
      return '#ffffff';
    } else {
      // default
      return isActive ? 'rgba(255, 255, 255, 0.6)' : isHovered ? '#ffffff' : 'rgba(255, 255, 255, 0.8)';
    }
  };

  // Получаем тени
  const getBoxShadow = (): string => {
    if (disabled || loading) {
      return 'none';
    }
    
    if (isActive) {
      return 'inset -1px -1px 1px rgba(255, 255, 255, 0.05), inset 1px 1px 1px rgba(0, 0, 0, 0.5)';
    }
    
    if (isHovered) {
      return '-3px -3px 3px rgba(255, 255, 255, 0.15), 3px 3px 3px rgba(0, 0, 0, 0.4)';
    }
    
    return '-3px -3px 3px rgba(255, 255, 255, 0.1), 3px 3px 3px rgba(0, 0, 0, 0.3)';
  };

  // Формируем классы
  const buttonClasses = classNames(
    'btn-neo', // Базовый класс неоморфизма
    className, // Добавляем внешние классы
    { 
      disabled: disabled || loading, // Добавляем класс disabled если кнопка отключена или в процессе загрузки
    }
  );

  // Обработчик клика с учетом состояния loading
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (loading || disabled) {
      e.preventDefault();
      return;
    }
    onClick?.(e);
  };

  // Создаем стили напрямую
  const buttonStyles = {
    backgroundColor: getButtonColor(),
    color: getTextColor(),
    boxShadow: getBoxShadow(),
    border: 'none',
    outline: 'none',
    padding: getPadding(),
    fontSize: getFontSize(),
    fontWeight: 500,
    borderRadius: '6px',
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    userSelect: 'none' as 'none',
    textAlign: 'center' as 'center', 
    display: 'inline-block' as 'inline-block',
    verticalAlign: 'middle' as 'middle',
    opacity: disabled || loading ? 0.6 : 1,
    transition: 'all 0.2s ease-in-out',
    ...style,
  };

  return (
    <button
      className={buttonClasses}
      onClick={handleClick}
      disabled={disabled || loading}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setIsActive(false);
      }}
      onMouseDown={() => setIsActive(true)}
      onMouseUp={() => setIsActive(false)}
      style={buttonStyles}
      {...restProps}
    >
      {loading ? loadingIcon : icon && <span className="neo-button-icon">{icon}</span>}
      {children}
    </button>
  );
};

export default NeoButton; 