import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Table,
  Space,
  Modal,
  Form,
  Input,
  Spin,
  Switch,
  Typography,
  Popconfirm,
  App, // Используем App для message
  Card,
  Button as AntButton // Импортируем стандартную кнопку для Popconfirm, если нужно
} from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import api from '../services/api';
import { CultNeumorphButton } from '../components/ui/CultNeumorphButton';
import type { ColumnsType } from 'antd/es/table';

const { Title } = Typography;
const { TextArea } = Input;

// Интерфейс для Функции (можно взять из types/organization.ts, если он там есть)
interface Function {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const AdminFunctionsPage: React.FC = () => {
  const { message } = App.useApp();
  const [tableLoading, setTableLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [functions, setFunctions] = useState<Function[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<Function | null>(null);

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
    message.destroy(); 
    
    try {
      // Используем allSettled для унификации
      const [responseResult] = await Promise.allSettled([
        api.get('/functions/', { signal })
      ]);

      if (responseResult.status === 'fulfilled') {
        if (!signal.aborted) {
          setFunctions(responseResult.value.data);
        }
      } else { // status === 'rejected'
        if (!signal.aborted) {
          if (responseResult.reason && responseResult.reason.name !== 'AbortError') {
            console.error('[AdminFunctionsPage] Ошибка при загрузке функций:', responseResult.reason);
            message.error('Не удалось загрузить список функций.');
          }
          setFunctions([]);
        }
      }

    } catch (error: any) {
       if (error.name === 'AbortError') {
         console.log('[AdminFunctionsPage] Fetch aborted');
         return; 
       }
       console.error('[AdminFunctionsPage] Непредвиденная ошибка при загрузке функций:', error);
       message.error('Произошла непредвиденная ошибка при загрузке функций.');
       setFunctions([]);
    } finally {
       if (!signal.aborted) {
          setTableLoading(false);
          abortControllerRef.current = null;
      }
    }
  }, [message]);

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
  const handleEdit = (record: Function) => {
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
      // Можно добавить обработку полей перед отправкой, если нужно

      if (editingItem) {
        await api.put(`/functions/${editingItem.id}`, dataToSend);
        message.success('Функция успешно обновлена');
      } else {
        await api.post('/functions/', dataToSend);
        message.success('Функция успешно создана');
      }
      setIsModalVisible(false);
      setEditingItem(null);
      fetchData(); // Обновляем таблицу
    } catch (error: any) {
      console.error('[AdminFunctionsPage] Ошибка при сохранении функции:', error);
      let errorMessage = 'Ошибка при сохранении функции';
        // TODO: Добавить парсинг ошибок валидации с бэка, как в других админках
      message.error(errorMessage);
    } finally {
      setModalLoading(false);
    }
  };

  // Логика удаления
  const handleDelete = async (id: number) => {
     try {
        setTableLoading(true);
        await api.delete(`/functions/${id}`);
        message.success('Функция успешно удалена');
        fetchData(); // Обновляем таблицу
      } catch (error) {
        console.error('[AdminFunctionsPage] Ошибка при удалении функции:', error);
        message.error('Ошибка при удалении функции.');
        setTableLoading(false);
      }
  };

  // Колонки для таблицы
  const columns: ColumnsType<Function> = [
    { title: 'ID', dataIndex: 'id', key: 'id', sorter: (a, b) => a.id - b.id, width: 80 },
    { title: 'Название', dataIndex: 'name', key: 'name', sorter: (a, b) => a.name.localeCompare(b.name) },
    { title: 'Код', dataIndex: 'code', key: 'code', width: 150 },
    { title: 'Описание', dataIndex: 'description', key: 'description', render: (text) => text || '-' },
    {
      title: 'Активна',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (isActive ? 'Да' : 'Нет'),
      width: 100
      // TODO: Добавить фильтры по статусу
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 120,
      render: (_: any, record: Function) => (
        <Space size="small">
          <CultNeumorphButton size="small" intent="secondary" onClick={() => handleEdit(record)}>
            <EditOutlined />
          </CultNeumorphButton>
          <Popconfirm
            title="Удалить функцию?"
            description={`Вы уверены, что хотите удалить "${record.name}"?`}
            onConfirm={() => handleDelete(record.id)}
            okText="Да, удалить"
            cancelText="Отмена"
            // Можно использовать стандартную кнопку AntD внутри Popconfirm для наглядности
            okButtonProps={{ danger: true }}
          >
            <CultNeumorphButton size="small" intent="danger">
              <DeleteOutlined />
            </CultNeumorphButton>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Title level={2}>Управление функциями</Title>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <CultNeumorphButton intent="primary" onClick={handleCreate}>
            <PlusOutlined style={{ marginRight: '8px' }} />
            Добавить функцию
          </CultNeumorphButton>
          <CultNeumorphButton onClick={fetchData} loading={tableLoading}>
            <ReloadOutlined style={{ marginRight: '8px' }} />
            Обновить
          </CultNeumorphButton>
        </Space>
        
        <Table<Function>
            columns={columns}
            dataSource={functions}
            rowKey="id"
            loading={tableLoading}
            pagination={{ pageSize: 15 }}
        />
      </Card>

      {/* Модальное окно */}
      <Modal
        title={editingItem ? 'Редактировать функцию' : 'Создать функцию'}
        open={isModalVisible} 
        onCancel={() => setIsModalVisible(false)}
        confirmLoading={modalLoading}
        footer={[
          <CultNeumorphButton key="back" onClick={() => setIsModalVisible(false)}>
              Отмена
          </CultNeumorphButton>,
          <CultNeumorphButton key="submit" intent="primary" loading={modalLoading} onClick={handleSave}>
              {editingItem ? 'Сохранить' : 'Создать'}
          </CultNeumorphButton>,
        ]}
      >
        <Spin spinning={modalLoading}>
          <Form
            form={form}
            layout="vertical"
            name="function_form"
          >
            <Form.Item
              name="name"
              label="Название функции"
              rules={[{ required: true, message: 'Пожалуйста, введите название!' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="code"
              label="Код функции"
              rules={[{ required: true, message: 'Пожалуйста, введите код!' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="description"
              label="Описание"
            >
              <TextArea rows={3} />
            </Form.Item>
            <Form.Item
              name="is_active"
              label="Активна"
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

export default AdminFunctionsPage; 