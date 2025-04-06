import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Typography,
  Form,
  Input,
  Button,
  Select,
  Divider,
  Avatar,
  Alert,
  Spin,
  Upload,
  Row,
  Col,
  Card,
  Space,
  message,
  Tooltip,
  Checkbox
} from 'antd';
import {
  SaveOutlined,
  CloseOutlined,
  UploadOutlined,
  UserOutlined,
  InfoCircleOutlined,
  PhoneOutlined,
  HomeOutlined,
  EnvironmentOutlined,
  IdcardOutlined,
} from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd/es/upload/interface';
import api from '../../services/api';
import { API_URL, MAX_FILE_SIZE, ALLOWED_FILE_TYPES } from '../../config';

const { Title, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// Типы данных для сотрудника
interface StaffFormData {
  first_name: string;
  last_name: string;
  middle_name?: string;
  email: string;
  phone?: string;
  position: string;
  organization_id: number | '';
  primary_organization_id?: number | null;
  location_id?: number | null;
  parent_id?: number | null;
  telegram_id?: string;
  vk?: string;
  instagram?: string;
  registration_address?: string;
  actual_address?: string;
  is_active: boolean;
}

interface Organization {
  id: number;
  name: string;
}

interface StaffMember {
  id: number;
  name: string;
  position: string;
}

// Начальное состояние формы
const initialFormData: StaffFormData = {
  first_name: '',
  last_name: '',
  middle_name: '',
  email: '',
  phone: '',
  position: '',
  organization_id: '',
  primary_organization_id: null,
  location_id: null,
  parent_id: null,
  telegram_id: '',
  vk: '',
  instagram: '',
  registration_address: '',
  actual_address: '',
  is_active: true
};

// Компонент формы сотрудника
const StaffForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditing = !!id;
  const [form] = Form.useForm();
  
  // Состояния
  const [formData, setFormData] = useState<StaffFormData>(initialFormData);
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [locations, setLocations] = useState<Organization[]>([]);
  const [managers, setManagers] = useState<StaffMember[]>([]);
  const [positions, setPositions] = useState<{id: number; name: string}[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  
  // Файлы
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [passportFile, setPassportFile] = useState<File | null>(null);
  const [contractFile, setContractFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>('');
  const [photoRequired, setPhotoRequired] = useState<boolean>(!isEditing); // Фото обязательно при создании
  
  // Загрузка данных организаций и потенциальных руководителей
  useEffect(() => {
    fetchOrganizations();
    fetchLocations();
    fetchPositions();
    
    if (isEditing) {
      fetchStaffData();
    }
  }, [id]);
  
  // Загрузить список организаций
  const fetchOrganizations = async () => {
    try {
      const response = await api.get('/organizations/');
      setOrganizations(response.data);
    } catch (err: any) {
      message.error('Ошибка при загрузке организаций: ' + (err.message || 'Неизвестная ошибка'));
      setError(err.message || 'Ошибка при загрузке организаций');
    }
  };

  // Загрузить список локаций (физических местоположений)
  const fetchLocations = async () => {
    try {
      const response = await api.get('/organizations/?org_type=location');
      setLocations(response.data);
    } catch (err: any) {
      message.error('Ошибка при загрузке локаций: ' + (err.message || 'Неизвестная ошибка'));
      setError(err.message || 'Ошибка при загрузке локаций');
    }
  };

  // Загрузить список должностей
  const fetchPositions = async () => {
    try {
      const response = await api.get('/positions/');
      setPositions(response.data);
    } catch (err: any) {
      message.error('Ошибка при загрузке должностей: ' + (err.message || 'Неизвестная ошибка'));
      setError(err.message || 'Ошибка при загрузке должностей');
    }
  };
  
  // Загрузить данные сотрудника для редактирования
  const fetchStaffData = async () => {
    setLoading(true);
    
    try {
      const response = await api.get(`/staff/${id}`);
      const data = response.data;
      
      const formValues = {
        first_name: data.first_name,
        last_name: data.last_name,
        middle_name: data.middle_name,
        email: data.email || '',
        phone: data.phone || '',
        position: data.position,
        organization_id: data.organization_id,
        primary_organization_id: data.primary_organization_id,
        parent_id: data.parent_id,
        is_active: data.is_active,
        location_id: data.location_id,
        telegram_id: data.telegram_id,
        vk: data.vk,
        instagram: data.instagram,
        registration_address: data.registration_address,
        actual_address: data.actual_address
      };
      
      setFormData(formValues);
      form.setFieldsValue(formValues);
      
      // Если есть фото, загружаем превью
      if (data.photo_path) {
        setPhotoPreview(`${API_URL}/uploads/${data.photo_path}`);
        setPhotoRequired(false); // При редактировании, если уже есть фото, не требуем загрузки
      }
      
      // Загружаем возможных руководителей из той же организации
      fetchPotentialManagers(data.organization_id);
    } catch (err: any) {
      message.error('Ошибка при загрузке данных сотрудника: ' + (err.message || 'Неизвестная ошибка'));
      setError(err.message || 'Ошибка при загрузке данных сотрудника');
    } finally {
      setLoading(false);
    }
  };
  
  // Загрузить потенциальных руководителей при выборе организации
  const fetchPotentialManagers = async (orgId: number) => {
    if (!orgId) return;
    
    try {
      const response = await api.get(`/staff/?organization_id=${orgId}`);
      const data = response.data;
      
      // Исключаем текущего сотрудника из списка потенциальных руководителей
      const filteredManagers = isEditing
        ? data.filter((member: StaffMember) => member.id !== parseInt(id as string))
        : data;
      
      setManagers(filteredManagers);
    } catch (err: any) {
      console.error('Ошибка при загрузке потенциальных руководителей:', err);
    }
  };
  
  // Обработчики изменения полей формы
  const handleFormChange = (changedValues: any, allValues: any) => {
    setFormData(allValues);
    
    // Если изменилась организация, загружаем руководителей
    if ('organization_id' in changedValues) {
      const orgId = changedValues.organization_id;
      if (orgId) {
        fetchPotentialManagers(orgId);
        
        // Сбрасываем выбранного руководителя
        form.setFieldValue('parent_id', null);
      }
    }
  };
  
  // Обработчики загрузки файлов
  const handlePhotoChange: UploadProps['onChange'] = ({ file }) => {
    const fileObj = file.originFileObj;
    
    if (fileObj) {
      // Проверка размера файла
      if (fileObj.size > MAX_FILE_SIZE) {
        message.error(`Размер файла превышает максимально допустимый (${MAX_FILE_SIZE / 1024 / 1024} MB)`);
        return;
      }
      
      // Проверка типа файла
      if (!ALLOWED_FILE_TYPES.includes(fileObj.type)) {
        message.error(`Недопустимый тип файла. Разрешены: ${ALLOWED_FILE_TYPES.join(', ')}`);
        return;
      }
      
      setPhotoFile(fileObj);
      setPhotoPreview(URL.createObjectURL(fileObj));
      setPhotoRequired(false); // Если загрузили фото, снимаем требование
    }
  };
  
  const handlePassportChange: UploadProps['onChange'] = ({ file }) => {
    const fileObj = file.originFileObj;
    
    if (fileObj) {
      // Проверка размера файла
      if (fileObj.size > MAX_FILE_SIZE) {
        message.error(`Размер файла превышает максимально допустимый (${MAX_FILE_SIZE / 1024 / 1024} MB)`);
        return;
      }
      
      // Проверка типа файла (для документов можно разрешить PDF)
      const allowedDocTypes = [...ALLOWED_FILE_TYPES, 'application/pdf'];
      if (!allowedDocTypes.includes(fileObj.type)) {
        message.error(`Недопустимый тип файла. Разрешены: ${allowedDocTypes.join(', ')}`);
        return;
      }
      
      setPassportFile(fileObj);
      message.success(`Файл ${fileObj.name} успешно загружен`);
    }
  };
  
  const handleContractChange: UploadProps['onChange'] = ({ file }) => {
    const fileObj = file.originFileObj;
    
    if (fileObj) {
      // Проверка размера файла
      if (fileObj.size > MAX_FILE_SIZE) {
        message.error(`Размер файла превышает максимально допустимый (${MAX_FILE_SIZE / 1024 / 1024} MB)`);
        return;
      }
      
      // Проверка типа файла (для документов можно разрешить PDF)
      const allowedDocTypes = [...ALLOWED_FILE_TYPES, 'application/pdf'];
      if (!allowedDocTypes.includes(fileObj.type)) {
        message.error(`Недопустимый тип файла. Разрешены: ${allowedDocTypes.join(', ')}`);
        return;
      }
      
      setContractFile(fileObj);
      message.success(`Файл ${fileObj.name} успешно загружен`);
    }
  };
  
  // Отправка формы
  const handleSubmit = async (values: any) => {
    // Проверка наличия фото при создании
    if (photoRequired && !photoFile) {
      message.error('Необходимо загрузить фотографию сотрудника');
      return;
    }

    setSubmitting(true);
    setError(null);
    
    try {
      let apiUrl = `/staff/`;
      let method = 'POST';
      
      // Если редактирование, используем PUT и добавляем ID
      if (isEditing) {
        apiUrl += `${id}`;
        method = 'PUT';
      }
      
      // Создаем копию данных
      const staffData = { ...values };
      
      // Удаляем null и undefined значения
      Object.keys(staffData).forEach(key => {
        if (staffData[key] === null || staffData[key] === undefined) {
          delete staffData[key];
        }
      });
      
      // Предупреждение об отключенной загрузке файлов
      if (photoFile || passportFile || contractFile) {
        message.warning('Загрузка файлов временно отключена. Файлы не будут сохранены.');
      }
      
      // Простой POST/PUT запрос
      const response = method === 'POST' 
        ? await api.post(apiUrl, staffData)
        : await api.put(apiUrl, staffData);
      
      console.log('[LOG:Staff] Успешный ответ:', response);
      
      // Успех
      setSuccess(true);
      message.success(`Сотрудник успешно ${isEditing ? 'обновлен' : 'добавлен'}!`);
      
      // Редирект на список сотрудников после небольшой задержки
      setTimeout(() => {
        navigate('/staff');
      }, 1500);
    } catch (error: any) {
      console.error('[LOG:Staff] Ошибка при сохранении:', error);
      
      // Обработка ошибок
      if (error.response) {
        const errorMessage = error.response.data?.detail || error.message || 'Ошибка при сохранении';
        setError(errorMessage);
        message.error(errorMessage);
      } else {
        const errorMessage = error.message || 'Сетевая ошибка, проверьте подключение';
        setError(errorMessage);
        message.error(errorMessage);
      }
    } finally {
      setSubmitting(false);
    }
  };
  
  // Отмена и возврат к списку
  const handleCancel = () => {
    navigate('/staff');
  };
  
  // Только сохраняем настройки для компонентов загрузки
  const uploadProps = {
    beforeUpload: () => false, // Отключаем автоматическую загрузку
    showUploadList: false,     // Скрываем список файлов
  };
  
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <Spin size="large" />
      </div>
    );
  }
  
  return (
    <div style={{ padding: '24px' }}>
      <Card>
        <Title level={4}>
          {isEditing ? 'Редактирование сотрудника' : 'Добавление нового сотрудника'}
        </Title>
        
        {error && (
          <Alert 
            message="Ошибка" 
            description={error} 
            type="error" 
            showIcon 
            closable 
            style={{ marginBottom: 16 }}
            onClose={() => setError(null)}
          />
        )}
        
        {success && (
          <Alert 
            message="Успех" 
            description={`Сотрудник успешно ${isEditing ? 'обновлен' : 'добавлен'}!`} 
            type="success" 
            showIcon 
            style={{ marginBottom: 16 }}
          />
        )}
        
        <Form
          form={form}
          layout="vertical"
          initialValues={initialFormData}
          onFinish={handleSubmit}
          onValuesChange={handleFormChange}
          requiredMark="optional"
        >
          {/* Основная информация */}
          <Title level={5}>Основная информация</Title>
          
          <Row gutter={24}>
            <Col xs={24} md={8}>
              <Form.Item
                name="first_name"
                label="Имя"
                rules={[{ required: true, message: 'Имя обязательно' }]}
              >
                <Input placeholder="Введите имя" />
              </Form.Item>
            </Col>
            
            <Col xs={24} md={8}>
              <Form.Item
                name="last_name"
                label="Фамилия"
                rules={[{ required: true, message: 'Фамилия обязательна' }]}
              >
                <Input placeholder="Введите фамилию" />
              </Form.Item>
            </Col>
            
            <Col xs={24} md={8}>
              <Form.Item
                name="middle_name"
                label="Отчество"
              >
                <Input placeholder="Введите отчество" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item
                name="email"
                label="Email"
                rules={[
                  { required: true, message: 'Email обязателен' },
                  { type: 'email', message: 'Введите корректный email' }
                ]}
              >
                <Input placeholder="email@example.com" />
              </Form.Item>
            </Col>
            
            <Col xs={24} md={12}>
              <Form.Item
                name="phone"
                label="Телефон"
              >
                <Input placeholder="+7 (___) ___-__-__" />
              </Form.Item>
            </Col>
          </Row>
          
          <Divider />
          
          {/* Информация об организации */}
          <Title level={5}>Информация об организации</Title>
          
          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item
                name="position"
                label="Должность"
                rules={[{ required: true, message: 'Должность обязательна' }]}
              >
                <Select placeholder="Выберите должность">
                  {positions.map(pos => (
                    <Option key={pos.id} value={pos.name}>{pos.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col xs={24} md={12}>
              <Form.Item
                name="organization_id"
                label="Организация"
                rules={[{ required: true, message: 'Организация обязательна' }]}
              >
                <Select placeholder="Выберите организацию" onChange={(value) => fetchPotentialManagers(value as number)}>
                  {organizations.map(org => (
                    <Option key={org.id} value={org.id}>{org.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item
                name="primary_organization_id"
                label="Основная организация"
              >
                <Select placeholder="Выберите основную организацию" allowClear>
                  {organizations.map(org => (
                    <Option key={org.id} value={org.id}>{org.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            
            <Col xs={24} md={12}>
              <Form.Item
                name="location_id"
                label="Локация (физическое местоположение)"
              >
                <Select placeholder="Выберите локацию" allowClear>
                  {locations.map(loc => (
                    <Option key={loc.id} value={loc.id}>{loc.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item
                name="parent_id"
                label="Руководитель"
              >
                <Select placeholder="Выберите руководителя" allowClear>
                  {managers.map(manager => (
                    <Option key={manager.id} value={manager.id}>
                      {manager.name} ({manager.position})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>
          
          <Divider />
          
          {/* Социальные сети */}
          <Title level={5}>Социальные сети</Title>
          
          <Row gutter={24}>
            <Col xs={24} md={8}>
              <Form.Item
                name="telegram_id"
                label="Telegram ID"
              >
                <Input placeholder="@username" />
              </Form.Item>
            </Col>
            
            <Col xs={24} md={8}>
              <Form.Item
                name="vk"
                label="ВКонтакте"
              >
                <Input placeholder="URL профиля ВКонтакте" />
              </Form.Item>
            </Col>
            
            <Col xs={24} md={8}>
              <Form.Item
                name="instagram"
                label="Instagram"
              >
                <Input placeholder="@username" />
              </Form.Item>
            </Col>
          </Row>
          
          <Divider />
          
          {/* Адресная информация */}
          <Title level={5}>Адресная информация</Title>
          
          <Row gutter={24}>
            <Col xs={24} md={12}>
              <Form.Item
                name="registration_address"
                label="Адрес регистрации"
              >
                <TextArea rows={2} placeholder="Введите адрес регистрации" />
              </Form.Item>
            </Col>
            
            <Col xs={24} md={12}>
              <Form.Item
                name="actual_address"
                label="Фактический адрес"
              >
                <TextArea rows={2} placeholder="Введите фактический адрес" />
              </Form.Item>
            </Col>
          </Row>
          
          <Divider />
          
          {/* Загрузка файлов */}
          <Title level={5}>Документы</Title>
          
          <Row gutter={24}>
            <Col xs={24} md={8} style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: 16 }}>
                {photoPreview ? (
                  <Avatar
                    src={photoPreview}
                    alt="Фото"
                    size={120}
                    style={{ marginBottom: 8 }}
                  />
                ) : (
                  <Avatar
                    icon={<UserOutlined />}
                    size={120}
                    style={{ marginBottom: 8 }}
                  />
                )}
                
                <div>
                  <Upload {...uploadProps} onChange={handlePhotoChange}>
                    <Button icon={<UploadOutlined />}>Загрузить фото</Button>
                  </Upload>
                </div>
              </div>
            </Col>
            
            <Col xs={24} md={8} style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: 16 }}>
                <Text>Паспорт</Text>
                <div style={{ marginTop: 8 }}>
                  <Upload {...uploadProps} onChange={handlePassportChange}>
                    <Button icon={<UploadOutlined />}>Загрузить паспорт</Button>
                  </Upload>
                </div>
                {passportFile && (
                  <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
                    {passportFile.name}
                  </Text>
                )}
              </div>
            </Col>
            
            <Col xs={24} md={8} style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: 16 }}>
                <Text>Трудовой договор</Text>
                <div style={{ marginTop: 8 }}>
                  <Upload {...uploadProps} onChange={handleContractChange}>
                    <Button icon={<UploadOutlined />}>Загрузить договор</Button>
                  </Upload>
                </div>
                {contractFile && (
                  <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
                    {contractFile.name}
                  </Text>
                )}
              </div>
            </Col>
          </Row>
          
          <Divider />
          
          {/* Дополнительная информация */}
          <Title level={5}>Дополнительная информация</Title>
          
          <Row gutter={24}>
            <Col span={24}>
              <Form.Item
                name="is_active"
                valuePropName="checked"
              >
                <Checkbox>Активный сотрудник</Checkbox>
              </Form.Item>
            </Col>
          </Row>
          
          {/* Кнопки */}
          <Row justify="end" gutter={16}>
            <Col>
              <Button onClick={handleCancel}>
                <CloseOutlined /> Отмена
              </Button>
            </Col>
            <Col>
              <Button type="primary" htmlType="submit" loading={submitting}>
                <SaveOutlined /> {isEditing ? 'Обновить' : 'Создать'}
              </Button>
            </Col>
          </Row>
        </Form>
      </Card>
    </div>
  );
};

export default StaffForm; 