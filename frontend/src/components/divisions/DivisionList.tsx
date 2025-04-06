import React, { useState, useEffect } from 'react';
import {
  Typography,
  Button,
  Table,
  Space,
  Select,
  Tag,
  Alert,
  Spin,
  Input,
  Collapse,
  Tooltip,
  Switch,
  Card,
  Divider,
  List,
  Tree,
  Modal,
  message
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FilterOutlined,
  SearchOutlined,
  ApartmentOutlined,
  CaretDownOutlined,
  CaretRightOutlined
} from '@ant-design/icons';
import type { TreeDataNode } from 'antd';
import { Division, Organization } from '../../types/organization';
import DivisionEditModal from './DivisionEditModal';
import api from '../../services/api';
import { useNavigate } from 'react-router-dom';

const { Title, Text } = Typography;
const { Option } = Select;
const { Search } = Input;
const { Panel } = Collapse;

const DivisionList: React.FC = () => {
  // Состояния данных
  const [divisions, setDivisions] = useState<Division[]>([]);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [treeData, setTreeData] = useState<Division[]>([]);
  
  // Состояния UI
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedOrg, setSelectedOrg] = useState<number | ''>('');
  const [selectedDivision, setSelectedDivision] = useState<Division | null>(null);
  const [openCreate, setOpenCreate] = useState(false);
  const [openEdit, setOpenEdit] = useState(false);
  const [openFilters, setOpenFilters] = useState(false);
  const [showTree, setShowTree] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [parentDivision, setParentDivision] = useState<number | null>(null);
  const [includeInactive, setIncludeInactive] = useState(false);
  const [formData, setFormData] = useState<Division>({
    id: 0,
    name: '',
    code: '',
    description: '',
    is_active: true,
    level: 0,
    organization_id: 0,
    parent_id: null
  });
  const [editId, setEditId] = useState<number | null>(null);
  const navigate = useNavigate();
  
  // Первоначальная загрузка данных
  useEffect(() => {
    fetchOrganizations();
  }, []);
  
  // Загрузка отделов при изменении выбранной организации
  useEffect(() => {
    if (selectedOrg) {
      fetchDivisions();
      if (showTree) {
        fetchDivisionTree();
      }
    } else {
      setDivisions([]);
      setTreeData([]);
    }
  }, [selectedOrg, parentDivision, includeInactive]);
  
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
      message.error('Не удалось загрузить организации');
    } finally {
      setLoading(false);
    }
  };
  
  // Загрузка списка отделов
  const fetchDivisions = async () => {
    if (!selectedOrg) return;
    
    setLoading(true);
    try {
      let url = `/divisions/?organization_id=${selectedOrg}&include_inactive=${includeInactive}`;
      
      // Добавляем фильтры
      if (parentDivision !== null) {
        url += `&parent_id=${parentDivision}`;
      } else {
        url += '&parent_id=null';
      }
      
      const response = await api.get(url);
      setDivisions(response.data);
    } catch (err: any) {
      setError(err.message || 'Ошибка при загрузке отделов');
      message.error('Не удалось загрузить список отделов');
    } finally {
      setLoading(false);
    }
  };
  
  // Загрузка дерева отделов
  const fetchDivisionTree = async () => {
    if (!selectedOrg) return;
    
    setLoading(true);
    try {
      const response = await api.get(`/divisions/tree?organization_id=${selectedOrg}&include_inactive=${includeInactive}`);
      setTreeData(response.data);
    } catch (err: any) {
      setError(err.message || 'Ошибка при загрузке дерева отделов');
      message.error('Не удалось загрузить дерево отделов');
    } finally {
      setLoading(false);
    }
  };
  
  // Создание или обновление отдела
  const handleSaveDivision = (division: Division) => {
    fetchDivisions();
    if (showTree) {
      fetchDivisionTree();
    }
  };
  
  // Удаление отдела
  const handleDeleteDivision = async (divisionId: number) => {
    Modal.confirm({
      title: 'Подтвердите удаление',
      content: 'Вы уверены, что хотите удалить этот отдел?',
      okText: 'Да, удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      onOk: async () => {
        try {
          await api.delete(`/divisions/${divisionId}`);
          message.success('Отдел успешно удален');
          
          // Обновляем список отделов
          fetchDivisions();
          if (showTree) {
            fetchDivisionTree();
          }
        } catch (err: any) {
          setError(err.message || 'Ошибка при удалении отдела');
          message.error('Не удалось удалить отдел');
        }
      }
    });
  };
  
  // Переключение между табличным и древовидным представлением
  const handleToggleShowTree = () => {
    const newShowTree = !showTree;
    setShowTree(newShowTree);
    
    if (newShowTree && selectedOrg) {
      fetchDivisionTree();
    }
  };
  
  // Сброс формы
  const resetForm = () => {
    setSelectedDivision(null);
    setFormData({
      id: 0,
      name: '',
      code: '',
      description: '',
      is_active: true,
      level: 0,
      organization_id: Number(selectedOrg) || 0,
      parent_id: null
    });
    setEditId(null);
  };
  
  // Преобразование данных для дерева Ant Design
  const convertToTreeData = (data: Division[]): TreeDataNode[] => {
    return data.map(item => ({
      key: item.id.toString(),
      title: (
        <Space>
          <span>{item.name} {item.code && `(${item.code})`}</span>
          {!item.is_active && <Tag color="default">Неактивный</Tag>}
          <Space size="small">
            <Button 
              type="text" 
              size="small" 
              icon={<EditOutlined />} 
              onClick={(e) => {
                e.stopPropagation();
                handleEditClick(item);
              }}
            />
            <Button 
              type="text" 
              size="small" 
              danger
              icon={<DeleteOutlined />} 
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteDivision(item.id);
              }}
            />
          </Space>
        </Space>
      ),
      isLeaf: !item.children || item.children.length === 0,
      children: item.children ? convertToTreeData(item.children) : undefined
    }));
  };
  
  // Обработчики формы
  const handleOrganizationChange = (value: number) => {
    setSelectedOrg(value);
    setParentDivision(null);
  };
  
  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
  };
  
  const handleCreateDivision = () => {
    resetForm();
    setOpenCreate(true);
  };
  
  const handleEditClick = (division: Division) => {
    setSelectedDivision(division);
    setFormData({
      ...division
    });
    setEditId(division.id);
    setOpenEdit(true);
  };
  
  // Фильтрованные данные для таблицы
  const filteredDivisions = divisions.filter(div => 
    div.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    div.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (div.description && div.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );
  
  // Колонки таблицы
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 70,
    },
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: Division, b: Division) => a.name.localeCompare(b.name),
    },
    {
      title: 'Код',
      dataIndex: 'code',
      key: 'code',
      width: 120,
    },
    {
      title: 'Описание',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => text || '-',
    },
    {
      title: 'Статус',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'success' : 'default'}>
          {isActive ? 'Активный' : 'Неактивный'}
        </Tag>
      ),
      filters: [
        { text: 'Активные', value: true },
        { text: 'Неактивные', value: false },
      ],
      onFilter: (value: boolean, record: Division) => record.is_active === value,
    },
    {
      title: 'Действия',
      key: 'actions',
      width: 150,
      render: (_: any, record: Division) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditClick(record)}
          />
          <Button
            type="primary"
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteDivision(record.id)}
          />
        </Space>
      ),
    },
  ];
  
  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={4}>Подразделения</Title>
        
        <Space>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => {
              fetchDivisions();
              if (showTree) fetchDivisionTree();
            }}
          >
            Обновить
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreateDivision}
          >
            Создать подразделение
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
                onChange={handleOrganizationChange}
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
                onSearch={handleSearchChange}
                style={{ width: '100%' }}
              />
            </div>
            
            <div>
              <Switch
                checked={showTree}
                onChange={handleToggleShowTree}
              />
              <Text style={{ marginLeft: 8 }}>Древовидная структура</Text>
            </div>
          </div>
          
          <Collapse ghost style={{ marginTop: 8 }}>
            <Panel header="Дополнительные фильтры" key="1">
              <Space direction="vertical" style={{ width: '100%' }}>
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <Switch
                    checked={includeInactive}
                    onChange={(checked) => setIncludeInactive(checked)}
                  />
                  <Text style={{ marginLeft: 8 }}>Включать неактивные подразделения</Text>
                </div>
                
                <div>
                  <Text>Родительское подразделение:</Text>
                  <Select
                    style={{ width: '100%', marginTop: 4 }}
                    value={parentDivision}
                    onChange={(value) => setParentDivision(value)}
                    allowClear
                    placeholder="Все подразделения"
                  >
                    <Option value={null}>Корневые подразделения</Option>
                    {divisions.map(div => (
                      <Option key={div.id} value={div.id}>{div.name}</Option>
                    ))}
                  </Select>
                </div>
              </Space>
            </Panel>
          </Collapse>
        </Space>
      </Card>
      
      {error && (
        <Alert
          type="error"
          message="Ошибка"
          description={error}
          closable
          style={{ marginBottom: 16 }}
          onClose={() => setError(null)}
        />
      )}
      
      <Card>
        <Spin spinning={loading}>
          {showTree ? (
            treeData.length > 0 ? (
              <Tree
                showLine={{ showLeafIcon: false }}
                showIcon={false}
                defaultExpandAll
                switcherIcon={({ expanded }) => expanded ? <CaretDownOutlined /> : <CaretRightOutlined />}
                treeData={convertToTreeData(treeData)}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: 32 }}>
                <Text>Нет данных для отображения</Text>
              </div>
            )
          ) : (
            <Table
              columns={columns}
              dataSource={filteredDivisions}
              rowKey="id"
              pagination={{ pageSize: 10 }}
              size="middle"
              bordered
            />
          )}
        </Spin>
      </Card>
      
      {/* Используем компонент DivisionEditModal здесь, предполагая что он тоже будет мигрирован на Ant Design */}
      {openCreate && (
        <DivisionEditModal
          open={openCreate}
          onClose={() => setOpenCreate(false)}
          onSave={handleSaveDivision}
          division={{
            id: 0,
            name: '',
            code: '',
            description: '',
            is_active: true,
            level: 0,
            organization_id: Number(selectedOrg) || 0,
            parent_id: null
          }}
          organizations={organizations}
          parentDivisions={divisions}
        />
      )}
      
      {openEdit && selectedDivision && (
        <DivisionEditModal
          open={openEdit}
          onClose={() => setOpenEdit(false)}
          onSave={handleSaveDivision}
          division={selectedDivision}
          organizations={organizations}
          parentDivisions={divisions.filter(d => d.id !== selectedDivision.id)}
        />
      )}
    </div>
  );
};

export default DivisionList; 