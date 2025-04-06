import React, { useState, useEffect } from 'react';
import { 
  Modal, 
  Form, 
  Input, 
  Select, 
  Switch, 
  Typography, 
  Space, 
  Button, 
  Alert, 
  Spin,
  Divider
} from 'antd';
import { Division, Organization } from '../../types/organization';
import api from '../../services/api';

const { Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

interface DivisionEditModalProps {
  open: boolean;
  division: Division;
  organizations: Organization[];
  parentDivisions: Division[];
  onClose: () => void;
  onSave: (division: Division) => void;
}

// Уровни иерархии для отделов
const levelOptions = [
  { value: 0, label: 'Организация' },
  { value: 1, label: 'Департамент' },
  { value: 2, label: 'Отдел' },
  { value: 3, label: 'Подразделение' },
  { value: 4, label: 'Группа' }
];

const DivisionEditModal: React.FC<DivisionEditModalProps> = ({ 
  open, 
  division, 
  organizations, 
  parentDivisions,
  onClose, 
  onSave 
}) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Инициализация формы при открытии
  useEffect(() => {
    if (open && division) {
      form.setFieldsValue({
        name: division.name,
        code: division.code || '',
        description: division.description || '',
        level: division.level || 2,
        is_active: division.is_active,
        organization_id: division.organization_id,
        parent_id: division.parent_id
      });
    }
  }, [open, division, form]);
  
  // Сохранение формы
  const handleSave = async (values: any) => {
    setLoading(true);
    setError(null);
    
    try {
      // Подготовка данных
      const divisionData = {
        ...values,
        code: values.code || null,
        description: values.description || null,
      };
      
      let response;
      
      // Если редактируем, используем PUT
      if (division.id) {
        response = await api.put(`/divisions/${division.id}`, divisionData);
      } else {
        response = await api.post('/divisions/', divisionData);
      }
      
      const savedDivision = response.data;
      onSave(savedDivision);
      onClose();
    } catch (err: any) {
      let errorMessage = 'Ошибка при сохранении отдела';
      
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail
            .map((e: any) => `${e.loc.join('.')}: ${e.msg}`)
            .join('; ');
        }
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
      title={division.id ? 'Редактирование подразделения' : 'Новое подразделение'}
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
            level: 2,
            is_active: true,
            organization_id: division.organization_id,
            parent_id: division.parent_id
          }}
        >
          <Form.Item
            name="name"
            label="Название подразделения"
            rules={[
              { required: true, message: 'Пожалуйста, введите название подразделения' },
            ]}
          >
            <Input placeholder="Введите название" />
          </Form.Item>
          
          <Form.Item
            name="code"
            label="Код подразделения"
            rules={[
              { max: 20, message: 'Код не должен превышать 20 символов' },
            ]}
            tooltip="Опциональный уникальный код подразделения"
          >
            <Input placeholder="Например: HR, IT, FIN" />
          </Form.Item>
          
          <Form.Item
            name="organization_id"
            label="Организация"
            rules={[
              { required: true, message: 'Пожалуйста, выберите организацию' },
            ]}
          >
            <Select placeholder="Выберите организацию">
              {organizations.map(org => (
                <Option key={org.id} value={org.id}>{org.name}</Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="level"
            label="Уровень иерархии"
          >
            <Select placeholder="Выберите уровень иерархии">
              {levelOptions.map(option => (
                <Option key={option.value} value={option.value}>{option.label}</Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="parent_id"
            label="Родительское подразделение"
          >
            <Select 
              placeholder="Выберите родительское подразделение"
              allowClear
            >
              <Option value={null}>Корневое подразделение (без родителя)</Option>
              {parentDivisions.map(div => (
                <Option key={div.id} value={div.id}>{div.name}</Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            name="description"
            label="Описание"
            rules={[
              { max: 500, message: 'Описание не должно превышать 500 символов' },
            ]}
          >
            <TextArea 
              placeholder="Введите описание подразделения"
              autoSize={{ minRows: 3, maxRows: 6 }}
            />
          </Form.Item>
          
          <Form.Item
            name="is_active"
            valuePropName="checked"
            label="Статус"
          >
            <Switch 
              checkedChildren="Активно" 
              unCheckedChildren="Неактивно"
            />
          </Form.Item>
          
          <Divider />
          
          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button onClick={handleCancel}>
                Отмена
              </Button>
              <Button type="primary" htmlType="submit" loading={loading}>
                {division.id ? 'Сохранить' : 'Создать'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Spin>
    </Modal>
  );
};

export default DivisionEditModal; 