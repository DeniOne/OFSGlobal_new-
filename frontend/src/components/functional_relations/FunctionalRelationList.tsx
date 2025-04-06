import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  Table,
  Button,
  Space,
  Tag,
  Select,
  Input,
  Modal,
  Form,
  Alert,
  Spin,
  Empty
} from 'antd';
import { 
  PlusOutlined, 
  DeleteOutlined, 
  ReloadOutlined,
  FilterOutlined,
  ApiOutlined
} from '@ant-design/icons';
import { API_URL } from '../../config';
import './FunctionalRelationList.css';

const { Title, Text } = Typography;
const { Option } = Select;

// Интерфейсы данных
interface Organization {
  id: number;
  name: string;
}

interface Staff {
  id: number;
  name: string;
  position: string;
  division: string;
  photo_path?: string;
}

interface FunctionalRelation {
  id: number;
  manager_id: number;
  subordinate_id: number;
  relation_type: string;
  manager_name?: string;
  subordinate_name?: string;
  manager_position?: string;
  subordinate_position?: string;
  manager_department?: string;
  subordinate_department?: string;
}

// Типы функциональных отношений
const relationTypes = [
  { value: 'functional', label: 'Функциональная', color: '#2196f3' },
  { value: 'administrative', label: 'Административная', color: '#4caf50' },
  { value: 'project', label: 'Проектная', color: '#ff9800' },
  { value: 'territorial', label: 'Территориальная', color: '#9c27b0' },
  { value: 'mentoring', label: 'Менторство', color: '#03a9f4' }
];

const FunctionalRelationList: React.FC = () => {
  // Form для модального окна
  const [form] = Form.useForm();
  
  // Состояния для данных
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [staff, setEmployees] = useState<Staff[]>([]);
  const [relations, setRelations] = useState<FunctionalRelation[]>([]);
  
  // Состояния для фильтров
  const [selectedOrganization, setSelectedOrganization] = useState<number | ''>('');
  const [filterManagerId, setFilterManagerId] = useState<number | ''>('');
  const [filterSubordinateId, setFilterSubordinateId] = useState<number | ''>('');
  const [filterRelationType, setFilterRelationType] = useState<string>('');
  
  // Состояния для формы создания связи
  const [isDialogOpen, setIsDialogOpen] = useState<boolean>(false);
  const [newRelationManager, setNewRelationManager] = useState<number | ''>('');
  const [newRelationSubordinate, setNewRelationSubordinate] = useState<number | ''>('');
  const [newRelationType, setNewRelationType] = useState<string>('');
  
  // Состояния загрузки и ошибок
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  // Загрузка организаций при монтировании компонента
  useEffect(() => {
    fetchOrganizations();
  }, []);
  
  // Загрузка сотрудников и связей при изменении выбранной организации
  useEffect(() => {
    if (selectedOrganization) {
      fetchEmployees(Number(selectedOrganization));
      fetchRelations();
    } else {
      setEmployees([]);
      setRelations([]);
    }
  }, [selectedOrganization]);
  
  // Загрузка списка организаций
  const fetchOrganizations = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/organizations/`);
      if (response.ok) {
        const data = await response.json();
        setOrganizations(data);
        
        // Если есть организации, выбираем первую по умолчанию
        if (data.length > 0) {
          setSelectedOrganization(data[0].id);
        }
      } else {
        throw new Error('Не удалось загрузить список организаций');
      }
    } catch (error) {
      setError('Ошибка при загрузке организаций: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };
  
  // Загрузка списка сотрудников
  const fetchEmployees = async (organizationId: number) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/staff/?organization_id=${organizationId}`);
      if (response.ok) {
        const data = await response.json();
        setEmployees(data);
      } else {
        throw new Error('Не удалось загрузить список сотрудников');
      }
    } catch (error) {
      setError('Ошибка при загрузке сотрудников: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };
  
  // Загрузка функциональных связей с фильтрами
  const fetchRelations = async () => {
    if (!selectedOrganization) return;
    
    setLoading(true);
    let url = `${API_URL}/functional-relations/?organization_id=${selectedOrganization}`;
    
    if (filterManagerId) {
      url += `&manager_id=${filterManagerId}`;
    }
    
    if (filterSubordinateId) {
      url += `&subordinate_id=${filterSubordinateId}`;
    }
    
    if (filterRelationType) {
      url += `&relation_type=${filterRelationType}`;
    }
    
    try {
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        
        // Добавляем имена сотрудников к данным о связях
        const enhancedData = data.map((relation: FunctionalRelation) => {
          const manager = staff.find(emp => emp.id === relation.manager_id);
          const subordinate = staff.find(emp => emp.id === relation.subordinate_id);
          
          return {
            ...relation,
            manager_name: manager?.name || 'Неизвестен',
            subordinate_name: subordinate?.name || 'Неизвестен',
            manager_position: manager?.position || 'Неизвестна',
            subordinate_position: subordinate?.position || 'Неизвестна',
            manager_department: manager?.division || 'Неизвестен',
            subordinate_department: subordinate?.division || 'Неизвестен'
          };
        });
        
        setRelations(enhancedData);
      } else {
        throw new Error('Не удалось загрузить функциональные связи');
      }
    } catch (error) {
      setError('Ошибка при загрузке функциональных связей: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };
  
  // Создание новой функциональной связи
  const createRelation = async () => {
    if (!newRelationManager || !newRelationSubordinate || !newRelationType) {
      setError('Все поля обязательны для заполнения');
      return;
    }
    
    if (newRelationManager === newRelationSubordinate) {
      setError('Руководитель и подчиненный не могут быть одним и тем же сотрудником');
      return;
    }
    
    setLoading(true);
    try {
      const payload = {
        manager_id: newRelationManager,
        subordinate_id: newRelationSubordinate,
        relation_type: newRelationType
      };
      
      const response = await fetch(`${API_URL}/functional-relations/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      
      if (response.ok) {
        // Очищаем форму и обновляем список связей
        setNewRelationManager('');
        setNewRelationSubordinate('');
        setNewRelationType('');
        setIsDialogOpen(false);
        fetchRelations();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Не удалось создать связь');
      }
    } catch (error) {
      setError('Ошибка при создании связи: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };
  
  // Удаление функциональной связи
  const deleteRelation = async (relationId: number) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту функциональную связь?')) {
      return;
    }
    
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/functional-relations/${relationId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        // Обновляем список связей
        fetchRelations();
      } else {
        throw new Error('Не удалось удалить связь');
      }
    } catch (error) {
      setError('Ошибка при удалении связи: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };
  
  // Сброс фильтров
  const resetFilters = () => {
    setFilterManagerId('');
    setFilterSubordinateId('');
    setFilterRelationType('');
    fetchRelations();
  };
  
  // Получение цвета чипа по типу связи
  const getRelationColor = (type: string): string => {
    const relationType = relationTypes.find(rt => rt.value === type);
    return relationType ? relationType.color : '#888';
  };
  
  // Получение метки типа связи
  const getRelationLabel = (type: string): string => {
    const relationType = relationTypes.find(rt => rt.value === type);
    return relationType ? relationType.label : type;
  };
  
  return (
    <div className="functional-relation-container">
      <div className="functional-relation-header">
        <Title level={5}>
          Функциональные связи
        </Title>
        
        <Select
          style={{ width: 200 }}
          value={selectedOrganization}
          onChange={(value) => setSelectedOrganization(value)}
        >
          {organizations.map((org) => (
            <Option key={org.id} value={org.id}>{org.name}</Option>
          ))}
        </Select>
      </div>
      
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
        />
      )}
      
      <div className="functional-relation-filter-panel">
        <Title level={5}>
          <FilterOutlined style={{ marginRight: 8 }} />
          Фильтры
        </Title>
        
        <div className="filter-controls">
          <Select
            style={{ width: 200 }}
            value={filterManagerId}
            onChange={(value) => setFilterManagerId(value)}
          >
            <Option value="">Все руководители</Option>
            {staff.map((emp) => (
              <Option key={emp.id} value={emp.id}>{emp.name}</Option>
            ))}
          </Select>
          
          <Select
            style={{ width: 200 }}
            value={filterSubordinateId}
            onChange={(value) => setFilterSubordinateId(value)}
          >
            <Option value="">Все подчиненные</Option>
            {staff.map((emp) => (
              <Option key={emp.id} value={emp.id}>{emp.name}</Option>
            ))}
          </Select>
          
          <Select
            style={{ width: 150 }}
            value={filterRelationType}
            onChange={(value) => setFilterRelationType(value)}
          >
            <Option value="">Все типы</Option>
            {relationTypes.map((type) => (
              <Option key={type.value} value={type.value}>{type.label}</Option>
            ))}
          </Select>
          
          <div className="filter-actions">
            <Button
              type="primary"
              icon={<FilterOutlined />}
              onClick={fetchRelations}
            >
              Применить
            </Button>
            
            <Button
              type="text"
              onClick={resetFilters}
            >
              Сбросить
            </Button>
          </div>
        </div>
      </div>
      
      <div className="functional-relation-actions">
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setIsDialogOpen(true)}
          disabled={loading || !selectedOrganization}
        >
          Добавить связь
        </Button>
        
        <Button
          type="primary"
          icon={<ReloadOutlined />}
          onClick={fetchRelations}
          disabled={loading || !selectedOrganization}
        >
          Обновить
        </Button>
      </div>
      
      <Table
        className="functional-relation-table"
        columns={[
          {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
          },
          {
            title: 'Тип связи',
            dataIndex: 'relation_type',
            key: 'relation_type',
            render: (type) => (
              <Tag
                color={getRelationColor(type)}
              >
                {getRelationLabel(type)}
              </Tag>
            ),
          },
          {
            title: 'Руководитель',
            dataIndex: 'manager_name',
            key: 'manager_name',
          },
          {
            title: 'Должность руководителя',
            dataIndex: 'manager_position',
            key: 'manager_position',
          },
          {
            title: 'Отдел руководителя',
            dataIndex: 'manager_department',
            key: 'manager_department',
          },
          {
            title: 'Подчиненный',
            dataIndex: 'subordinate_name',
            key: 'subordinate_name',
          },
          {
            title: 'Должность подчиненного',
            dataIndex: 'subordinate_position',
            key: 'subordinate_position',
          },
          {
            title: 'Отдел подчиненного',
            dataIndex: 'subordinate_department',
            key: 'subordinate_department',
          },
          {
            title: 'Действия',
            key: 'actions',
            render: (text, record) => (
              <Space>
                <Button
                  type="primary"
                  icon={<DeleteOutlined />}
                  onClick={() => deleteRelation(record.id)}
                >
                  Удалить
                </Button>
              </Space>
            ),
          },
        ]}
        dataSource={relations}
        rowKey="id"
        loading={loading}
        locale={{ emptyText: selectedOrganization ? 'Нет функциональных связей с указанными фильтрами' : 'Выберите организацию' }}
      />
      
      {/* Диалог для создания новой функциональной связи */}
      <Modal
        visible={isDialogOpen}
        onCancel={() => setIsDialogOpen(false)}
        onOk={createRelation}
        confirmLoading={loading}
        title="Новая функциональная связь"
      >
        <Form
          form={form}
          onFinish={(values) => {
            setNewRelationManager(values.manager_id);
            setNewRelationSubordinate(values.subordinate_id);
            setNewRelationType(values.relation_type);
          }}
        >
          <Form.Item
            label="Руководитель"
            name="manager_id"
            rules={[{ required: true, message: 'Пожалуйста, выберите руководителя' }]}
          >
            <Select
              style={{ width: '100%' }}
              value={newRelationManager}
              onChange={(value) => setNewRelationManager(value)}
            >
              {staff.map((emp) => (
                <Option key={emp.id} value={emp.id}>
                  {emp.name} ({emp.position})
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item
            label="Подчиненный"
            name="subordinate_id"
            rules={[{ required: true, message: 'Пожалуйста, выберите подчиненного' }]}
          >
            <Select
              style={{ width: '100%' }}
              value={newRelationSubordinate}
              onChange={(value) => setNewRelationSubordinate(value)}
            >
              {staff
                .filter(emp => emp.id !== newRelationManager) // Исключаем выбранного руководителя
                .map((emp) => (
                  <Option key={emp.id} value={emp.id}>
                    {emp.name} ({emp.position})
                  </Option>
                ))
              }
            </Select>
          </Form.Item>
          
          <Form.Item
            label="Тип связи"
            name="relation_type"
            rules={[{ required: true, message: 'Пожалуйста, выберите тип связи' }]}
          >
            <Select
              style={{ width: '100%' }}
              value={newRelationType}
              onChange={(value) => setNewRelationType(value)}
            >
              {relationTypes.map((type) => (
                <Option key={type.value} value={type.value}>{type.label}</Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default FunctionalRelationList; 