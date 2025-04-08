import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Table,
  Space,
  Modal,
  Form,
  Input,
  Spin,
  message,
  Alert,
  Switch,
  Typography,
  Card,
  Popconfirm,
  Row,
  Col,
  Select,
  Layout
} from 'antd';
import type { SortOrder } from 'antd/es/table/interface';
import {
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
  ExclamationCircleOutlined,
  PartitionOutlined,
} from '@ant-design/icons';
import api from '../services/api';
import { CultNeumorphButton } from '../components/ui/CultNeumorphButton';
import type { ColumnsType } from 'antd/lib/table';
import type { Division } from '../types/organization';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

// Интерфейс для Отдела (Section)
interface Section {
  id: number;
  name: string;
  division_id: number;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  division_name?: string;
}

const AdminSectionsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [tableLoading, setTableLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [sections, setSections] = useState<Section[]>([]);
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<Section | null>(null);
  const [filterParams, setFilterParams] = useState({
    division_id: null as number | null,
    is_active: true as boolean | null,
  });

  const [form] = Form.useForm();
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchData = useCallback(async () => {
    // Отменяем предыдущие запросы, если они есть
    if (abortControllerRef.current) {
      console.log('[LOG:Sections] Отменяем предыдущие запросы');
      abortControllerRef.current.abort();
    }
    
    // Создаём новый AbortController
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    // Устанавливаем индикатор загрузки
    setTableLoading(true);
    
    // Флаг для отслеживания прерывания операции
    let isCancelled = false;
    
    try {
      console.log('[LOG:Sections] Начинаем загрузку данных...');
      
      // Задержка перед запросом для стабильности
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // 1. Сначала загружаем подразделения (divisions) с повышенной отказоустойчивостью
      let loadedDivisions: Division[] = [];
      try {
        console.log('[LOG:Sections] Отправляем GET запрос на /divisions');
        // Используем timeout в 10 секунд для запроса
        const divisionsResponse = await Promise.race([
          api.get('/divisions', { 
            signal,
            timeout: 10000, // 10 секунд таймаут
          }),
          new Promise<never>((_, reject) => 
            setTimeout(() => reject(new Error('Timeout loading divisions')), 10000)
          )
        ]);
        
        console.log('[LOG:Sections] Получен ответ от /divisions', divisionsResponse?.status);
        
        if (divisionsResponse?.data && Array.isArray(divisionsResponse.data)) {
          loadedDivisions = divisionsResponse.data;
          console.log(`[LOG:Sections] Загружено ${loadedDivisions.length} подразделений.`);
          // Устанавливаем divisions в state только если операция не отменена
          if (!isCancelled && !signal.aborted) {
            setDivisions(loadedDivisions);
          }
        } else {
          console.warn('[LOG:Sections] Получен пустой или некорректный ответ от /divisions');
          // Используем пустой массив вместо ошибки
          setDivisions([]);
        }
      } catch (divError: any) {
        console.error('[LOG:Sections] Ошибка при загрузке подразделений:', divError);
        // Проверяем, не была ли операция преднамеренно отменена
        if (divError.name === 'AbortError' || divError.name === 'CanceledError') {
          console.log('[LOG:Sections] Запрос подразделений был отменен');
        } else if (!isCancelled && !signal.aborted) {
          message.error('Не удалось загрузить список подразделений для формы');
          // Устанавливаем пустой массив в случае ошибки
          setDivisions([]);
        }
      }
      
      // Задержка между запросами для стабильности
      if (!isCancelled && !signal.aborted) {
        await new Promise(resolve => setTimeout(resolve, 300));
      }
      
      // 2. Затем загружаем отделы (sections) с похожей отказоустойчивостью
      let loadedSections: Section[] = [];
      try {
        if (isCancelled || signal.aborted) {
          throw new Error('Operation cancelled before sections request');
        }
        
        console.log('[LOG:Sections] Отправляем GET запрос на /sections с параметрами:', filterParams);
        // Также используем timeout
        const sectionsResponse = await Promise.race([
          api.get('/sections', { 
            signal, 
            params: filterParams,
            timeout: 10000 // 10 секунд таймаут
          }),
          new Promise<never>((_, reject) => 
            setTimeout(() => reject(new Error('Timeout loading sections')), 10000)
          )
        ]);
        
        console.log('[LOG:Sections] Получен ответ от /sections', sectionsResponse?.status);
        
        if (sectionsResponse?.data && Array.isArray(sectionsResponse.data)) {
          loadedSections = sectionsResponse.data;
          console.log(`[LOG:Sections] Загружено ${loadedSections.length} отделов.`);
          
          // Добавляем имена подразделений к отделам
          const sectionsWithDivisionName = loadedSections.map(section => ({
            ...section,
            division_name: loadedDivisions.find(div => div.id === section.division_id)?.name || 'Неизвестно'
          }));
          
          // Устанавливаем обогащенный список отделов в state только если операция не отменена
          if (!isCancelled && !signal.aborted) {
            setSections(sectionsWithDivisionName);
          }
        } else {
          console.warn('[LOG:Sections] Получен пустой или некорректный ответ от /sections');
          // Используем пустой массив вместо ошибки
          if (!isCancelled && !signal.aborted) {
            setSections([]);
          }
        }
      } catch (secError: any) {
        console.error('[LOG:Sections] Ошибка при загрузке отделов:', secError);
        // Проверяем, не была ли операция преднамеренно отменена
        if (secError.name === 'AbortError' || secError.name === 'CanceledError') {
          console.log('[LOG:Sections] Запрос отделов был отменен');
        } else if (!isCancelled && !signal.aborted) {
          message.error('Не удалось загрузить список отделов');
          // Устанавливаем пустой массив в случае ошибки
          setSections([]);
        }
      }

    } catch (error: any) {
      console.error('[LOG:Sections] Общая непредвиденная ошибка:', error);
      if (error.name !== 'AbortError' && error.name !== 'CanceledError' && !isCancelled && !signal.aborted) {
        message.error('Произошла непредвиденная ошибка при загрузке данных');
      }
    } finally {
      // Сбрасываем индикатор загрузки только если операция не была отменена
      if (!isCancelled && !signal.aborted) {
        setTableLoading(false);
        setLoading(false);
      }
    }
    
    // Функция очистки для отслеживания отмены операции внутри колбэка
    return () => {
      isCancelled = true;
    };
  }, [filterParams]);

  useEffect(() => {
    setLoading(true);
    fetchData();
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData]);

  const showModal = (item: Section | null = null) => {
    setEditingItem(item);
    if (item) {
      form.setFieldsValue({
        ...item,
        is_active: item.is_active ?? true,
      });
    } else {
      form.resetFields();
      form.setFieldsValue({ is_active: true });
    }
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingItem(null);
    form.resetFields();
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setModalLoading(true);

      const payload = {
        ...values,
        is_active: values.is_active ?? true,
      };

      // ***** ДИАГНОСТИЧЕСКИЙ ЛОГ *****
      console.log('[LOG:Sections DEBUG] Данные для отправки (payload):', payload);
      console.log('[LOG:Sections DEBUG] Тип division_id:', typeof payload.division_id);
      // ***** КОНЕЦ ДИАГНОСТИКИ *****

      console.log(`[LOG:Sections] Сохранение отдела: ${editingItem ? 'обновление ID '+editingItem.id : 'создание'}`, payload);

      if (editingItem) {
        await api.put(`/sections/${editingItem.id}`, payload);
        message.success('Отдел успешно обновлен');
      } else {
        await api.post('/sections/', payload);
        message.success('Отдел успешно создан');
      }
      setIsModalVisible(false);
      setEditingItem(null);
      form.resetFields();
      fetchData();
    } catch (error: any) {
      console.error('[LOG:Sections] Ошибка при сохранении отдела:', error);
      let errorMessage = 'Ошибка при сохранении отдела';

      // Улучшенная обработка ошибок FastAPI
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'string') {
            errorMessage = detail;
        } else if (Array.isArray(detail)) {
            // Форматируем ошибки валидации Pydantic
            errorMessage = detail.map((e: any) => {
                const field = e.loc && e.loc.length > 1 ? e.loc[1] : (e.loc ? e.loc[0] : 'field');
                return `${field}: ${e.msg}`;
            }).join('; ');
        } else if (typeof detail === 'object' && detail !== null && detail.msg) {
             // Обрабатываем другой возможный формат {loc: ..., msg: ..., type: ...}
             const field = detail.loc && detail.loc.length > 1 ? detail.loc[1] : (detail.loc ? detail.loc[0] : 'field');
             errorMessage = `${field}: ${detail.msg}`;
        } else {
            // Если формат неизвестен, просто выводим JSON
            errorMessage = JSON.stringify(detail);
        }
      }
       // Добавляем статус ответа, если он есть
       if (error.response?.status) {
         errorMessage = `Ошибка ${error.response.status}: ${errorMessage}`;
       }

      message.error(errorMessage);
    } finally {
      setModalLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      setTableLoading(true);
      console.log(`[LOG:Sections] Удаление (деактивация) отдела ID: ${id}`);
      await api.delete(`/sections/${id}`);
      message.success('Отдел успешно деактивирован');
      fetchData();
    } catch (error: any) {
      console.error(`[LOG:Sections] Ошибка при удалении отдела ID: ${id}`, error);
      let errorMessage = 'Ошибка при удалении отдела';
      if (error.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string' ? error.response.data.detail : JSON.stringify(error.response.data.detail);
      }
      message.error(errorMessage);
      setTableLoading(false);
    }
  };

  const handleFilterChange = (key: keyof typeof filterParams, value: any) => {
    console.log(`[LOG:Sections] Изменение фильтра: ${key} = ${value}`);
    setFilterParams(prev => ({
      ...prev,
      [key]: value === undefined ? null : value,
    }));
  };

  const resetFilters = () => {
    console.log('[LOG:Sections] Сброс фильтров');
    setFilterParams({
      division_id: null,
      is_active: true,
    });
  };

  const columns: ColumnsType<Section> = [
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
      title: 'Подразделение',
      dataIndex: 'division_name',
      key: 'division_name',
      sorter: (a, b) => (a.division_name || '').localeCompare(b.division_name || ''),
      filterDropdown: (
        <div style={{ padding: 8 }}>
          <Select<number | null>
            showSearch
            allowClear
            placeholder="Фильтр по подразделению"
            optionFilterProp="children"
            value={filterParams.division_id}
            onChange={(value) => handleFilterChange('division_id', value)}
            style={{ width: 200 }}
            filterOption={(input, option) =>
              option?.children?.toString().toLowerCase().includes(input.toLowerCase()) ?? false
            }
          >
            {divisions.map(div => (
              <Option key={div.id} value={div.id}>{div.name}</Option>
            ))}
          </Select>
        </div>
      ),
      filterIcon: (filtered: boolean) => <PartitionOutlined style={{ color: filtered ? '#1890ff' : undefined }} />,
      onFilter: () => true,
    },
    {
      title: 'Описание',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: 'Активен',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (isActive ? 'Да' : 'Нет'),
      width: 100,
      filterDropdown: (
        <div style={{ padding: 8 }}>
          <Select<boolean | null>
            allowClear
            placeholder="Все"
            value={filterParams.is_active}
            onChange={(value) => handleFilterChange('is_active', value)}
            style={{ width: 100 }}
          >
            <Option value={true}>Да</Option>
            <Option value={false}>Нет</Option>
          </Select>
        </div>
      ),
      filterIcon: (filtered: boolean) => <PartitionOutlined style={{ color: filtered ? '#1890ff' : undefined }} />,
      onFilter: () => true,
    },
    {
      title: 'Действия',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space size="middle">
          <CultNeumorphButton
            onClick={() => showModal(record)}
            intent="primary"
          >
            <EditOutlined />
          </CultNeumorphButton>
          <Popconfirm
            title="Деактивировать отдел?"
            description="Вы уверены, что хотите деактивировать этот отдел?"
            onConfirm={() => handleDelete(record.id)}
            okText="Да"
            cancelText="Нет"
            placement="topRight"
            icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
          >
            <CultNeumorphButton
              intent="danger"
            >
              <DeleteOutlined />
            </CultNeumorphButton>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Layout style={{ padding: '24px', background: 'var(--background-color)' }}>
      <Card
        bordered={false}
        style={{
          background: 'var(--card-background-color)',
          borderRadius: '16px',
          boxShadow: 'var(--card-shadow)',
        }}
      >
        <Row justify="space-between" align="middle" style={{ marginBottom: 16 }}>
          <Col>
            <Title level={3} style={{ color: 'var(--text-color-primary)', margin: 0 }}>Отделы</Title>
          </Col>
          <Col>
            <Space>
              <CultNeumorphButton
                intent="primary"
                onClick={() => showModal()}
              >
                <PlusOutlined /> Добавить отдел
              </CultNeumorphButton>
              <CultNeumorphButton
                onClick={fetchData}
                loading={tableLoading}
              >
                <ReloadOutlined /> Обновить
              </CultNeumorphButton>
              <CultNeumorphButton
                onClick={resetFilters}
              >
                Сбросить фильтры
              </CultNeumorphButton>
            </Space>
          </Col>
        </Row>

        {loading && !tableLoading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
          </div>
        ) : (
          <Table<Section>
            columns={columns}
            dataSource={sections}
            rowKey="id"
            loading={tableLoading}
            pagination={{
              pageSize: 15,
              showSizeChanger: true,
              pageSizeOptions: ['15', '30', '50', '100'],
              showTotal: (total, range) => `${range[0]}-${range[1]} из ${total} отделов`,
            }}
            scroll={{ x: 'max-content' }}
            style={{ background: 'transparent' }}
          />
        )}
      </Card>

      <Modal
        title={editingItem ? "Редактировать отдел" : "Создать отдел"}
        open={isModalVisible}
        onCancel={handleCancel}
        destroyOnClose
        footer={[
          <CultNeumorphButton key="cancel" onClick={handleCancel}>
            Отмена
          </CultNeumorphButton>,
          <CultNeumorphButton
            key="save"
            intent="primary"
            loading={modalLoading}
            onClick={handleSave}
          >
            {editingItem ? "Сохранить" : "Создать"}
          </CultNeumorphButton>,
        ]}
      >
        <Spin spinning={modalLoading}>
          <Form form={form} layout="vertical" name="section_form">
            <Form.Item
              name="name"
              label="Название"
              rules={[{ required: true, message: 'Пожалуйста, введите название отдела!' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="division_id"
              label="Подразделение (Департамент)"
              rules={[{ required: true, message: 'Пожалуйста, выберите подразделение!' }]}
            >
              <Select
                showSearch
                placeholder="Выберите подразделение"
                optionFilterProp="children"
                filterOption={(input, option) =>
                  option?.children?.toString().toLowerCase().includes(input.toLowerCase()) ?? false
                }
                loading={divisions.length === 0}
              >
                {divisions.map(div => (
                  <Option key={div.id} value={div.id}>{div.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item name="description" label="Описание">
              <TextArea rows={3} />
            </Form.Item>
            <Form.Item name="is_active" label="Активен" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Form>
        </Spin>
      </Modal>
    </Layout>
  );
};

export default AdminSectionsPage; 