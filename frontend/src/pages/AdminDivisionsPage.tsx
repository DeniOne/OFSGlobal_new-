import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Button,
  Table,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Spin,
  message,
  Switch,
  Typography
} from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import api from '../services/api';

const { Title } = Typography;
const { Option } = Select;

// Типы данных
interface Division {
  id: number;
  name: string;
  code: string;
  organization_id?: number;
  parent_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Organization {
  id: number;
  name: string;
}

// !!! ВАЖНО: Переименовать компонент вручную в DivisionsPage !!!
const AdminDivisionsPage: React.FC = () => {
  const [tableLoading, setTableLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<Division | null>(null);

  const [form] = Form.useForm();
  const abortControllerRef = useRef<AbortController | null>(null);

  // Загрузка данных
  const fetchData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setTableLoading(true);
    try {
      const [divisionsResponse, orgResponse] = await Promise.all([
        api.get('/divisions/', { signal }),
        api.get('/organizations/', { signal })
      ]);
      
      setDivisions(divisionsResponse.data);
      setOrganizations(orgResponse.data);

    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('[LOG:Divisions] Fetch aborted');
        return;
      }
      console.error('[LOG:Divisions] Ошибка при загрузке данных:', error);
      message.error('Ошибка при загрузке данных для подразделений.');
    } finally {
       if (!signal.aborted) {
          setTableLoading(false);
          abortControllerRef.current = null;
      }
    }
  }, []);

  useEffect(() => {
    fetchData();
    return () => {
      abortControllerRef.current?.abort();
    };
  }, [fetchData]);

  // Открытие модалки для создания
  const handleCreate = () => {
    setEditingItem(null);
    form.resetFields();
    form.setFieldsValue({ is_active: true }); 
    setIsModalVisible(true);
  };

  // Открытие модалки для редактирования
  const handleEdit = (record: Division) => {
    setEditingItem(record);
    form.setFieldsValue(record);
    setIsModalVisible(true);
  };

  // Логика сохранения
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setModalLoading(true);
      
      const dataToSend = { ...values };
       // Убедимся, что parent_id отправляется как null, если не выбрано
      if (dataToSend.parent_id === undefined || dataToSend.parent_id === '') {
          dataToSend.parent_id = null;
      }
      console.log('[LOG:Divisions] Данные для отправки:', dataToSend);

      if (editingItem) {
        await api.put(`/divisions/${editingItem.id}`, dataToSend);
        message.success('Подразделение успешно обновлено');
      } else {
        await api.post('/divisions/', dataToSend);
        message.success('Подразделение успешно создано');
      }
      setIsModalVisible(false);
      setEditingItem(null);
      fetchData();
    } catch (error: any) {
      console.error('[LOG:Divisions] Ошибка при сохранении:', error);
      let errorMessage = 'Ошибка при сохранении';
        if (error.response?.data?.detail) {
             if (Array.isArray(error.response.data.detail)) {
                errorMessage = error.response.data.detail
                    .map((e: any) => `${e.loc.length > 1 ? e.loc[1] : 'field'}: ${e.msg}`)
                    .join('; ');
            } else if (typeof error.response.data.detail === 'string') {
                errorMessage = error.response.data.detail;
            }
        } else if (error.message) {
             errorMessage = error.message;
        }
      message.error(errorMessage);
    } finally {
      setModalLoading(false);
    }
  };

  // Логика удаления
  const handleDelete = (id: number) => {
    Modal.confirm({
      title: 'Подтвердите удаление',
      content: 'Вы уверены, что хотите удалить это подразделение? Это может затронуть связанные сущности.',
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          setTableLoading(true);
          await api.delete(`/divisions/${id}`);
          message.success('Подразделение успешно удалено');
          fetchData();
        } catch (error) {
          console.error('[LOG:Divisions] Ошибка при удалении:', error);
          message.error('Ошибка при удалении подразделения.');
          setTableLoading(false);
        }
      },
    });
  };

  // Колонки для таблицы
  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', sorter: (a: Division, b: Division) => a.id - b.id },
    { title: 'Название', dataIndex: 'name', key: 'name', sorter: (a: Division, b: Division) => a.name.localeCompare(b.name) },
    { title: 'Код', dataIndex: 'code', key: 'code' },
    {
      title: 'Организация',
      dataIndex: 'organization_id',
      key: 'organization',
      render: (orgId?: number) => organizations.find(org => org.id === orgId)?.name || '—',
      // TODO: Добавить фильтры по организации
    },
    {
      title: 'Родительское подр.',
      dataIndex: 'parent_id',
      key: 'parent',
      render: (parentId?: number) => divisions.find(div => div.id === parentId)?.name || '—',
       // TODO: Добавить фильтры по родителю
    },
    {
      title: 'Активно',
      dataIndex: 'is_active',
      key: 'isActive',
      render: (isActive: boolean) => (isActive ? 'Да' : 'Нет'),
      // TODO: Добавить фильтры по статусу
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: Division) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Button icon={<DeleteOutlined />} danger onClick={() => handleDelete(record.id)} />
        </Space>
      ),
    },
  ];

  // Опции для Select родительского подразделения (исключаем текущее редактируемое)
  const parentDivisionOptions = divisions
    .filter(div => !editingItem || div.id !== editingItem.id)
    .map(div => (
        <Option key={div.id} value={div.id}>{div.name}</Option>
    ));

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Title level={2}>Подразделения</Title>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Добавить подразделение
        </Button>
        <Button icon={<ReloadOutlined />} onClick={fetchData} loading={tableLoading}>
          Обновить
        </Button>
      </Space>
      
      <Spin spinning={tableLoading}>
          <Table 
              columns={columns} 
              dataSource={divisions} 
              rowKey="id" 
              // pagination={{ pageSize: 10 }}
          />
      </Spin>

      {/* Модальное окно */}
      <Modal
        title={editingItem ? 'Редактировать подразделение' : 'Создать подразделение'}
        visible={isModalVisible}
        onOk={handleSave}
        onCancel={() => setIsModalVisible(false)}
        confirmLoading={modalLoading}
        destroyOnClose
      >
        <Spin spinning={modalLoading}>
          <Form form={form} layout="vertical" name="divisionForm">
            <Form.Item
              name="name"
              label="Название"
              rules={[{ required: true, message: 'Пожалуйста, введите название' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="code"
              label="Код"
              rules={[{ required: true, message: 'Пожалуйста, введите код' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="organization_id"
              label="Организация"
               rules={[{ required: true, message: 'Пожалуйста, выберите организацию' }]}
            >
              <Select placeholder="Выберите организацию" loading={tableLoading} allowClear>
                {organizations.map(org => (
                  <Option key={org.id} value={org.id}>{org.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="parent_id"
              label="Родительское подразделение"
            >
              <Select placeholder="Нет родителя" loading={tableLoading} allowClear>
                {/* Опция для отсутствия родителя */}
                {/* <Option value={null}>Нет родителя</Option> */}
                {parentDivisionOptions}
              </Select>
            </Form.Item>
            <Form.Item
              name="is_active"
              label="Активно"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>
          </Form>
        </Spin>
      </Modal>
    </Space>
  );
};

// !!! ВАЖНО: Переименовать компонент вручную в DivisionsPage !!!
export default AdminDivisionsPage; 