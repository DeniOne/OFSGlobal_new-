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
  App, 
  Card,
  Button as AntButton
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

// Интерфейс для Отдела (Section)
interface Section {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  ckp?: string; // Если используется
  created_at: string;
  updated_at: string;
}

const AdminSectionsPage: React.FC = () => {
  const { message } = App.useApp();
  const [tableLoading, setTableLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [sections, setSections] = useState<Section[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<Section | null>(null);

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
      // Используем allSettled даже для одного запроса для унификации обработки
      const [responseResult] = await Promise.allSettled([
          api.get('/sections/', { signal }) // Запрашиваем Отделы
      ]);
      
      if (responseResult.status === 'fulfilled') {
          if (!signal.aborted) {
            setSections(responseResult.value.data);
          }
      } else { // status === 'rejected'
          if (!signal.aborted) {
            if (responseResult.reason && responseResult.reason.name !== 'AbortError') {
              console.error('[AdminSectionsPage] Ошибка при загрузке отделов:', responseResult.reason);
              message.error('Не удалось загрузить список отделов.');
            }
            setSections([]);
          }
      }
      
    } catch (error: any) { // Этот catch маловероятен с allSettled
       if (error.name === 'AbortError') {
         console.log('[AdminSectionsPage] Fetch aborted');
         return; 
       }
       console.error('[AdminSectionsPage] Непредвиденная ошибка при загрузке отделов:', error);
       message.error('Произошла непредвиденная ошибка при загрузке отделов.');
       setSections([]);
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
  const handleEdit = (record: Section) => {
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
      
      if (editingItem) {
        await api.put(`/sections/${editingItem.id}`, dataToSend);
        message.success('Отдел успешно обновлен');
      } else {
        await api.post('/sections/', dataToSend);
        message.success('Отдел успешно создан');
      }
      setIsModalVisible(false);
      setEditingItem(null);
      fetchData();
    } catch (error: any) {
      console.error('[AdminSectionsPage] Ошибка при сохранении отдела:', error);
      let errorMessage = 'Ошибка при сохранении отдела';
      message.error(errorMessage);
    } finally {
      setModalLoading(false);
    }
  };

  // Логика удаления
  const handleDelete = async (id: number) => {
     try {
        setTableLoading(true);
        await api.delete(`/sections/${id}`);
        message.success('Отдел успешно удален');
        fetchData();
      } catch (error) {
        console.error('[AdminSectionsPage] Ошибка при удалении отдела:', error);
        message.error('Ошибка при удалении отдела.');
        setTableLoading(false);
      }
  };

  // Колонки для таблицы
  const columns: ColumnsType<Section> = [
    { title: 'ID', dataIndex: 'id', key: 'id', sorter: (a, b) => a.id - b.id, width: 80 },
    { title: 'Название', dataIndex: 'name', key: 'name', sorter: (a, b) => a.name.localeCompare(b.name) },
    { title: 'Код', dataIndex: 'code', key: 'code', width: 150 },
    { title: 'Описание', dataIndex: 'description', key: 'description', render: (text) => text || '-' },
    { title: 'ЦКП', dataIndex: 'ckp', key: 'ckp', render: (text) => text || '-' }, // Если ЦКП используется
    {
      title: 'Активен',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (isActive ? 'Да' : 'Нет'),
      width: 100
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 120,
      render: (_: any, record: Section) => (
        <Space size="small">
          <CultNeumorphButton size="small" intent="secondary" onClick={() => handleEdit(record)}>
            <EditOutlined />
          </CultNeumorphButton>
          <Popconfirm
            title="Удалить отдел?"
            description={`Вы уверены, что хотите удалить "${record.name}"?`}
            onConfirm={() => handleDelete(record.id)}
            okText="Да, удалить"
            cancelText="Отмена"
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
      <Title level={2}>Управление отделами</Title>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <CultNeumorphButton intent="primary" onClick={handleCreate}>
            <PlusOutlined style={{ marginRight: '8px' }} />
            Добавить отдел
          </CultNeumorphButton>
          <CultNeumorphButton onClick={fetchData} loading={tableLoading}>
            <ReloadOutlined style={{ marginRight: '8px' }} />
            Обновить
          </CultNeumorphButton>
        </Space>
        
        <Table<Section>
            columns={columns}
            dataSource={sections}
            rowKey="id"
            loading={tableLoading}
            pagination={{ pageSize: 15 }}
        />
      </Card>

      {/* Модальное окно */}
      <Modal
        title={editingItem ? 'Редактировать отдел' : 'Создать отдел'}
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
            name="section_form"
          >
            <Form.Item
              name="name"
              label="Название отдела"
              rules={[{ required: true, message: 'Пожалуйста, введите название!' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="code"
              label="Код отдела"
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
              name="ckp"
              label="ЦКП"
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="is_active"
              label="Активен"
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

export default AdminSectionsPage; 