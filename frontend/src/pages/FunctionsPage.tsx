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
  Switch, // Оставим на всякий случай, вдруг понадобится статус
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

// Тип данных для Функции
interface FunctionItem {
  id: number;
  name: string;
  code: string;
  description?: string;
  division_id?: number; // Привязка к подразделению
  // is_active: boolean; // Пока уберем, если не нужно по API
  created_at: string;
  updated_at: string;
}

// Тип для Подразделения (нужен для Select)
interface Division {
  id: number;
  name: string;
}

// Новый компонент для управления Функциями
const FunctionsPage: React.FC = () => {
  const [tableLoading, setTableLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [functions, setFunctions] = useState<FunctionItem[]>([]);
  const [divisions, setDivisions] = useState<Division[]>([]); // Для Select подразделения
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<FunctionItem | null>(null);

  const [form] = Form.useForm();
  const abortControllerRef = useRef<AbortController | null>(null);

  // Загрузка данных (Функции и Подразделения)
  const fetchData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setTableLoading(true);
    try {
      // !!! Убедиться, что эндпоинты /functions/ и /divisions/ существуют на бэкенде !!!
      const [functionsResponse, divisionsResponse] = await Promise.all([
        api.get('/functions/', { signal }), // Меняем эндпоинт
        api.get('/divisions/', { signal }) // Загружаем подразделения для Select
      ]);
      
      setFunctions(functionsResponse.data);
      setDivisions(divisionsResponse.data);

    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('[LOG:Functions] Fetch aborted');
        return;
      }
      console.error('[LOG:Functions] Ошибка при загрузке данных:', error);
      // Проверяем статус 404 (Not Found) - возможно эндпоинт еще не создан
      if (error.response?.status === 404) {
           message.error('Ошибка: Не удалось загрузить функции (эндпоинт /functions/ не найден). Возможно, он еще не создан на бэкенде.');
      } else {
          message.error('Ошибка при загрузке данных для функций.');
      }
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
    // form.setFieldsValue({ is_active: true }); // Убираем, если нет статуса
    setIsModalVisible(true);
  };

  // Открытие модалки для редактирования
  const handleEdit = (record: FunctionItem) => {
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
       // Убедимся, что division_id отправляется как null, если не выбрано
      if (dataToSend.division_id === undefined || dataToSend.division_id === '') {
          dataToSend.division_id = null;
      }
      console.log('[LOG:Functions] Данные для отправки:', dataToSend);

      if (editingItem) {
        // !!! Убедиться, что PUT /functions/{id} существует
        await api.put(`/functions/${editingItem.id}`, dataToSend);
        message.success('Функция успешно обновлена');
      } else {
         // !!! Убедиться, что POST /functions/ существует
        await api.post('/functions/', dataToSend);
        message.success('Функция успешно создана');
      }
      setIsModalVisible(false);
      setEditingItem(null);
      fetchData();
    } catch (error: any) {
      console.error('[LOG:Functions] Ошибка при сохранении:', error);
      let errorMessage = 'Ошибка при сохранении функции';
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
       // Проверяем статус 404 (Not Found) - возможно эндпоинт еще не создан
       if (error.response?.status === 404) {
           message.error(`Ошибка сохранения: Эндпоинт ${editingItem ? '/functions/{id}':'/functions/'} не найден на бэкенде.`);
       } else {
            message.error(errorMessage);
       }
    } finally {
      setModalLoading(false);
    }
  };

  // Логика удаления
  const handleDelete = (id: number) => {
    Modal.confirm({
      title: 'Подтвердите удаление',
      content: 'Вы уверены, что хотите удалить эту функцию? Это действие нельзя отменить.',
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          setTableLoading(true);
           // !!! Убедиться, что DELETE /functions/{id} существует
          await api.delete(`/functions/${id}`);
          message.success('Функция успешно удалена');
          fetchData();
        } catch (error: any) {
          console.error('[LOG:Functions] Ошибка при удалении:', error);
          let errorMessage = 'Ошибка при удалении функции.';
          // Проверяем статус 404 (Not Found) - возможно эндпоинт еще не создан
         if (error.response?.status === 404) {
             message.error('Ошибка удаления: Эндпоинт /functions/{id} не найден на бэкенде.');
         } else {
              message.error(errorMessage);
         }
          setTableLoading(false);
        }
      },
    });
  };

  // Колонки для таблицы
  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', sorter: (a: FunctionItem, b: FunctionItem) => a.id - b.id },
    { title: 'Название', dataIndex: 'name', key: 'name', sorter: (a: FunctionItem, b: FunctionItem) => a.name.localeCompare(b.name) },
    { title: 'Код', dataIndex: 'code', key: 'code' },
    { title: 'Описание', dataIndex: 'description', key: 'description', render: (desc?: string) => desc || '—' },
    {
      title: 'Подразделение',
      dataIndex: 'division_id',
      key: 'division',
      render: (divisionId?: number) => divisions.find(div => div.id === divisionId)?.name || '—',
      // TODO: Добавить фильтры по подразделению
    },
    // {
    //   title: 'Активно',
    //   dataIndex: 'is_active',
    //   key: 'isActive',
    //   render: (isActive: boolean) => (isActive ? 'Да' : 'Нет'),
    // },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: FunctionItem) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Button icon={<DeleteOutlined />} danger onClick={() => handleDelete(record.id)} />
        </Space>
      ),
    },
  ];

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Title level={2}>Функции</Title> // Меняем заголовок
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Добавить функцию // Меняем текст кнопки
        </Button>
        <Button icon={<ReloadOutlined />} onClick={fetchData} loading={tableLoading}>
          Обновить
        </Button>
      </Space>
      
      <Spin spinning={tableLoading}>
          <Table 
              columns={columns} 
              dataSource={functions} // Меняем источник данных
              rowKey="id" 
              // pagination={{ pageSize: 10 }}
          />
      </Spin>

      {/* Модальное окно */}
      <Modal
        title={editingItem ? 'Редактировать функцию' : 'Создать функцию'} // Меняем заголовок
        visible={isModalVisible}
        onOk={handleSave}
        onCancel={() => setIsModalVisible(false)}
        confirmLoading={modalLoading}
        destroyOnClose
      >
        <Spin spinning={modalLoading}>
          <Form form={form} layout="vertical" name="functionForm">
            <Form.Item
              name="name"
              label="Название"
              rules={[{ required: true, message: 'Пожалуйста, введите название функции' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="code"
              label="Код"
              rules={[{ required: true, message: 'Пожалуйста, введите код функции' }]}
            >
              <Input />
            </Form.Item>
             <Form.Item
              name="description"
              label="Описание"
            >
              <Input.TextArea rows={3} />
            </Form.Item>
            <Form.Item
              name="division_id"
              label="Подразделение" 
              // rules={[{ required: true, message: 'Пожалуйста, выберите подразделение' }]} // Делаем необязательным?
            >
              <Select placeholder="Выберите подразделение" loading={tableLoading} allowClear>
                {divisions.map(div => (
                  <Option key={div.id} value={div.id}>{div.name}</Option>
                ))}
              </Select>
            </Form.Item>
            {/* <Form.Item
              name="is_active"
              label="Активно"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item> */}
          </Form>
        </Spin>
      </Modal>
    </Space>
  );
};

export default FunctionsPage; // Меняем имя экспорта 