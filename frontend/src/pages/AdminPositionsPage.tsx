import React, { useState, useEffect, useCallback, useRef, Key } from 'react';
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
  Popconfirm,
  Tooltip
} from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';
import api from '../services/api';
import { CultNeumorphButton } from '../components/ui/CultNeumorphButton';

const { Title } = Typography;
const { Option } = Select;

// Тип для Enum с бэкенда (можно вынести в отдельный файл)
enum PositionAttribute {
  BOARD = "Совет Учредителей",
  TOP_MANAGEMENT = "Высшее Руководство (Генеральный Директор)",
  DIRECTOR = "Директор Направления",
  DEPARTMENT_HEAD = "Руководитель Департамента",
  SECTION_HEAD = "Руководитель Отдела",
  SPECIALIST = "Специалист"
}

// Интерфейс для Function
interface Function {
  id: number;
  name: string;
  // Добавь другие поля, если они есть и нужны
}

// Интерфейс для Position
interface Position {
  id: number;
  name: string;
  description?: string | null; // Добавлено описание
  // code: string; // Убрано
  attribute: string; // Используем string, т.к. с бэка придет строка
  division_id?: number | null; // Стало необязательным
  section_id?: number | null; // Добавлено необязательное поле
  // parent_id?: number; // Убрано
  is_active: boolean;
  functions: Function[]; // Добавлено поле для связанных функций
  created_at: string;
  updated_at: string;
}

// Интерфейс для Division
interface Division {
  id: number;
  name: string;
}

// Интерфейс для Section
interface Section {
  id: number;
  name: string;
  division_id: number; // Добавим для фильтрации
}

const AdminPositionsPage: React.FC = () => {
  const { message } = App.useApp();
  const [tableLoading, setTableLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [positions, setPositions] = useState<Position[]>([]);
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [sections, setSections] = useState<Section[]>([]); // <<-- ДОБАВЛЕНО состояние для отделов
  const [functions, setFunctions] = useState<Function[]>([]); // <<-- ДОБАВЛЕНО состояние для функций
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
      // Загружаем все 4 сущности параллельно
      const [
        positionsResponse, 
        divisionsResponse, 
        sectionsResponse, // <<-- ДОБАВЛЕНО
        functionsResponse // <<-- ДОБАВЛЕНО
      ] = await Promise.allSettled([
        api.get('/positions/', { signal }), 
        api.get('/divisions/', { signal }),
        api.get('/sections/', { signal }),  // <<-- ДОБАВЛЕНО
        api.get('/functions/', { signal })   // <<-- ДОБАВЛЕНО
      ]);
      
      // Обработка должностей (критично)
      if (positionsResponse.status === 'fulfilled') {
        if (!signal.aborted) setPositions(positionsResponse.value.data);
      } else if (!signal.aborted && positionsResponse.reason?.name !== 'AbortError') {
        console.error("[AdminPositionsPage] Ошибка при загрузке должностей:", positionsResponse.reason);
        message.error('Критическая ошибка: Не удалось загрузить список должностей.');
        setPositions([]);
      }

      // Обработка подразделений (не критично)
      if (divisionsResponse.status === 'fulfilled') {
        if (!signal.aborted) setDivisions(divisionsResponse.value.data);
      } else if (!signal.aborted && divisionsResponse.reason?.name !== 'AbortError') {
        console.warn("[AdminPositionsPage] Ошибка при загрузке подразделений:", divisionsResponse.reason);
        message.warning('Не удалось загрузить список подразделений.');
        setDivisions([]);
      }

      // Обработка отделов (не критично) // <<-- ДОБАВЛЕНО
      if (sectionsResponse.status === 'fulfilled') {
        if (!signal.aborted) setSections(sectionsResponse.value.data);
      } else if (!signal.aborted && sectionsResponse.reason?.name !== 'AbortError') {
        console.warn("[AdminPositionsPage] Ошибка при загрузке отделов:", sectionsResponse.reason);
        message.warning('Не удалось загрузить список отделов.');
        setSections([]);
      }
      
      // Обработка функций (не критично) // <<-- ДОБАВЛЕНО
      if (functionsResponse.status === 'fulfilled') {
        if (!signal.aborted) setFunctions(functionsResponse.value.data);
      } else if (!signal.aborted && functionsResponse.reason?.name !== 'AbortError') {
         console.warn("[AdminPositionsPage] Ошибка при загрузке функций:", functionsResponse.reason);
         message.warning('Не удалось загрузить список функций.');
         setFunctions([]);
      }

    } catch (error: any) {
       if (error.name === 'AbortError') return; 
       console.error("[AdminPositionsPage] Непредвиденная ошибка при загрузке данных:", error);
       message.error('Произошла непредвиденная ошибка при загрузке данных.');
       setPositions([]); setDivisions([]); setSections([]); setFunctions([]); // Сбрасываем все
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
    // Устанавливаем значения по умолчанию
    form.setFieldsValue({ 
        is_active: true, 
        attribute: PositionAttribute.SPECIALIST,
        function_ids: [],
        division_id: null,
        section_id: null
    }); 
    setIsModalVisible(true);
  };

  // Открытие модалки для редактирования
  const handleEdit = (record: Position) => {
    setEditingItem(record);
    // Заполняем форму данными из записи, включая ID функций
    form.setFieldsValue({
        ...record, // Основные поля name, description, is_active, attribute, division_id, section_id
        function_ids: record.functions.map(func => func.id) // Преобразуем массив объектов в массив ID
    });
    setIsModalVisible(true);
  };

  // Логика сохранения
  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setModalLoading(true);
      
      // Формируем данные для отправки, включая attribute и function_ids
      // null для division_id и section_id будет обработан автоматически, если они не выбраны
      const dataToSend = { 
          name: values.name,
          description: values.description || null,
          is_active: values.is_active,
          attribute: values.attribute,
          division_id: values.division_id || null,
          section_id: values.section_id || null,
          function_ids: values.function_ids || []
      };

      if (editingItem) {
        await api.put(`/positions/${editingItem.id}`, dataToSend);
        message.success('Должность успешно обновлена');
      } else {
        await api.post('/positions/', dataToSend);
        message.success('Должность успешно создана');
      }
      setIsModalVisible(false);
      setEditingItem(null);
      fetchData(); // Обновляем данные в таблице
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
        console.error("[AdminPositionsPage] Ошибка сохранения:", error); // Логируем ошибку
        message.error(errorMessage);
    } finally {
      setModalLoading(false);
    }
  };

  // Логика удаления
  const handleDelete = (id: number) => {
    Modal.confirm({
      title: 'Подтвердите удаление',
      content: 'Вы уверены, что хотите удалить эту должность? Убедитесь, что она не используется сотрудниками.',
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          setTableLoading(true);
          await api.delete(`/positions/${id}`);
          message.success('Должность успешно удалена');
          fetchData();
        } catch (error: any) { // <<-- Добавлено error: any
          let errorDetail = 'Ошибка при удалении должности.';
           if (error.response?.data?.detail) {
               errorDetail = error.response.data.detail;
           }
          console.error("[AdminPositionsPage] Ошибка удаления:", error); // Логируем ошибку
          message.error(errorDetail);
          // setTableLoading(false); // fetchData сделает это в finally
        } 
        // finally блок не нужен здесь, fetchData сам управляет tableLoading
      },
    });
  };

  // Колонки для таблицы
  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id', sorter: (a: Position, b: Position) => a.id - b.id, width: 80 },
    { title: 'Название', dataIndex: 'name', key: 'name', sorter: (a: Position, b: Position) => a.name.localeCompare(b.name) },
    { 
      title: 'Атрибут',
      dataIndex: 'attribute', 
      key: 'attribute',
      filters: Object.values(PositionAttribute).map(attr => ({ text: attr, value: attr })),
      onFilter: (value: Key | boolean, record: Position) => record.attribute === value,
    },
    {
      title: 'Подразделение', // Департамент
      dataIndex: 'division_id',
      key: 'division',
      render: (divisionId?: number) => divisions.find(div => div.id === divisionId)?.name || '—',
      filters: divisions.map(div => ({ text: div.name, value: div.id })),
      onFilter: (value: Key | boolean, record: Position) => record.division_id === value,
    },
    {
      title: 'Отдел',
      dataIndex: 'section_id',
      key: 'section',
      render: (sectionId?: number) => sections.find(sec => sec.id === sectionId)?.name || '—',
      filters: sections.map(sec => ({ text: sec.name, value: sec.id })),
      onFilter: (value: Key | boolean, record: Position) => record.section_id === value,
    },
    {
      title: 'Функции',
      dataIndex: 'functions',
      key: 'functions',
      render: (funcs: Function[]) => funcs && funcs.length > 0 
         ? funcs.map(func => func.name).join(', ') 
         : '—',
      // TODO: Добавить фильтр по функциям (сложнее, т.к. массив)
    },
    {
      title: 'Активна',
      dataIndex: 'is_active',
      key: 'isActive',
      render: (isActive: boolean) => (isActive ? 'Да' : 'Нет'),
      filters: [{ text: 'Да', value: true }, { text: 'Нет', value: false }],
      onFilter: (value: Key | boolean, record: Position) => record.is_active === value,
      width: 100,
    },
    {
      title: 'Действия',
      key: 'actions',
      fixed: 'right' as const, // Закрепляем колонку справа
      width: 120, // Фиксируем ширину
      render: (_: any, record: Position) => (
        <Space size="small">
          <Tooltip title="Редактировать">
            <CultNeumorphButton size="small" intent="secondary" onClick={() => handleEdit(record)}>
              <EditOutlined />
            </CultNeumorphButton>
          </Tooltip>
          <Tooltip title="Удалить">
             {/* Оборачиваем кнопку в Popconfirm */}
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
          </Tooltip>
        </Space>
      ),
    },
  ];

  // Отслеживание выбранного division_id для фильтрации отделов
  const selectedDivisionId = Form.useWatch('division_id', form);

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
              label="Название должности"
              rules={[{ required: true, message: 'Пожалуйста, введите название должности!' }]}
            >
              <Input />
            </Form.Item>
             <Form.Item
              name="description"
              label="Описание"
            >
              <Input.TextArea rows={2} />
            </Form.Item>

            {/* <<-- НАЧАЛО НОВЫХ ПОЛЕЙ ФОРМЫ -->> */}
            <Form.Item
              name="attribute"
              label="Атрибут (Уровень доступа/важности)"
              rules={[{ required: true, message: 'Пожалуйста, выберите атрибут!' }]}
            >
              <Select placeholder="Выберите атрибут">
                {Object.entries(PositionAttribute).map(([key, value]) => (
                  <Option key={key} value={value}>{value}</Option>
                ))}
              </Select>
            </Form.Item>
            
            <Form.Item
                name="division_id"
                label={
                    <Space>
                        Подразделение (Департамент)
                        <Tooltip title="Укажите основной департамент. Для должностей уровня 'Директор' и выше рекомендуется оставлять пустым.">
                            <QuestionCircleOutlined style={{ color: 'rgba(0,0,0,.45)' }}/>
                        </Tooltip>
                    </Space>
                }
                rules={[{ required: false }]} // Необязательное поле
            >
                <Select placeholder="Не выбрано" allowClear loading={divisions.length === 0 && tableLoading}>
                    {divisions.map(div => (
                        <Option key={div.id} value={div.id}>{div.name}</Option>
                    ))}
                </Select>
            </Form.Item>

            <Form.Item
                name="section_id"
                label={
                     <Space>
                        Отдел
                        <Tooltip title="Укажите основной отдел. Для должностей уровня 'Рук. Департамента' и выше рекомендуется оставлять пустым.">
                            <QuestionCircleOutlined style={{ color: 'rgba(0,0,0,.45)' }}/>
                        </Tooltip>
                     </Space>
                }
                rules={[{ required: false }]} // Необязательное поле
            >
                <Select 
                    placeholder={!selectedDivisionId ? "Сначала выберите Подразделение" : "Не выбрано"} 
                    allowClear 
                    loading={sections.length === 0 && tableLoading}
                    disabled={!selectedDivisionId} // Блокируем, если не выбрано подразделение
                >
                    {sections
                        .filter(sec => sec.division_id === selectedDivisionId) // Фильтруем отделы по выбранному подразделению
                        .map(sec => (
                            <Option key={sec.id} value={sec.id}>{sec.name}</Option>
                    ))}
                </Select>
            </Form.Item>

             <Form.Item
              name="function_ids"
              label="Функции"
              rules={[{ required: false }]} // Необязательное поле
            >
              <Select
                mode="multiple"
                allowClear
                style={{ width: '100%' }}
                placeholder="Выберите одну или несколько функций"
                loading={functions.length === 0 && tableLoading}
                optionFilterProp="children" // Позволяет искать по названию функции
                filterOption={(input, option) => // Регистронезависимый поиск
                    (option?.children as unknown as string)?.toLowerCase().includes(input.toLowerCase()) ?? false
                 }
              >
                {functions.map(func => (
                  <Option key={func.id} value={func.id}>{func.name}</Option>
                ))}
              </Select>
            </Form.Item>
            {/* <<-- КОНЕЦ НОВЫХ ПОЛЕЙ ФОРМЫ -->> */}

            <Form.Item name="is_active" label="Активна" valuePropName="checked">
              <Switch />
            </Form.Item>
          </Form>
        </Spin>
      </Modal>
    </Space>
  );
};

export default AdminPositionsPage; 