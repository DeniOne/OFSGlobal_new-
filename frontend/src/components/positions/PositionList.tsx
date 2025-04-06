import React, { useState, useEffect } from 'react';
import {
  Typography,
  Button,
  Space,
  Select,
  Input,
  Table,
  Tag,
  Alert,
  Spin,
  Collapse,
  Card,
  Tooltip,
  Switch,
  Divider,
  Modal
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FilterOutlined,
  SearchOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { Key } from 'react';
import { Position, Organization } from '../../types/organization';
import PositionEditModal from './PositionEditModal';
import api from '../../services/api';

const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;
const { Panel } = Collapse;

// Расширяем интерфейс Position для добавления поля, которое используется, но не определено в типах
interface ExtendedPosition extends Position {
  organization_id?: number;
}

const PositionList: React.FC = () => {
  // Состояния данных
  const [positions, setPositions] = useState<ExtendedPosition[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  
  // Состояния UI
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrg, setSelectedOrg] = useState<number | ''>('');
  const [selectedPosition, setSelectedPosition] = useState<ExtendedPosition | null>(null);
  const [openCreate, setOpenCreate] = useState(false);
  const [openEdit, setOpenEdit] = useState(false);
  const [openFilters, setOpenFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [includeInactive, setIncludeInactive] = useState(false);
  
  // Первоначальная загрузка данных
  useEffect(() => {
    fetchOrganizations();
  }, []);
  
  // Загрузка должностей при изменении выбранной организации
  useEffect(() => {
    if (selectedOrg) {
      fetchPositions();
    } else {
      setPositions([]);
    }
  }, [selectedOrg, includeInactive]);
  
  // Загрузка списка организаций
  const fetchOrganizations = async () => {
    setLoading(true);
    try {
      const response = await api.get('/organizations/');
      setOrganizations(response.data);
      
      // Если есть организации, выбираем первую по умолчанию
      if (response.data.length > 0) {
        setSelectedOrg(response.data[0].id);
      }
    } catch (err: any) {
      setError(err.message || 'Ошибка при загрузке организаций');
    } finally {
      setLoading(false);
    }
  };
  
  // Загрузка списка должностей
  const fetchPositions = async () => {
    if (!selectedOrg) return;
    
    setLoading(true);
    try {
      let url = `/positions/?organization_id=${selectedOrg}&include_inactive=${includeInactive}`;
      
      const response = await api.get(url);
      setPositions(response.data);
    } catch (err: any) {
      setError(err.message || 'Ошибка при загрузке должностей');
    } finally {
      setLoading(false);
    }
  };
  
  // Создание или обновление должности
  const handleSavePosition = (position: ExtendedPosition) => {
    fetchPositions();
  };
  
  // Удаление должности
  const handleDeletePosition = async (positionId: number) => {
    try {
      await api.delete(`/positions/${positionId}`);
      fetchPositions();
    } catch (err: any) {
      setError(err.message || 'Ошибка при удалении должности');
    }
  };
  
  // Сброс формы
  const resetForm = () => {
    setSelectedPosition(null);
  };
  
  // Обработчик редактирования
  const handleEdit = (position: ExtendedPosition) => {
    setSelectedPosition(position);
    setOpenEdit(true);
  };
  
  // Фильтрация должностей по поисковому запросу
  const filteredPositions = positions.filter(position => {
    if (!searchTerm) return true;
    return position.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
           (position.code && position.code.toLowerCase().includes(searchTerm.toLowerCase()));
  });
  
  // Колонки для таблицы
  const columns: ColumnsType<ExtendedPosition> = [
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: ExtendedPosition, b: ExtendedPosition) => a.name.localeCompare(b.name)
    },
    {
      title: 'Код',
      dataIndex: 'code',
      key: 'code',
      render: (code: string) => code || '-'
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'status',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? 'Активная' : 'Неактивная'}
        </Tag>
      ),
      filters: [
        { text: 'Активные', value: true },
        { text: 'Неактивные', value: false }
      ],
      // Используем более безопасную форму функции фильтрации
      onFilter: (value: boolean | Key, record: ExtendedPosition) => {
        if (typeof value === 'boolean') {
          return record.is_active === value;
        }
        return record.is_active === (value.toString() === 'true');
      }
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_: unknown, record: ExtendedPosition) => (
        <Space>
          <Button
            type="primary"
            icon={<EditOutlined />}
            size="small"
            onClick={() => handleEdit(record)}
          />
          <Button
            type="primary"
            danger
            icon={<DeleteOutlined />}
            size="small"
            onClick={() => {
              Modal.confirm({
                title: 'Подтвердите удаление',
                content: 'Вы уверены, что хотите удалить эту должность?',
                okText: 'Удалить',
                okType: 'danger',
                cancelText: 'Отмена',
                onOk: () => handleDeletePosition(record.id)
              });
            }}
          />
        </Space>
      )
    }
  ];
  
  return (
    <div style={{ padding: 24 }}>
      {error && (
        <Alert
          message="Ошибка"
          description={error}
          type="error"
          closable
          style={{ marginBottom: 16 }}
          onClose={() => setError(null)}
        />
      )}
      
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={4}>Должности</Title>
        
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchPositions}
            loading={loading}
          >
            Обновить
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              resetForm();
              setOpenCreate(true);
            }}
            disabled={!selectedOrg}
          >
            Добавить должность
          </Button>
        </Space>
      </div>
      
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
            <div style={{ minWidth: 200 }}>
              <Text strong>Организация:</Text>
              <Select
                style={{ width: '100%', marginTop: 4 }}
                value={selectedOrg}
                onChange={(value) => setSelectedOrg(value)}
                loading={loading}
                disabled={loading}
              >
                {organizations.map(org => (
                  <Option key={org.id} value={org.id}>{org.name}</Option>
                ))}
              </Select>
            </div>
            
            <div style={{ flex: 1, minWidth: 200 }}>
              <Search
                placeholder="Поиск по названию или коду"
                allowClear
                onSearch={setSearchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{ width: '100%' }}
              />
            </div>
            
            <Button
              icon={<FilterOutlined />}
              onClick={() => setOpenFilters(!openFilters)}
              type={openFilters ? 'primary' : 'default'}
            >
              Фильтры
            </Button>
          </div>
          
          <Collapse ghost activeKey={openFilters ? ['1'] : undefined} style={{ marginTop: 8 }}>
            <Panel header="Дополнительные фильтры" key="1">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <Switch
                    checked={includeInactive}
                    onChange={(checked) => setIncludeInactive(checked)}
                  />
                  <Text style={{ marginLeft: 8 }}>Включать неактивные должности</Text>
                </div>
              </Space>
            </Panel>
          </Collapse>
        </Space>
      </Card>
      
      <Card>
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={filteredPositions}
            rowKey="id"
            pagination={{ pageSize: 10 }}
            size="middle"
            bordered
          />
        </Spin>
      </Card>
      
      {/* Модальные окна для создания/редактирования */}
      {openCreate && (
        <PositionEditModal
          open={openCreate}
          position={null}
          organizationId={Number(selectedOrg)}
          onClose={() => setOpenCreate(false)}
          onSave={handleSavePosition}
        />
      )}
      
      {openEdit && selectedPosition && (
        <PositionEditModal
          open={openEdit}
          position={selectedPosition}
          organizationId={selectedPosition.organization_id || Number(selectedOrg)}
          onClose={() => setOpenEdit(false)}
          onSave={handleSavePosition}
        />
      )}
    </div>
  );
};

export default PositionList; 