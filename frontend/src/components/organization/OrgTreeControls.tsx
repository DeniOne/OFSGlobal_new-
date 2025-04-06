import React from 'react';
import { Radio, Space } from 'antd';
import { ApartmentOutlined, UnorderedListOutlined } from '@ant-design/icons';
import styled from '@emotion/styled';

const StyledRadioGroup = styled(Radio.Group)`
  margin-bottom: 16px;
  margin-left: 8px;
  
  .ant-radio-button-wrapper {
    background-color: rgba(32, 32, 36, 0.9);
    border: 1px solid rgba(45, 45, 55, 0.9);
    color: #fff;
    padding: 8px 16px;
    border-radius: 12px;
    margin-right: 8px;
    transition: all 0.25s ease;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    
    &:hover {
      transform: translateY(-2px);
      background-color: rgba(38, 38, 44, 0.95);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4), 0 0 10px rgba(157, 106, 245, 0.2);
    }
    
    &.ant-radio-button-wrapper-checked {
      background-color: rgba(42, 42, 48, 0.95);
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4), 0 0 20px rgba(157, 106, 245, 0.3);
      border: 1px solid rgba(157, 106, 245, 0.4);
      transform: translateY(-2px);
    }
    
    &:before {
      display: none;
    }
  }
  
  .anticon {
    color: #9D6AF5;
    margin-right: 8px;
    font-size: 16px;
  }
  
  .ant-radio-button-wrapper-checked .anticon {
    color: #b350ff;
    filter: drop-shadow(0 0 8px rgba(157, 106, 245, 0.7));
  }
`;

interface OrgTreeControlsProps {
  displayMode: 'tree' | 'list';
  onDisplayModeChange: (mode: 'tree' | 'list') => void;
}

const OrgTreeControls: React.FC<OrgTreeControlsProps> = ({
  displayMode,
  onDisplayModeChange
}) => {
  const handleChange = (e: any) => {
    onDisplayModeChange(e.target.value);
  };

  return (
    <StyledRadioGroup 
      value={displayMode}
      onChange={handleChange}
      buttonStyle="solid"
    >
      <Radio.Button value="tree">
        <ApartmentOutlined /> Дерево
      </Radio.Button>
      <Radio.Button value="list">
        <UnorderedListOutlined /> Список
      </Radio.Button>
    </StyledRadioGroup>
  );
};

export default OrgTreeControls; 