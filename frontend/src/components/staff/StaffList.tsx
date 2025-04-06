import React, { useState, useEffect } from 'react';
import {
  Typography,
  Button,
  Table,
  Input,
  Space,
  Card,
  Alert,
  Tag,
  Spin,
  Empty,
  Tooltip
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  BankOutlined,
  IdcardOutlined,
  PhoneOutlined,
  MailOutlined
} from '@ant-design/icons';
import { Link } from 'react-router-dom';
import api from '../../services/api';
import type { ColumnsType } from 'antd/es/table';

const { Title, Text } = Typography;
const { Search } = Input;

// Типы данных
interface StaffMember {
  id: number;
  name: string;
  position: string;
  division: string;
  organization: {
    id: number;
    name: string;
  };
  is_active: boolean;
  phone?: string;
  email?: string;
}

// Интерфейс для данных с API
interface StaffApiData {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone?: string;
  description?: string;
  is_active: boolean;
  organization_id?: number;
  primary_organization_id?: number;
  created_at: string;
  updated_at: string;
}

interface Organization {
  id: number;
  name: string;
  code: string;
  description?: string;
  org_type: string;
}

// Компонент списка сотрудников
const StaffList: React.FC = () => {
  // Состояния
  const [staffList, setStaffList] = useState<StaffMember[]>([]);
  const [filteredStaff, setFilteredStaff] = useState<StaffMember[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [selectedOrg, setSelectedOrg] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  // Загрузка данных при первом рендере
  useEffect(() => {
    fetchStaff();
    fetchOrganizations();
  }, []);
  
  // Фильтрация сотрудников при изменении параметров фильтрации
  useEffect(() => {
    filterStaff();
  }, [staffList, selectedOrg, searchQuery]);
  
  // Преобразование данных API в формат компонента
  const transformApiData = (apiData: StaffApiData[], orgs: Organization[]): StaffMember[] => {
    return apiData.map(staff => {
      // Находим организацию по ID
      const organization = staff.organization_id 
        ? orgs.find(org => org.id === staff.organization_id) 
        : null;
        
      return {
        id: staff.id,
        name: `${staff.last_name} ${staff.first_name}${staff.middle_name ? ` ${staff.middle_name}` : ''}`,
        position: staff.description || 'Должность не указана',
        division: 'Отдел не указан', // Данных о подразделении нет в API
        organization: organization 
          ? { id: organization.id, name: organization.name }
          : { id: 0, name: 'Не указана' },
        is_active: staff.is_active,
        phone: staff.phone,
        email: staff.email
      };
    });
  };
  
  // Загрузить список сотрудников
  const fetchStaff = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get('/staff/');
      const orgResponse = await api.get('/organizations/');
      
      const staffData = response.data as StaffApiData[];
      const orgsData = orgResponse.data as Organization[];
      
      const transformedData = transformApiData(staffData, orgsData);
      setStaffList(transformedData);
    } catch (err: any) {
      console.error('Ошибка при загрузке данных:', err);
      setError(err.message || 'Ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  };
  
  // Загрузить список организаций для фильтра
  const fetchOrganizations = async () => {
    try {
      const response = await api.get('/organizations/');
      setOrganizations(response.data);
    } catch (err) {
      console.error('Ошибка при загрузке организаций:', err);
    }
  };
  
  // Фильтрация сотрудников по выбранным критериям
  const filterStaff = () => {
    let filtered = [...staffList];
    
    // Фильтр по организации
    if (selectedOrg) {
      filtered = filtered.filter(staff => staff.organization.id === selectedOrg);
    }
    
    // Фильтр по поисковому запросу
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(staff => (
        staff.name.toLowerCase().includes(query) ||
        staff.position.toLowerCase().includes(query) ||
        staff.division.toLowerCase().includes(query) ||
        (staff.email && staff.email.toLowerCase().includes(query)) ||
        (staff.phone && staff.phone.toLowerCase().includes(query))
      ));
    }
    
    setFilteredStaff(filtered);
  };
  
  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
  };
  
  const handleOrgFilter = (orgId: number) => {
    setSelectedOrg(orgId === selectedOrg ? null : orgId);
  };

  // Определение колонок для таблицы
  const columns: ColumnsType<StaffMember> = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 60,
    },
    {
      title: 'ФИО',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Link to={`/staff/${record.id}`}>{text}</Link>
      ),
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: 'Должность',
      dataIndex: 'position',
      key: 'position',
      render: (text) => (
        <Space>
          <IdcardOutlined />
          <span>{text}</span>
        </Space>
      ),
    },
    {
      title: 'Организация',
      dataIndex: ['organization', 'name'],
      key: 'organization',
      render: (text, record) => (
        <Tag color="blue" icon={<BankOutlined />}>
          {record.organization.name}
        </Tag>
      ),
      filters: organizations.map(org => ({ text: org.name, value: org.id })),
      onFilter: (value, record) => record.organization.id === value,
    },
    {
      title: 'Контакты',
      key: 'contacts',
      render: (_, record) => (
        <Space>
          {record.phone && (
            <Tooltip title={record.phone}>
              <Button 
                type="text" 
                size="small" 
                icon={<PhoneOutlined />} 
                onClick={() => window.open(`tel:${record.phone}`)}
              />
            </Tooltip>
          )}
          {record.email && (
            <Tooltip title={record.email}>
              <Button 
                type="text" 
                size="small" 
                icon={<MailOutlined />} 
                onClick={() => window.open(`mailto:${record.email}`)}
              />
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? 'Активен' : 'Неактивен'}
        </Tag>
      ),
      filters: [
        { text: 'Активен', value: true },
        { text: 'Неактивен', value: false },
      ],
      onFilter: (value, record) => record.is_active === value,
    },
  ];
  
  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={4}>Сотрудники</Title>
        
        <Button
          type="primary"
          icon={<PlusOutlined />}
          href="/staff/new"
        >
          Добавить сотрудника
        </Button>
      </div>
      
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Search
            placeholder="Поиск по имени, должности, отделу..."
            allowClear
            enterButton={<SearchOutlined />}
            size="middle"
            onSearch={handleSearchChange}
            style={{ maxWidth: 500 }}
          />
          
          <div>
            <Text style={{ marginRight: 8 }}>Фильтр по организации:</Text>
            <Space wrap>
              {organizations.map(org => (
                <Tag
                  key={org.id}
                  color={selectedOrg === org.id ? 'blue' : undefined}
                  icon={<BankOutlined />}
                  style={{ cursor: 'pointer' }}
                  onClick={() => handleOrgFilter(org.id)}
                >
                  {org.name}
                </Tag>
              ))}
            </Space>
          </div>
        </Space>
      </Card>
      
      {error && (
        <Alert
          message="Ошибка"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      <Card>
        <Spin spinning={loading}>
          {filteredStaff.length === 0 && !loading ? (
            <Empty 
              description={
                staffList.length === 0
                  ? 'Нет данных о сотрудниках. Добавьте первого сотрудника!'
                  : 'Нет сотрудников, соответствующих выбранным фильтрам.'
              }
            />
          ) : (
            <Table
              columns={columns}
              dataSource={filteredStaff.map(staff => ({ ...staff, key: staff.id }))}
              pagination={{ pageSize: 10 }}
              bordered
              size="middle"
              rowKey="id"
            />
          )}
        </Spin>
      </Card>
    </div>
  );
};

export default StaffList; 