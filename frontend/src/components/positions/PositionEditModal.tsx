import React, { useState, useEffect } from 'react';
import { 
  Modal, 
  Form, 
  Input, 
  Button, 
  Space, 
  Switch, 
  Alert, 
  Spin,
  Typography,
  Divider
} from 'antd';
import { Position } from '../../types/organization';
import api from '../../services/api';

const { TextArea } = Input;
const { Text } = Typography;

interface ExtendedPosition extends Position {
  organization_id?: number;
}

interface PositionEditModalProps {
  open: boolean;
  position: ExtendedPosition | null; // Null для создания нового
  organizationId: number;
  onClose: () => void;
  onSave: (position: ExtendedPosition) => void;
}

const PositionEditModal: React.FC<PositionEditModalProps> = ({ 
  open, 
  position, 
  organizationId, 
  onClose, 
  onSave 
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Инициализация формы при открытии
  useEffect(() => {
    if (open) {
      if (position) {
        // Режим редактирования - заполняем форму данными
        form.setFieldsValue({
          name: position.name,
          code: position.code || '',
          description: position.description || '',
          is_active: position.is_active
        });
      } else {
        // Режим создания - сбрасываем форму
        form.resetFields();
        form.setFieldsValue({
          is_active: true
        });
      }
    }
  }, [open, position, form]);
  
  // Сохранение формы
  const handleSave = async (values: any) => {
    setLoading(true);
    setError(null);
    
    try {
      const positionData = {
        ...values,
        code: values.code || null,
        description: values.description || null,
        organization_id: organizationId
      };
      
      let response;
      
      // Если редактируем, используем PUT
      if (position) {
        response = await api.put(`/positions/${position.id}`, positionData);
      } else {
        response = await api.post('/positions/', positionData);
      }
      
      const savedPosition = response.data;
      onSave(savedPosition);
      onClose();
    } catch (err: any) {
      let errorMessage = 'Ошибка при сохранении должности';
      
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail
            .map((e: any) => `${e.loc.join('.')}: ${e.msg}`)
            .join('; ');
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCancel = () => {
    form.resetFields();
    onClose();
  };
  
  return (
    <Modal
      title={position ? 'Редактирование должности' : 'Новая должность'}
      open={open}
      onCancel={handleCancel}
      footer={null}
      width={600}
    >
      <Spin spinning={loading}>
        {error && (
          <Alert
            message="Ошибка"
            description={error}
            type="error"
            showIcon
            closable
            onClose={() => setError(null)}
            style={{ marginBottom: 16 }}
          />
        )}
        
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          initialValues={{
            name: '',
            code: '',
            description: '',
            is_active: true
          }}
        >
          <Form.Item
            name="name"
            label="Название должности"
            rules={[
              { required: true, message: 'Пожалуйста, введите название должности' },
            ]}
          >
            <Input placeholder="Введите название" />
          </Form.Item>
          
          <Form.Item
            name="code"
            label="Код должности"
            rules={[
              { max: 20, message: 'Код не должен превышать 20 символов' },
            ]}
            tooltip="Опциональный уникальный код должности"
          >
            <Input placeholder="Например: DEV, PM, HR" />
          </Form.Item>
          
          <Form.Item
            name="description"
            label="Описание"
            rules={[
              { max: 500, message: 'Описание не должно превышать 500 символов' },
            ]}
          >
            <TextArea 
              placeholder="Введите описание должности"
              autoSize={{ minRows: 3, maxRows: 6 }}
            />
          </Form.Item>
          
          <Form.Item
            name="is_active"
            valuePropName="checked"
            label="Статус"
          >
            <Switch 
              checkedChildren="Активная" 
              unCheckedChildren="Неактивная"
            />
          </Form.Item>
          
          <Divider />
          
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={handleCancel}>
                Отмена
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                {position ? 'Сохранить' : 'Создать'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Spin>
    </Modal>
  );
};

export default PositionEditModal; 