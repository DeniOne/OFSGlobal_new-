import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Button,
  Table,
  Space,
  Modal,
  Form,
  Select,
  Spin,
  message,
  Switch,
  Typography,
  Tag // Для отображения типов
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
interface FunctionalRelation {
  id: number;
  source_type: string;
  source_id: number;
  target_type: string;
  target_id: number;
  relation_type: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Division {
  id: number;
  name: string;
}

interface Position {
  id: number;
  name: string;
}

interface Staff {
  id: number;
  first_name: string;
  last_name: string;
  middle_name?: string;
}

// Типы сущностей для Select
type EntityType = 'staff' | 'position' | 'division';

// Типы отношений для Select
const RELATION_TYPES = {
  reports_to: 'Подчиняется',
  manages: 'Руководит',
  collaborates: 'Сотрудничает',
  part_of: 'Часть',
  controls: 'Контролирует'
};

// !!! ВАЖНО: Переименовать компонент вручную в FunctionalRelationsPage !!!
const AdminFunctionalRelationsPage: React.FC = () => {
  const [tableLoading, setTableLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [relations, setRelations] = useState<FunctionalRelation[]>([]);
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [positions, setPositions] = useState<Position[]>([]);
  const [staff, setStaff] = useState<Staff[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<FunctionalRelation | null>(null);

  const [form] = Form.useForm();
  const abortControllerRef = useRef<AbortController | null>(null);

  // Загрузка всех данных
  const fetchData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setTableLoading(true);
    try {
      const [relResponse, divResponse, posResponse, staffResponse] = await Promise.all([
        api.get('/functional-relations/', { signal }),
        api.get('/divisions/', { signal }),
        api.get('/positions/', { signal }),
        api.get('/staff/', { signal })
      ]);
      
      setRelations(relResponse.data);
      setDivisions(divResponse.data);
      setPositions(posResponse.data);
      setStaff(staffResponse.data);

    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('[LOG:FuncRel] Fetch aborted');
        return;
      }
      console.error('[LOG:FuncRel] Ошибка при загрузке данных:', error);
      message.error('Ошибка при загрузке данных для функциональных связей.');
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

  // Получение отображаемого имени для объекта по его типу и ID
  const getItemName = (type: string, id: number): string => {
    switch(type as EntityType) {
      case 'division':
        const division = divisions.find(d => d.id === id);
        return division ? division.name : `Подразделение #${id}`;
      case 'position':
        const position = positions.find(p => p.id === id);
        return position ? position.name : `Должность #${id}`;
      case 'staff':
        const employee = staff.find(s => s.id === id);
        return employee ? `${employee.last_name} ${employee.first_name} ${employee.middle_name || ''}`.trim() : `Сотрудник #${id}`;
      default:
        return `${type}:${id}`;
    }
  };

  // Получение типа отношения
  const getRelationTypeName = (type: string): string => {
    return RELATION_TYPES[type as keyof typeof RELATION_TYPES] || type;
  };

  // Получение цвета тега для типа сущности
  const getEntityTypeColor = (type: string): string => {
      switch(type as EntityType) {
          case 'division': return 'blue';
          case 'position': return 'green';
          case 'staff': return 'purple';
          default: return 'default';
      }
  }
   // Получение цвета тега для типа отношения
  const getRelationTypeColor = (type: string): string => {
      switch(type) {
          case 'reports_to': return 'cyan';
          case 'manages': return 'gold';
          case 'collaborates': return 'lime';
          case 'part_of': return 'geekblue';
          case 'controls': return 'volcano';
          default: return 'default';
      }
  }

  // Открытие модалки для создания
  const handleCreate = () => {
    setEditingItem(null);
    form.resetFields();
    form.setFieldsValue({ 
        is_active: true, 
        source_type: 'staff', // Значения по умолчанию для удобства
        target_type: 'position',
        relation_type: 'reports_to' 
    }); 
    setIsModalVisible(true);
  };

  // Открытие модалки для редактирования
  const handleEdit = (record: FunctionalRelation) => {
    setEditingItem(record);
    form.setFieldsValue(record);
    setIsModalVisible(true);
  };

  // Логика сохранения (будет доработана для динамических Select)
  const handleSave = async () => {
      try {
        const values = await form.validateFields();
        setModalLoading(true);
        
        const dataToSend = { ...values };
        console.log('[LOG:FuncRel] Данные для отправки:', dataToSend);

        if (editingItem) {
            await api.put(`/functional-relations/${editingItem.id}`, dataToSend);
            message.success('Связь успешно обновлена');
        } else {
            await api.post('/functional-relations/', dataToSend);
            message.success('Связь успешно создана');
        }
        setIsModalVisible(false);
        setEditingItem(null);
        fetchData();
        } catch (error: any) {
        console.error('[LOG:FuncRel] Ошибка при сохранении:', error);
        let errorMessage = 'Ошибка при сохранении связи';
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
      content: 'Вы уверены, что хотите удалить эту функциональную связь?',
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          setTableLoading(true);
          await api.delete(`/functional-relations/${id}`);
          message.success('Связь успешно удалена');
          fetchData();
        } catch (error) {
          console.error('[LOG:FuncRel] Ошибка при удалении:', error);
          message.error('Ошибка при удалении связи.');
          setTableLoading(false);
        }
      },
    });
  };

  // Колонки для таблицы
  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', sorter: (a: FunctionalRelation, b: FunctionalRelation) => a.id - b.id },
    {
      title: 'Источник',
      key: 'source',
      render: (_: any, record: FunctionalRelation) => (
          <Space direction="vertical" size="small">
              <Tag color={getEntityTypeColor(record.source_type)}>{record.source_type}</Tag>
              <span>{getItemName(record.source_type, record.source_id)}</span>
          </Space>
      )
    },
    {
      title: 'Отношение',
      dataIndex: 'relation_type',
      key: 'relation',
       render: (type: string) => <Tag color={getRelationTypeColor(type)}>{getRelationTypeName(type)}</Tag>
    },
    {
      title: 'Цель',
      key: 'target',
       render: (_: any, record: FunctionalRelation) => (
          <Space direction="vertical" size="small">
              <Tag color={getEntityTypeColor(record.target_type)}>{record.target_type}</Tag>
              <span>{getItemName(record.target_type, record.target_id)}</span>
          </Space>
      )
    },
    {
      title: 'Активно',
      dataIndex: 'is_active',
      key: 'isActive',
      render: (isActive: boolean) => (isActive ? 'Да' : 'Нет'),
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: any, record: FunctionalRelation) => (
        <Space size="middle">
          <Button icon={<EditOutlined />} onClick={() => handleEdit(record)} />
          <Button icon={<DeleteOutlined />} danger onClick={() => handleDelete(record.id)} />
        </Space>
      ),
    },
  ];

  // Компонент формы внутри модалки
  const RelationForm: React.FC = () => {
    const sourceType = Form.useWatch('source_type', form);
    const targetType = Form.useWatch('target_type', form);

    // Опции для Select источника в зависимости от типа
    const sourceOptions = useCallback(() => {
        switch (sourceType as EntityType) {
            case 'division':
                return divisions.map(d => <Option key={d.id} value={d.id}>{d.name}</Option>);
            case 'position':
                return positions.map(p => <Option key={p.id} value={p.id}>{p.name}</Option>);
            case 'staff':
                return staff.map(s => <Option key={s.id} value={s.id}>{`${s.last_name} ${s.first_name} ${s.middle_name || ''}`.trim()}</Option>);
            default:
                return [];
        }
    }, [sourceType, divisions, positions, staff]);

     // Опции для Select цели в зависимости от типа
    const targetOptions = useCallback(() => {
        switch (targetType as EntityType) {
            case 'division':
                return divisions.map(d => <Option key={d.id} value={d.id}>{d.name}</Option>);
            case 'position':
                return positions.map(p => <Option key={p.id} value={p.id}>{p.name}</Option>);
            case 'staff':
                return staff.map(s => <Option key={s.id} value={s.id}>{`${s.last_name} ${s.first_name} ${s.middle_name || ''}`.trim()}</Option>);
            default:
                return [];
        }
    }, [targetType, divisions, positions, staff]);

    // Сброс ID при смене типа
    useEffect(() => {
        form.setFieldsValue({ source_id: undefined });
    }, [sourceType]);

    useEffect(() => {
        form.setFieldsValue({ target_id: undefined });
    }, [targetType]);


    return (
        <Form form={form} layout="vertical" name="functionalRelationForm">
            <Form.Item
                name="source_type"
                label="Тип источника"
                rules={[{ required: true, message: 'Выберите тип источника' }]}
            >
                <Select placeholder="Выберите тип">
                    <Option value="staff">Сотрудник</Option>
                    <Option value="position">Должность</Option>
                    <Option value="division">Подразделение</Option>
                </Select>
            </Form.Item>
            <Form.Item
                name="source_id"
                label="Источник"
                rules={[{ required: true, message: 'Выберите источник' }]}
                dependencies={['source_type']} // Зависимость для обновления
            >
                <Select placeholder="Выберите источник" loading={tableLoading} allowClear showSearch filterOption={(input, option) => (option?.children as unknown as string ?? '').toLowerCase().includes(input.toLowerCase())}>
                    {sourceOptions()}
                </Select>
            </Form.Item>
            <Form.Item
                name="relation_type"
                label="Тип отношения"
                rules={[{ required: true, message: 'Выберите тип отношения' }]}
            >
                <Select placeholder="Выберите тип">
                    {Object.entries(RELATION_TYPES).map(([key, value]) => (
                        <Option key={key} value={key}>{value}</Option>
                    ))}
                </Select>
            </Form.Item>
             <Form.Item
                name="target_type"
                label="Тип цели"
                rules={[{ required: true, message: 'Выберите тип цели' }]}
            >
                <Select placeholder="Выберите тип">
                    <Option value="staff">Сотрудник</Option>
                    <Option value="position">Должность</Option>
                    <Option value="division">Подразделение</Option>
                </Select>
            </Form.Item>
             <Form.Item
                name="target_id"
                label="Цель"
                rules={[{ required: true, message: 'Выберите цель' }]}
                dependencies={['target_type']} // Зависимость для обновления
            >
                <Select placeholder="Выберите цель" loading={tableLoading} allowClear showSearch filterOption={(input, option) => (option?.children as unknown as string ?? '').toLowerCase().includes(input.toLowerCase())}>
                    {targetOptions()}
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
    );
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Title level={2}>Функциональные связи</Title>
      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
          Добавить связь
        </Button>
        <Button icon={<ReloadOutlined />} onClick={fetchData} loading={tableLoading}>
          Обновить
        </Button>
      </Space>
      
      <Spin spinning={tableLoading}>
          <Table 
              columns={columns} 
              dataSource={relations} 
              rowKey="id" 
              // pagination={{ pageSize: 10 }}
          />
      </Spin>

      {/* Модальное окно */}
      <Modal
        title={editingItem ? 'Редактировать связь' : 'Создать связь'}
        visible={isModalVisible}
        onOk={handleSave} // Теперь handleSave будет работать корректно
        onCancel={() => setIsModalVisible(false)}
        confirmLoading={modalLoading}
        destroyOnClose
        width={700}
      >
        <Spin spinning={modalLoading}>
            {/* Используем компонент формы */} 
            <RelationForm />
        </Spin>
      </Modal>
    </Space>
  );
};

// !!! ВАЖНО: Переименовать компонент вручную в FunctionalRelationsPage !!!
export default AdminFunctionalRelationsPage; 