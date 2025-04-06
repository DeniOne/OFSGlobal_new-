import React, { useState, useEffect } from 'react';
import { 
  Typography, 
  Table, 
  Button, 
  Space, 
  Modal, 
  Form, 
  Input, 
  Select, 
  message, 
  Popconfirm, // Для подтверждения удаления
  Spin, // Общий спиннер
  Card,
  Checkbox // Добавляем Checkbox для is_active
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { 
  EditOutlined, 
  DeleteOutlined, 
  PlusOutlined, // Аналог AddIcon
  ReloadOutlined, // Аналог RefreshIcon
  SaveOutlined, // Для кнопки сохранения в модалке
  CloseOutlined // Для кнопки отмены в модалке
} from '@ant-design/icons';

import api from '../services/api';
// import { API_URL } from '../config'; // API_URL пока не используется напрямую

// Типы данных для организаций
interface Organization {
  id: number;
  name: string;
  code: string;
  legal_name?: string;
  ckp?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const { Title } = Typography;
const { Option } = Select;

const AdminOrganizationsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [currentItem, setCurrentItem] = useState<Partial<Organization> | null>(null);
  const [organizations, setOrganizations] = useState<Organization[]>([]);

  // Используем Form instance для управления формой в модалке
  const [form] = Form.useForm();

  console.log('🎨 AdminOrganizationsPage: Рендер компонента (Ant Design)');

  // Функция загрузки данных - логика та же, но используем message для ошибок
  const fetchData = async () => {
    if (loading) return;
    console.log('📡 Загружаем данные организаций');
    setLoading(true);
    try {
      const timestamp = new Date().getTime();
      const response = await api.get(`/organizations/?_=${timestamp}`);
      console.log('✅ Данные получены:', response.data);
      setOrganizations(response.data || []);
    } catch (error: any) {
      console.error('❌ Ошибка загрузки:', error);
      message.error('Не удалось загрузить данные: ' + (error.message || 'Неизвестная ошибка'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log('🔄 Первая загрузка данных');
    fetchData();
  }, []);

  // --- Обработчики действий --- 

  const handleCreateItem = () => {
    console.log('🎯 Создание новой записи');
    setCurrentItem({ is_active: true }); // Устанавливаем значения по умолчанию
    form.resetFields(); // Сбрасываем поля формы
    form.setFieldsValue({ is_active: true }); // Устанавливаем значение по умолчанию для Select
    setEditModalOpen(true);
  };

  const handleEditItem = (item: Organization) => {
    console.log('🎯 Редактирование записи:', item);
    setCurrentItem({ ...item });
    form.setFieldsValue({ ...item }); // Заполняем форму текущими значениями
    setEditModalOpen(true);
  };

  // handleDeleteItem теперь будет вызываться из Popconfirm
  const handleDeleteConfirm = async (id: number) => {
    console.log('🗑️ Удаляем запись (ID):', id);
    setLoading(true);
    try {
      await api.delete(`/organizations/${id}`);
      message.success('Запись успешно удалена');
      fetchData(); // Обновляем данные после удаления
    } catch (error: any) {
      console.error('❌ Ошибка удаления:', error);
      message.error('Не удалось удалить запись: ' + (error.message || 'Неизвестная ошибка'));
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    console.log('🎯 Обновление данных');
    fetchData();
  };

  // Сохранение/Обновление (вызывается из формы)
  const handleSaveItem = async (values: Omit<Organization, 'id' | 'created_at' | 'updated_at'>) => {
    setLoading(true);
    console.log('💾 Начинаем сохранение данных', values);
    
    const dataToSend = {
      name: values.name?.trim(),
      code: values.code?.trim(),
      legal_name: values.legal_name?.trim() || null,
      ckp: values.ckp?.trim() || null,
      is_active: Boolean(values.is_active)
    };
    console.log('📦 Данные для отправки:', dataToSend);
    
    try {
      if (currentItem?.id) {
        // Обновление
        console.log('📝 Обновляем запись:', currentItem.id);
        const response = await api.put(`/organizations/${currentItem.id}`, dataToSend);
        console.log('✅ Ответ сервера (обновление):', response);
        message.success('Запись успешно обновлена');
      } else {
        // Создание
        console.log('➕ Создаем новую запись');
        const response = await api.post('/organizations/', dataToSend);
        console.log('✅ Ответ сервера (создание):', response);
        message.success('Запись успешно создана');
      }
      setEditModalOpen(false); // Закрываем модалку
      fetchData(); // Обновляем данные
    } catch (error: any) {
      console.error('❌ Ошибка сохранения:', error);
      if (error.response) {
        console.error('🔍 Детали ошибки:', error.response.data);
        message.error(`Ошибка сервера ${error.response.status}: ${JSON.stringify(error.response.data)}`);
      } else {
        message.error('Ошибка сохранения: ' + (error.message || 'Неизвестная ошибка'));
      }
    } finally {
      setLoading(false);
    }
  };

  // --- Определение колонок для таблицы Ant Design --- 
  const columns: ColumnsType<Organization> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      sorter: (a, b) => a.id - b.id,
      width: 80,
    },
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: 'Юр. название',
      dataIndex: 'legal_name',
      key: 'legal_name',
    },
    {
      title: 'Код',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: 'ЦКП',
      dataIndex: 'ckp',
      key: 'ckp',
      render: (ckp) => ckp || '—',
    },
    {
      title: 'Активна',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (isActive ? 'Да' : 'Нет'),
      filters: [
        { text: 'Да', value: true },
        { text: 'Нет', value: false },
      ],
      onFilter: (value, record) => record.is_active === value,
      width: 100,
    },
    {
      title: 'Действия',
      key: 'actions',
      align: 'center',
      width: 120,
      render: (_, record) => (
        <Space size="small">
          <Button 
            type="primary" 
            icon={<EditOutlined />} 
            onClick={() => handleEditItem(record)}
            size="small"
            style={{ boxShadow: 'none' }}
          />
          <Popconfirm
            title="Удалить запись?"
            description={`Вы уверены, что хотите удалить "${record.name}"?`}
            onConfirm={() => handleDeleteConfirm(record.id)}
            okText="Да"
            cancelText="Нет"
            placement="left"
          >
            <Button 
              danger 
              icon={<DeleteOutlined />} 
              size="small"
              loading={loading && currentItem?.id === record.id} // Показываем спиннер только для удаляемого элемента
              style={{ boxShadow: 'none' }}
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // --- Модальное окно редактирования/создания --- 
  const renderEditModal = () => {
    return (
      <Modal
        title={currentItem?.id ? 'Редактировать организацию' : 'Создать организацию'}
        open={editModalOpen}
        // Обработчик onOk будет вызывать submit формы
        // onOk={() => form.submit()}
        confirmLoading={loading} // Индикатор загрузки на кнопке OK
        onCancel={() => setEditModalOpen(false)} // Закрытие по кнопке Cancel или крестику
        // Кастомный футер для управления кнопками
        footer={[
          <Button 
            key="back" 
            onClick={() => setEditModalOpen(false)} 
            disabled={loading}
            icon={<CloseOutlined />}
          >
            Отмена
          </Button>,
          <Button 
            key="submit" 
            type="primary" 
            loading={loading} 
            onClick={() => form.submit()} // Вызываем сабмит формы по клику
            icon={<SaveOutlined />}
          >
            Сохранить
          </Button>,
        ]}
        width={600}
        maskClosable={!loading} // Запрещаем закрытие кликом по маске во время загрузки
      >
        {/* Обертка Spin для блокировки формы во время загрузки (можно и без нее, т.к. есть confirmLoading) */}
        {/* <Spin spinning={loading}> */}
          <Form 
            form={form} // Передаем form instance
            layout="vertical"
            name="organizationForm"
            onFinish={handleSaveItem} // Обработчик сабмита формы
            // initialValues устанавливаются в handleEditItem/handleCreateItem через form.setFieldsValue/resetFields
          >
            <Form.Item
              name="name"
              label="Название"
              rules={[{ required: true, message: 'Пожалуйста, введите название!' }]}
            >
              <Input placeholder="Название организации" />
            </Form.Item>

            <Form.Item
              name="legal_name"
              label="Юридическое название"
            >
              <Input placeholder="Полное юридическое название" />
            </Form.Item>

            <Form.Item
              name="code"
              label="Код"
              rules={[{ required: true, message: 'Пожалуйста, введите код!' }]}
            >
              <Input placeholder="Уникальный код организации" />
            </Form.Item>

            <Form.Item
              name="ckp"
              label="ЦКП"
            >
              <Input placeholder="Центр коллективного пользования (если есть)" />
            </Form.Item>
            
            {/* Используем Checkbox вместо Select для булева значения */}
            <Form.Item
              name="is_active"
              valuePropName="checked" // Важно для Checkbox
              label="Статус"
            >
              <Checkbox>Активна</Checkbox>
            </Form.Item>
            
          </Form>
        {/* </Spin> */}
      </Modal>
    );
  };

  // --- Рендер компонента --- 
  return (
    // Заменяем Container на div или Card
    <div style={{ padding: '24px' }}> 
      <Title level={3}>Администрирование организаций</Title>
      
      <Space style={{ marginBottom: 16 }}>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleCreateItem}
          loading={loading} // Можно добавить общий спиннер
        >
          Создать
        </Button>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={handleRefresh}
          loading={loading}
        >
          Обновить
        </Button>
      </Space>
      
      {/* Оборачиваем таблицу в Card для визуального сходства с Paper */}
      <Card variant="borderless" style={{ boxShadow: 'none', backgroundColor: '#1A1A20' }}>
        <Table 
          columns={columns} 
          dataSource={organizations} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 10 }} // Пример пагинации
          scroll={{ x: 'max-content' }} // Горизонтальный скролл при необходимости
          style={{ background: 'transparent' }}
          className="clean-table" // Добавляем специальный класс
        />
      </Card>

      {/* Вызываем рендер модального окна */} 
      {renderEditModal()}

      {/* Убираем Snackbar, используем message API */}
      {/* ... Snackbar ... */}
    </div>
  );
};

export default AdminOrganizationsPage; 