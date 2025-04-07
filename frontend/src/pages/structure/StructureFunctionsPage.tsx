import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Spin,
  Typography,
  Space,
  Button,
  Card,
  Alert,
  Divider,
  Table,
  Tag,
  Input,
  Switch
} from 'antd';
import {
  ReloadOutlined,
  SearchOutlined,
  FilterOutlined
} from '@ant-design/icons';
import api from '../../services/api';
import type { ColumnsType } from 'antd/es/table';
import type { FilterValue, SorterResult } from 'antd/es/table/interface';

const { Title, Text } = Typography;
const { Search } = Input;

// Интерфейс для функций
interface Function {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Интерфейс для связи с секциями
interface SectionFunction {
  id: number;
  section_id: number;
  function_id: number;
  is_primary: boolean;
  created_at: string;
  section_name?: string;
}

const StructureFunctionsPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [functions, setFunctions] = useState<Function[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [includeInactive, setIncludeInactive] = useState(false);
  const [filteredFunctions, setFilteredFunctions] = useState<Function[]>([]);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  // Загрузка данных
  const fetchData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams();
      if (includeInactive) params.append('include_inactive', 'true');
      
      const queryString = params.toString() ? `?${params.toString()}` : '';
      
      const response = await api.get(`/functions/${queryString}`, { signal });
      const data: Function[] = response.data;
      
      setFunctions(data);
      applyFilters(data); // Применяем фильтры к новым данным
      setError(null);
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('[LOG:Functions] Fetch aborted');
        return;
      }
      console.error('[LOG:Functions] Error loading functions:', err);
      setError(err.message || 'Ошибка при загрузке функций');
      setFunctions([]);
      setFilteredFunctions([]);
    } finally {
      if (!signal.aborted) {
        setLoading(false);
        abortControllerRef.current = null;
      }
    }
  }, [includeInactive]);

  // Применяем фильтры к данным
  const applyFilters = useCallback((data: Function[]) => {
    if (!searchTerm) {
      setFilteredFunctions(data);
      return;
    }
    
    const lowercaseSearch = searchTerm.toLowerCase();
    const filtered = data.filter(func => 
      func.name.toLowerCase().includes(lowercaseSearch) ||
      (func.code && func.code.toLowerCase().includes(lowercaseSearch)) ||
      (func.description && func.description.toLowerCase().includes(lowercaseSearch))
    );
    
    setFilteredFunctions(filtered);
  }, [searchTerm]);

  // Загружаем данные при изменении фильтров
  useEffect(() => {
    fetchData();
    
    return () => {
      abortControllerRef.current?.abort();
    };
  }, [fetchData]);

  // Применяем фильтры при изменении данных или поискового запроса
  useEffect(() => {
    applyFilters(functions);
  }, [functions, applyFilters]);

  // Обработчик изменения поискового запроса
  const handleSearch = (value: string) => {
    setSearchTerm(value);
  };

  // Колонки для таблицы
  const columns: ColumnsType<Function> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
      sorter: (a, b) => a.id - b.id
    },
    {
      title: 'Наименование',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name)
    },
    {
      title: 'Код',
      dataIndex: 'code',
      key: 'code',
      width: 120,
      sorter: (a, b) => a.code.localeCompare(b.code)
    },
    {
      title: 'Описание',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => text || '-'
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 120,
      render: (active: boolean) => (
        <Tag color={active ? 'success' : 'default'}>
          {active ? 'Активна' : 'Неактивна'}
        </Tag>
      ),
      filters: [
        { text: 'Активные', value: true },
        { text: 'Неактивные', value: false }
      ],
      onFilter: (value, record) => record.is_active === value
    },
    {
      title: 'Обновлена',
      dataIndex: 'updated_at',
      key: 'updated_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('ru'),
      sorter: (a, b) => new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime()
    }
  ];

  // Обработчик изменения таблицы (сортировка/фильтрация)
  const handleTableChange = (
    pagination: any,
    filters: Record<string, FilterValue | null>,
    sorter: SorterResult<Function> | SorterResult<Function>[]
  ) => {
    // Здесь можно обрабатывать изменения сортировки, если нужно
    console.log('Table params changed:', { pagination, filters, sorter });
  };

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Title level={2}>Функции</Title>
        
        <Card>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space wrap align="center" style={{ marginBottom: 16, justifyContent: 'space-between' }}>
              <Space>
                <Search
                  placeholder="Поиск по названию или коду"
                  onSearch={handleSearch}
                  onChange={(e) => handleSearch(e.target.value)}
                  style={{ width: 300 }}
                  enterButton={<SearchOutlined />}
                />
                
                <Button
                  icon={<FilterOutlined />}
                  onClick={() => setIncludeInactive(!includeInactive)}
                  type={includeInactive ? 'primary' : 'default'}
                >
                  {includeInactive ? 'Скрыть неактивные' : 'Показать все'}
                </Button>
              </Space>
              
              <Button 
                icon={<ReloadOutlined />} 
                onClick={fetchData}
                loading={loading}
              >
                Обновить
              </Button>
            </Space>
            
            {error && (
              <Alert
                message="Ошибка"
                description={error}
                type="error"
                showIcon
                closable
                onClose={() => setError(null)}
                style={{ marginBottom: 16 }}
              />
            )}
            
            <Table<Function>
              columns={columns}
              dataSource={filteredFunctions}
              rowKey="id"
              loading={loading}
              onChange={handleTableChange}
              pagination={{ 
                pageSize: 10,
                showSizeChanger: true,
                pageSizeOptions: ['10', '20', '50'],
                showTotal: (total) => `Всего: ${total} записей`
              }}
            />
            
            <div style={{ marginTop: 16 }}>
              <Text type="secondary">
                * В таблице показаны функции организации. 
                {!includeInactive && ' Неактивные функции скрыты по умолчанию.'}
              </Text>
            </div>
          </Space>
        </Card>
      </Space>
    </div>
  );
};

export default StructureFunctionsPage; 