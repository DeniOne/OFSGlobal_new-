import React, { useState, useEffect } from 'react';
import {
  Card, Typography, Button, Select, Table, Modal, Form, Input, 
  Tag, Space, Alert, Spin, Empty
} from 'antd';
import {
  PlusOutlined, DeleteOutlined, InfoCircleOutlined
} from '@ant-design/icons';
import { API_URL } from '../../config';

const { Title, Text } = Typography;
const { Option } = Select;

// Типы данных
interface Staff {
  id: number;
  name: string;
  position: string;
}

interface FunctionalRelation {
  id: number;
  manager_id: number;
  subordinate_id: number;
  relation_type: RelationType;
  description: string;
  created_at: string;
  manager?: Staff;
  subordinate?: Staff;
}

enum RelationType {
  FUNCTIONAL = 'functional',
  ADMINISTRATIVE = 'administrative',
  PROJECT = 'project',
  TERRITORIAL = 'territorial',
  MENTORING = 'mentoring'
}

interface FunctionalRelationsManagerProps {
  staffId: number;
  isManager?: boolean; // Если true, то отображаем подчиненных, иначе - руководителей
}

const relationTypeLabels = {
  [RelationType.FUNCTIONAL]: 'Функциональная',
  [RelationType.ADMINISTRATIVE]: 'Административная',
  [RelationType.PROJECT]: 'Проектная',
  [RelationType.TERRITORIAL]: 'Территориальная',
  [RelationType.MENTORING]: 'Менторская'
};

const relationTypeColors = {
  [RelationType.FUNCTIONAL]: '#2196f3',
  [RelationType.ADMINISTRATIVE]: '#f50057',
  [RelationType.PROJECT]: '#4caf50',
  [RelationType.TERRITORIAL]: '#00bcd4',
  [RelationType.MENTORING]: '#ff9800'
};

const FunctionalRelationsManager: React.FC<FunctionalRelationsManagerProps> = ({ 
  staffId, 
  isManager = true 
}) => {
  // Состояния
  const [relations, setRelations] = useState<FunctionalRelation[]>([]);
  const [staff, setStaff] = useState<Staff[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Состояния для создания новой связи
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedStaffId, setSelectedStaffId] = useState<number | ''>('');
  const [selectedRelationType, setSelectedRelationType] = useState<RelationType>(RelationType.FUNCTIONAL);
  const [description, setDescription] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  
  // Загрузка данных
  useEffect(() => {
    fetchRelations();
    fetchAvailableStaff();
  }, [staffId, isManager]);
  
  // Получение списка связей
  const fetchRelations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const endpoint = isManager
        ? `${API_URL}/functional-relations/by-manager/${staffId}`
        : `${API_URL}/functional-relations/by-subordinate/${staffId}`;
      
      const response = await fetch(endpoint);
      
      if (!response.ok) {
        throw new Error('Не удалось загрузить функциональные связи');
      }
      
      const data = await response.json();
      
      // Дополнительно загружаем информацию о сотрудниках
      const enrichedData = await Promise.all(
        data.map(async (relation: FunctionalRelation) => {
          // Загружаем данные руководителя, если мы не на странице руководителя
          if (!isManager) {
            const managerResponse = await fetch(`${API_URL}/staff/${relation.manager_id}`);
            if (managerResponse.ok) {
              const managerData = await managerResponse.json();
              relation.manager = {
                id: managerData.id,
                name: managerData.name,
                position: managerData.position
              };
            }
          }
          
          // Загружаем данные подчиненного, если мы не на странице подчиненного
          if (isManager) {
            const subordinateResponse = await fetch(`${API_URL}/staff/${relation.subordinate_id}`);
            if (subordinateResponse.ok) {
              const subordinateData = await subordinateResponse.json();
              relation.subordinate = {
                id: subordinateData.id,
                name: subordinateData.name,
                position: subordinateData.position
              };
            }
          }
          
          return relation;
        })
      );
      
      setRelations(enrichedData);
    } catch (err: any) {
      setError(err.message || 'Произошла ошибка при загрузке функциональных связей');
      console.error('Ошибка при загрузке функциональных связей:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Получение списка доступных сотрудников для связи
  const fetchAvailableStaff = async () => {
    try {
      // Загружаем список всех сотрудников
      const response = await fetch(`${API_URL}/staff/`);
      
      if (!response.ok) {
        throw new Error('Не удалось загрузить список сотрудников');
      }
      
      const data = await response.json();
      
      // Фильтруем сотрудников - исключаем текущего и тех, с кем уже есть связь
      const filteredStaff = data.filter((s: Staff) => {
        // Исключаем текущего сотрудника
        if (s.id === staffId) return false;
        
        // Исключаем сотрудников, с которыми уже есть связь
        if (isManager) {
          // Если мы создаем подчиненных, исключаем тех, кто уже является подчиненным
          return !relations.some(rel => rel.subordinate_id === s.id);
        } else {
          // Если мы создаем руководителей, исключаем тех, кто уже является руководителем
          return !relations.some(rel => rel.manager_id === s.id);
        }
      });
      
      setStaff(filteredStaff);
    } catch (err: any) {
      console.error('Ошибка при загрузке списка сотрудников:', err);
    }
  };
  
  // Открытие диалога создания связи
  const handleOpenAddDialog = () => {
    setOpenDialog(true);
    setSelectedStaffId('');
    setSelectedRelationType(RelationType.FUNCTIONAL);
    setDescription('');
    setFormError(null);
  };
  
  // Закрытие диалога
  const handleCloseDialog = () => {
    setOpenDialog(false);
  };
  
  // Обработчики изменения полей формы
  const handleStaffChange = (value: number | string) => {
    setSelectedStaffId(value as number);
    if (formError) setFormError(null);
  };
  
  const handleRelationTypeChange = (value: string) => {
    setSelectedRelationType(value as RelationType);
  };
  
  const handleDescriptionChange = (value: string) => {
    setDescription(value);
  };
  
  // Создание новой функциональной связи
  const handleCreateRelation = async () => {
    // Валидация
    if (!selectedStaffId) {
      setFormError('Необходимо выбрать сотрудника');
      return;
    }
    
    try {
      const relationData = {
        manager_id: isManager ? staffId : selectedStaffId,
        subordinate_id: isManager ? selectedStaffId : staffId,
        relation_type: selectedRelationType,
        description
      };
      
      const response = await fetch(`${API_URL}/functional-relations/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(relationData)
      });
      
      if (!response.ok) {
        throw new Error('Не удалось создать функциональную связь');
      }
      
      // Обновляем списки
      fetchRelations();
      fetchAvailableStaff();
      
      // Закрываем диалог
      handleCloseDialog();
    } catch (err: any) {
      setFormError(err.message || 'Ошибка при создании связи');
      console.error('Ошибка при создании функциональной связи:', err);
    }
  };
  
  // Удаление функциональной связи
  const handleDeleteRelation = async (relationId: number) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту функциональную связь?')) {
      return;
    }
    
    try {
      const response = await fetch(`${API_URL}/functional-relations/${relationId}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) {
        throw new Error('Не удалось удалить функциональную связь');
      }
      
      // Обновляем списки
      fetchRelations();
      fetchAvailableStaff();
    } catch (err: any) {
      alert('Ошибка при удалении связи: ' + (err.message || 'Неизвестная ошибка'));
      console.error('Ошибка при удалении функциональной связи:', err);
    }
  };
  
  // Отрисовка компонента
  return (
    <Card style={{ padding: 16, marginBottom: 16 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={5}>
          {isManager ? 'Функциональные подчиненные' : 'Функциональные руководители'}
        </Title>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleOpenAddDialog}
        >
          Добавить {isManager ? 'подчиненного' : 'руководителя'}
        </Button>
      </div>
      
      {error && (
        <Alert 
          message={error} 
          type="error" 
          showIcon 
          style={{ marginBottom: 16 }} 
        />
      )}
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: 20 }}>
          <Spin />
          <div style={{ marginTop: 16 }}>Загрузка данных...</div>
        </div>
      ) : relations.length === 0 ? (
        <Empty
          description={
            <Text>
              {isManager ? 'Функциональных подчиненных нет' : 'Функциональных руководителей нет'}
            </Text>
          }
        />
      ) : (
        <Table
          size="small"
          rowKey="id"
          dataSource={relations}
          columns={[
            {
              title: 'ФИО',
              key: 'name',
              render: (_, record) => isManager 
                ? record.subordinate?.name
                : record.manager?.name
            },
            {
              title: 'Должность',
              key: 'position',
              render: (_, record) => isManager 
                ? record.subordinate?.position
                : record.manager?.position
            },
            {
              title: 'Тип связи',
              key: 'relation_type',
              render: (_, record) => (
                <Tag 
                  color={relationTypeColors[record.relation_type]} 
                >
                  {relationTypeLabels[record.relation_type]}
                </Tag>
              )
            },
            {
              title: 'Описание',
              dataIndex: 'description',
              key: 'description'
            },
            {
              title: 'Действия',
              key: 'actions',
              render: (_, record) => (
                <Button 
                  type="primary"
                  danger
                  size="small"
                  icon={<DeleteOutlined />}
                  onClick={() => handleDeleteRelation(record.id)}
                />
              )
            }
          ]}
        />
      )}
      
      {/* Диалог добавления связи */}
      <Modal
        open={openDialog}
        onCancel={handleCloseDialog}
        onOk={handleCreateRelation}
        title={`Добавить ${isManager ? 'функционального подчиненного' : 'функционального руководителя'}`}
        okText="Создать связь"
        cancelText="Отмена"
        okButtonProps={{ 
          disabled: !selectedStaffId || !selectedRelationType
        }}
      >
        <Form layout="vertical">
          <Form.Item 
            label={isManager ? 'Подчиненный' : 'Руководитель'}
            required
            validateStatus={formError ? 'error' : 'success'}
            help={formError}
          >
            <Select
              value={selectedStaffId}
              onChange={handleStaffChange}
              placeholder={`Выберите ${isManager ? 'подчиненного' : 'руководителя'}`}
              style={{ width: '100%' }}
            >
              {staff.map((member) => (
                <Option key={member.id} value={member.id}>
                  {member.name} - {member.position}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item 
            label="Тип связи"
            required
          >
            <Select
              value={selectedRelationType}
              onChange={handleRelationTypeChange}
              style={{ width: '100%' }}
            >
              {Object.entries(relationTypeLabels).map(([value, label]) => (
                <Option key={value} value={value}>
                  {label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item 
            label="Описание"
          >
            <Input.TextArea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default FunctionalRelationsManager; 