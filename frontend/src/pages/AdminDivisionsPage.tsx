import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Table,
  Space,
  Modal,
  Form,
  Input,
  Select,
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
import type { Organization as OrgType } from '../types/organization'; // Импортируем тип организации

const { Title } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// Интерфейс для Подразделения
interface Division {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  organization_id: number; 
  parent_id?: number | null;
  ckp?: string;
  created_at: string;
  updated_at: string;
}

const AdminDivisionsPage: React.FC = () => {
  const { message } = App.useApp();
  const [tableLoading, setTableLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [organizations, setOrganizations] = useState<OrgType[]>([]); // Для выбора организации
  const [parentDivisions, setParentDivisions] = useState<Division[]>([]); // Для выбора родительского подразделения
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<Division | null>(null);

  const [form] = Form.useForm();
  const abortControllerRef = useRef<AbortController | null>(null);

  // Загрузка данных (Подразделения и Организации)
  const fetchData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setTableLoading(true);
    message.destroy(); 
    
    try {
      // Используем Promise.allSettled для параллельной загрузки
      const [divisionsResponse, orgResponse] = await Promise.allSettled([
        api.get('/divisions/', { signal }),
        api.get('/organizations?org_type=holding', { signal }) // Загружаем только холдинги для привязки
      ]);

      // Обработка подразделений
      if (divisionsResponse.status === 'fulfilled') {
        if (!signal.aborted) {
           setDivisions(divisionsResponse.value.data);
           setParentDivisions(divisionsResponse.value.data); // Используем тот же список для выбора родителя
        }
      } else {
        if (!signal.aborted) {
          if (divisionsResponse.reason && divisionsResponse.reason.name !== 'AbortError') {
            console.error("[AdminDivisionsPage] Ошибка при загрузке подразделений:", divisionsResponse.reason);
            message.error('Не удалось загрузить список подразделений.');
          }
          setDivisions([]);
          setParentDivisions([]);
        }
      }
      
      // Обработка организаций (холдингов)
      if (orgResponse.status === 'fulfilled') {
         if (!signal.aborted) {
            setOrganizations(orgResponse.value.data);
         }
      } else {
          if (!signal.aborted) {
             if (orgResponse.reason && orgResponse.reason.name !== 'AbortError') {
                console.warn("[AdminDivisionsPage] Ошибка при загрузке организаций (холдингов):", orgResponse.reason);
                message.warning('Не удалось загрузить список организаций для выбора.');
             }
            setOrganizations([]);
          }
      }

    } catch (error: any) {
       if (error.name === 'AbortError') {
         console.log('[AdminDivisionsPage] Fetch aborted by cleanup');
         return; 
       }
       console.error('[AdminDivisionsPage] Непредвиденная ошибка при загрузке данных:', error);
       message.error('Произошла непредвиденная ошибка при загрузке данных.');
       setDivisions([]);
       setOrganizations([]);
       setParentDivisions([]);
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
    // Устанавливаем первую организацию по умолчанию, если они есть
    if (organizations.length > 0) {
      form.setFieldsValue({ organization_id: organizations[0].id });
    }
    setIsModalVisible(true);
  };

  // Открытие модалки для редактирования
  const handleEdit = (record: Division) => {
    setEditingItem(record);
    // Преобразуем null в undefined для Select
    const formData = { ...record, parent_id: record.parent_id === null ? undefined : record.parent_id };
    form.setFieldsValue(formData);
    setIsModalVisible(true);
  };

  // Логика сохранения
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setModalLoading(true);
      
      // Убедимся, что parent_id отправляется как null, если не выбран
      const dataToSend = { 
          ...values, 
          parent_id: values.parent_id === undefined ? null : values.parent_id 
      };

      if (editingItem) {
        await api.put(`/divisions/${editingItem.id}`, dataToSend);
        message.success('Подразделение успешно обновлено');
      } else {
        await api.post('/divisions/', dataToSend);
        message.success('Подразделение успешно создано');
      }
      setIsModalVisible(false);
      setEditingItem(null);
      fetchData(); // Обновляем таблицу
    } catch (error: any) {
      console.error('[AdminDivisionsPage] Ошибка при сохранении подразделения:', error);
      let errorMessage = 'Ошибка при сохранении подразделения';
       // TODO: Добавить парсинг ошибок валидации с бэка
      if (error.response?.data?.detail) {
            errorMessage = error.response.data.detail;
       }
      message.error(errorMessage);
    } finally {
      setModalLoading(false);
    }
  };

  // Логика удаления
  const handleDelete = async (id: number) => {
     try {
        setTableLoading(true);
        await api.delete(`/divisions/${id}`);
        message.success('Подразделение успешно удалено');
        fetchData(); // Обновляем таблицу
      } catch (error: any) {
        console.error('[AdminDivisionsPage] Ошибка при удалении подразделения:', error);
        let errorMessage = 'Ошибка при удалении подразделения.';
        if (error.response?.data?.detail) {
            errorMessage = error.response.data.detail;
         }
        message.error(errorMessage);
        setTableLoading(false);
      }
  };

  // Колонки для таблицы
  const columns: ColumnsType<Division> = [
    { title: 'ID', dataIndex: 'id', key: 'id', sorter: (a, b) => a.id - b.id, width: 80 },
    { title: 'Название', dataIndex: 'name', key: 'name', sorter: (a, b) => a.name.localeCompare(b.name) },
    { title: 'Код', dataIndex: 'code', key: 'code', width: 150 },
    {
       title: 'Организация',
       dataIndex: 'organization_id',
       key: 'organization',
       render: (orgId) => organizations.find(org => org.id === orgId)?.name || '-',
    },
    {
       title: 'Родительское подр.',
       dataIndex: 'parent_id',
       key: 'parent',
       render: (parentId) => parentDivisions.find(div => div.id === parentId)?.name || '-',
    },
    { title: 'ЦКП', dataIndex: 'ckp', key: 'ckp', render: (text) => text || '-', width: 100 },
    {
      title: 'Активно',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (isActive ? 'Да' : 'Нет'),
      width: 100
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 120,
      render: (_: any, record: Division) => (
        <Space size="small">
          <CultNeumorphButton size="small" intent="secondary" onClick={() => handleEdit(record)}>
            <EditOutlined />
          </CultNeumorphButton>
          <Popconfirm
            title="Удалить подразделение?"
            description={`Вы уверены? Это может затронуть дочерние элементы и связи.`}
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
      <Title level={2}>Управление подразделениями</Title>
      <Card>
        <Space style={{ marginBottom: 16 }}>
          <CultNeumorphButton intent="primary" onClick={handleCreate}>
            <PlusOutlined style={{ marginRight: '8px' }} />
            Добавить подразделение
          </CultNeumorphButton>
          <CultNeumorphButton onClick={fetchData} loading={tableLoading}>
            <ReloadOutlined style={{ marginRight: '8px' }} />
            Обновить
          </CultNeumorphButton>
        </Space>
        
        <Table<Division>
            columns={columns}
            dataSource={divisions}
            rowKey="id"
            loading={tableLoading}
            pagination={{ pageSize: 15 }}
        />
      </Card>

      {/* Модальное окно */}
      <Modal
        title={editingItem ? 'Редактировать подразделение' : 'Создать подразделение'}
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
            name="division_form"
          >
            <Form.Item
              name="name"
              label="Название подразделения"
              rules={[{ required: true, message: 'Пожалуйста, введите название!' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="code"
              label="Код подразделения"
              rules={[{ required: true, message: 'Пожалуйста, введите код!' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="organization_id"
              label="Организация (Холдинг)"
              rules={[{ required: true, message: 'Пожалуйста, выберите организацию!' }]}
            >
              <Select placeholder="Выберите организацию">
                {organizations.map(org => (
                  <Option key={org.id} value={org.id}>{org.name}</Option>
                ))}
              </Select>
            </Form.Item>
             <Form.Item
              name="parent_id"
              label="Родительское подразделение (опционально)"
            >
              <Select placeholder="Корневое подразделение" allowClear>
                {parentDivisions
                   .filter(div => !editingItem || div.id !== editingItem.id) // Нельзя выбрать себя родителем
                   .map(div => (
                  <Option key={div.id} value={div.id}>{div.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="description"
              label="Описание"
            >
              <TextArea rows={3} />
            </Form.Item>
            <Form.Item
              name="ckp"
              label="ЦКП (опционально)"
            >
              <Input placeholder="Ценный конечный продукт"/>
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

export default AdminDivisionsPage; 