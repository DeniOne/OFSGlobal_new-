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
  App,
  Switch,
  Typography,
  Popconfirm
} from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import api from '../services/api';
import { CultNeumorphButton } from '../components/ui/CultNeumorphButton';

const { Title } = Typography;
const { Option } = Select;

// Типы данных для должностей
interface Position {
  id: number;
  name: string;
  code: string;
  division_id?: number;
  parent_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Типы для связанных данных
interface Division {
  id: number;
  name: string;
}

const AdminPositionsPage: React.FC = () => {
  const { message } = App.useApp();
  const [tableLoading, setTableLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [positions, setPositions] = useState<Position[]>([]);
  const [divisions, setDivisions] = useState<Division[]>([]); // Для Select подразделения
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<Position | null>(null);

  const [form] = Form.useForm();
  const abortControllerRef = useRef<AbortController | null>(null);

  // Загрузка данных (Должности и Подразделения)
  const fetchData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setTableLoading(true);
    message.destroy();
    
    try {
      const [positionsResponse, divisionsResponse] = await Promise.allSettled([
        api.get('/positions/', { signal }), 
        api.get('/divisions/', { signal })  
      ]);
      
      // Обработка должностей (критично)
      if (positionsResponse.status === 'fulfilled') {
        if (!signal.aborted) { 
          setPositions(positionsResponse.value.data);
        }
      } else { // status === 'rejected'
        if (!signal.aborted) { 
          // Проверяем, что причина - не AbortError
          if (positionsResponse.reason && positionsResponse.reason.name !== 'AbortError') {
            console.error("[AdminPositionsPage] Ошибка при загрузке должностей:", positionsResponse.reason); // Добавляем лог
            message.error('Критическая ошибка: Не удалось загрузить список должностей.');
          }
          setPositions([]);
        }
      }

      // Обработка подразделений (не критично)
      if (divisionsResponse.status === 'fulfilled') {
        if (!signal.aborted) { 
          setDivisions(divisionsResponse.value.data);
        }
      } else { // status === 'rejected'
        if (!signal.aborted) { 
           // Проверяем, что причина - не AbortError
           if (divisionsResponse.reason && divisionsResponse.reason.name !== 'AbortError') {
             console.warn("[AdminPositionsPage] Ошибка при загрузке подразделений:", divisionsResponse.reason); // Добавляем лог
             message.warning('Не удалось загрузить список подразделений. Фильтр и отображение могут быть неполными.');
           }
          setDivisions([]);
        }
      }

    } catch (error: any) {
       if (error.name === 'AbortError') {
         return; 
       }
      message.error('Произошла непредвиденная ошибка при загрузке данных.');
      setPositions([]);
      setDivisions([]);
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
  const handleEdit = (record: Position) => {
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
       // Убедимся, что parent_id и division_id отправляются как null, если не выбраны
      if (dataToSend.parent_id === undefined || dataToSend.parent_id === '') {
          dataToSend.parent_id = null;
      }
      if (dataToSend.division_id === undefined || dataToSend.division_id === '') {
          dataToSend.division_id = null;
      }

      if (editingItem) {
        await api.put(`/positions/${editingItem.id}`, dataToSend);
        message.success('Должность успешно обновлена');
      } else {
        await api.post('/positions/', dataToSend);
        message.success('Должность успешно создана');
      }
      setIsModalVisible(false);
      setEditingItem(null);
      fetchData();
    } catch (error: any) {
      let errorMessage = 'Ошибка при сохранении должности';
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
      content: 'Вы уверены, что хотите удалить эту должность? Это может затронуть связанные сущности.',
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          setTableLoading(true);
          await api.delete(`/positions/${id}`);
          message.success('Должность успешно удалена');
          fetchData();
        } catch (error) {
          message.error('Ошибка при удалении должности.');
          setTableLoading(false);
        }
      },
    });
  };

  // Колонки для таблицы
  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', sorter: (a: Position, b: Position) => a.id - b.id },
    { title: 'Название', dataIndex: 'name', key: 'name', sorter: (a: Position, b: Position) => a.name.localeCompare(b.name) },
    { title: 'Код', dataIndex: 'code', key: 'code' },
    {
      title: 'Подразделение',
      dataIndex: 'division_id',
      key: 'division',
      render: (divisionId?: number) => divisions.find(div => div.id === divisionId)?.name || '—',
      // TODO: Добавить фильтры по подразделению
    },
    {
      title: 'Родительская должность',
      dataIndex: 'parent_id',
      key: 'parent',
      render: (parentId?: number) => positions.find(pos => pos.id === parentId)?.name || '—',
       // TODO: Добавить фильтры по родителю
    },
    {
      title: 'Активна',
      dataIndex: 'is_active',
      key: 'isActive',
      render: (isActive: boolean) => (isActive ? 'Да' : 'Нет'),
      // TODO: Добавить фильтры по статусу
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: Position) => (
        <Space size="middle">
          <CultNeumorphButton size="small" intent="secondary" onClick={() => handleEdit(record)}>
            <EditOutlined />
          </CultNeumorphButton>
          <Popconfirm
            title="Удалить должность?"
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

  // Опции для Select родительской должности (исключаем текущую редактируемую)
  const parentPositionOptions = positions
    .filter(pos => !editingItem || pos.id !== editingItem.id)
    .map(pos => (
        <Option key={pos.id} value={pos.id}>{pos.name}</Option>
    ));
    
  // !!! ЛОГ ПЕРЕД РЕНДЕРОМ !!!
  console.log(`[AdminPositionsPage] Rendering table with ${positions.length} positions. First position ID: ${positions[0]?.id}`);

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Title level={2}>Должности</Title>
      <Space style={{ marginBottom: 16 }}>
        <CultNeumorphButton intent="primary" onClick={handleCreate}>
          <PlusOutlined style={{ marginRight: '8px' }} />
          Добавить должность
        </CultNeumorphButton>
        <CultNeumorphButton onClick={fetchData} loading={tableLoading}>
          <ReloadOutlined style={{ marginRight: '8px' }} />
          Обновить
        </CultNeumorphButton>
      </Space>
      
      <Spin spinning={tableLoading}>
          <Table 
              columns={columns} 
              dataSource={positions} // Меняем источник данных
              rowKey="id" 
              // pagination={{ pageSize: 10 }}
          />
      </Spin>

      {/* Модальное окно */}
      <Modal
        title={editingItem ? 'Редактировать должность' : 'Создать должность'}
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={[
            <CultNeumorphButton key="cancel" intent="secondary" onClick={() => setIsModalVisible(false)}>
              Отмена
            </CultNeumorphButton>,
            <CultNeumorphButton key="submit" intent="primary" loading={modalLoading} onClick={handleSave}>
              {editingItem ? 'Сохранить' : 'Создать'}
            </CultNeumorphButton>,
        ]}
      >
        <Spin spinning={modalLoading}>
          <Form form={form} layout="vertical" name="positionForm">
            <Form.Item
              name="name"
              label="Название"
              rules={[{ required: true, message: 'Пожалуйста, введите название должности' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="code"
              label="Код"
              rules={[{ required: true, message: 'Пожалуйста, введите код должности' }]}
            >
              <Input />
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
            <Form.Item
              name="parent_id"
              label="Родительская должность"
            >
              <Select placeholder="Нет родителя" loading={tableLoading} allowClear>
                 {/* <Option value={null}>Нет родителя</Option> */}
                 {parentPositionOptions}
              </Select>
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

export default AdminPositionsPage; 