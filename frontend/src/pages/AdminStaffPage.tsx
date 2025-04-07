import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Button,
  Table,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Spin,
  message,
  Alert,
  Switch, // Для is_active
  Typography,
  Card,
  Popconfirm,
  Result,
  Row,
  Col,
  Upload,
  Tooltip,
  Checkbox,
  Tag,
  Tabs,
  Divider,
  Layout
} from 'antd';
import type { SortOrder } from 'antd/es/table/interface'; // Добавляем тип для сортировки
import type { UploadFile } from 'antd/es/upload/interface'; // Типы для Upload компонента
import {
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
  DisconnectOutlined,
  ApiOutlined,
  IdcardOutlined,
  PhoneOutlined,
  InfoCircleOutlined,
  UploadOutlined,
  MailOutlined,
  SearchOutlined,
  PaperClipOutlined,
  FileOutlined,
  UserOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons';
import api, { checkApiHealth, delay } from '../services/api';
import { maskPhoneNumber } from '../utils/formatters'; // Добавляем импорт функции маскирования телефона
// Импортируем наш неоморфный компонент кнопки
import NeoButton from '../components/ui/NeoButton';
import { CultNeumorphButton } from '../components/ui/CultNeumorphButton'; // <-- Добавляем импорт
// Убираем import { API_URL } from '../config'; - он не используется напрямую
// Убираем import { Link } from 'react-router-dom'; - не используется
import type { ColumnsType } from 'antd/lib/table';
import { useNavigate } from 'react-router-dom';
// Импортируем нужные типы из types/organization.ts
import type { Staff, Address, Organization as OrgType, Position as PosType, Division as DivType } from '../types/organization'; 
// (Переименовываем импортируемые типы, чтобы избежать конфликтов имен)

const { Title } = Typography;
const { Option } = Select;

// Интерфейс Staff
/*interface Staff {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone?: string;
  position?: string;
  position_id?: number;
  description?: string;
  is_active: boolean;
  organization_id?: number; 
  primary_organization_id?: number; // Пока оставим, но возможно не нужно в UI напрямую
  // Добавим поля, которых не было, но могут понадобиться
  division_id?: number;
  location_id?: number;
  telegram_id?: string;
  registration_address?: string;
  actual_address?: string;
  vk?: string;
  instagram?: string;
  photo_path?: string;
  created_at: string;
  updated_at: string;
}

interface Organization {
  id: number;
  name: string;
  org_type?: string; // Тип организации (holding, legal_entity, location и т.д.)
}

// Добавим типы для новых сущностей
interface Position {
    id: number;
    name: string;
}

interface Division {
    id: number;
    name: string;
}*/

// Тип для формы загрузки файлов в antd Upload
interface UploadFormValue {
  fileList: UploadFile[];
  file: UploadFile;
}

// Интерфейс для структуры адреса
interface AddressFields {
  index: string;
  city: string;
  street: string;
  house: string;
  building?: string;
  apartment?: string;
}

// !!! Убираем старое предупреждение о переименовании !!!
const AdminStaffPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [tableLoading, setTableLoading] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [staff, setStaff] = useState<Staff[]>([]); // Теперь используется импортированный Staff
  const [filteredStaff, setFilteredStaff] = useState<Staff[]>([]);
  const [organizations, setOrganizations] = useState<OrgType[]>([]); // Используем OrgType
  const [positions, setPositions] = useState<PosType[]>([]); // Используем PosType
  const [divisions, setDivisions] = useState<DivType[]>([]); // Используем DivType
  const [locations, setLocations] = useState<any[]>([]); // Добавляем состояние для локаций
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<Staff | null>(null);
  // Новое состояние для детальной карточки сотрудника
  const [isDetailModalVisible, setIsDetailModalVisible] = useState(false);
  const [selectedStaff, setSelectedStaff] = useState<Staff | null>(null);
  // Добавляем состояние для отслеживания статуса API
  const [apiStatus, setApiStatus] = useState<{
    connected: boolean;
    message: string;
    checking: boolean;
  }>({
    connected: false,
    message: 'Проверка соединения...',
    checking: true
  });

  const [form] = Form.useForm();
  const abortControllerRef = useRef<AbortController | null>(null);

  // Состояния для данных
  const [searchText, setSearchText] = useState('');
  const [searchColumn, setSearchColumn] = useState('');
  const [filterParams, setFilterParams] = useState({
    organization_id: null as number | null,
    position_id: null as number | null,
    is_active: true as boolean | null,
  });

  const fetchData = useCallback(async () => {
    try {
      // Загрузка всех данных параллельно
      setLoading(true);
      setApiStatus(prev => ({ ...prev, checking: true }));
      
      console.log('[LOG:Staff] Начинаем параллельную загрузку данных...');
      
      const loadOrganizations = async () => {
        try {
          console.log('[LOG:Staff] Запрос GET /organizations');
          const orgResponse = await api.get('/organizations');
          console.log('[LOG:Staff] Получен ответ от /organizations');
          if (Array.isArray(orgResponse.data)) {
            console.log(`[LOG:Staff] Загружено ${orgResponse.data.length} организаций`);
            setOrganizations(orgResponse.data);
            return true; // Успех
          } else {
            console.error('[LOG:Staff] Ошибка: Ответ API организаций не является массивом:', orgResponse.data);
            throw new Error('Неверный формат данных организаций');
          }
        } catch (orgError) {
          console.error('[LOG:Staff] Ошибка при загрузке организаций:', orgError);
          message.warning('Не удалось загрузить список организаций. Используются временные данные.');
          console.log('[LOG:Staff] Использую временные данные для организаций');
          // Используем Partial<OrgType> для временных данных
          const tempOrgs: Partial<OrgType>[] = [
            { id: 1, name: 'ООО "Рога и Копыта"' },
            { id: 2, name: 'ИП Пупкин' },
            { id: 3, name: 'ЗАО "Весёлый молочник"' },
          ];
          setOrganizations(tempOrgs as OrgType[]); // Приводим тип обратно к OrgType[] для state
          return false; // Неудача
        }
      };

      const loadPositions = async () => {
        try {
          console.log('[LOG:Staff] Запрос GET /positions');
          const positionsResponse = await api.get('/positions');
          console.log('[LOG:Staff] Получен ответ от /positions');
          if (Array.isArray(positionsResponse.data)) {
            console.log(`[LOG:Staff] Загружено ${positionsResponse.data.length} должностей`);
            setPositions(positionsResponse.data);
            return true;
          } else {
            console.error('[LOG:Staff] Ошибка: Ответ API должностей не является массивом:', positionsResponse.data);
            throw new Error('Неверный формат данных должностей');
          }
        } catch (posError) {
          console.error('[LOG:Staff] Ошибка при загрузке должностей:', posError);
          message.warning('Не удалось загрузить список должностей. Используются временные данные.');
          console.log('[LOG:Staff] Использую временные данные для должностей');
          // Используем Partial<PosType> для временных данных
          const tempPositions: Partial<PosType>[] = [
            { id: 1, name: 'Директор' },
            { id: 2, name: 'Менеджер' },
            { id: 3, name: 'Программист' },
            { id: 4, name: 'Дизайнер' },
            { id: 5, name: 'Бухгалтер' },
          ];
          setPositions(tempPositions as PosType[]); // Приводим тип обратно к PosType[] для state
          return false;
        }
      };

      const loadLocations = async () => {
        try {
          console.log('[LOG:Staff] Запрос GET /organizations?org_type=location');
          const locationsResponse = await api.get('/organizations?org_type=location'); // <-- Исправленный запрос
          console.log('[LOG:Staff] Получен ответ от /organizations для локаций');
          if (Array.isArray(locationsResponse.data)) {
            console.log(`[LOG:Staff] Загружено ${locationsResponse.data.length} локаций`);
            setLocations(locationsResponse.data);
            return true;
          } else {
            console.error('[LOG:Staff] Ошибка: Ответ API локаций не является массивом:', locationsResponse.data);
            throw new Error('Неверный формат данных локаций');
          }
        } catch (locError) {
          console.error('[LOG:Staff] Ошибка при загрузке локаций:', locError);
          message.warning('Не удалось загрузить список локаций. Используются временные данные.');
          console.log('[LOG:Staff] Использую временные данные для локаций');
          setLocations([
            { id: 1, name: 'Москва' },
            { id: 2, name: 'Санкт-Петербург' },
            { id: 3, name: 'Казань' },
            { id: 4, name: 'Новосибирск' },
          ]);
          return false;
        }
      };
      
      const loadStaff = async () => {
          try {
              console.log('[LOG:Staff] Запрос GET /staff');
              const response = await api.get('/staff', { signal: abortControllerRef.current?.signal });
              console.log('[LOG:Staff] Получен ответ от /staff');
              if (Array.isArray(response.data)) {
                console.log(`[LOG:Staff] Загружено ${response.data.length} сотрудников`);
                setStaff(response.data);
                setFilteredStaff(response.data); // Раскомментируем эту строку!
                return true;
              } else {
                console.error('[LOG:Staff] Ошибка: Ответ API сотрудников не является массивом:', response.data);
                throw new Error('Неверный формат данных сотрудников');
              }
            } catch (error: any) {
              if (error.name === 'CanceledError') {
                console.log('[LOG:Staff] Запрос сотрудников отменен');
                return false;
              }
              console.error('[LOG:Staff] Ошибка при загрузке сотрудников:', error);
              message.error('Не удалось загрузить список сотрудников. Попробуйте обновить.');
              return false;
            }
      };

      try {
        // Выполняем все запросы параллельно
        const results = await Promise.allSettled([
          loadOrganizations(),
          loadPositions(),
          loadLocations(),
          loadStaff() // Загрузка сотрудников тоже параллельно
        ]);
        
        console.log('[LOG:Staff] Результаты параллельной загрузки:', results);
        
        // Проверяем, были ли ошибки
        const hasErrors = results.some(result => result.status === 'rejected' || (result.status === 'fulfilled' && result.value === false));
        
        if (!hasErrors) {
            console.log('[LOG:Staff] Все данные успешно загружены');
            setApiStatus(prev => ({ ...prev, connected: true, message: 'Данные загружены успешно', checking: false }));
        } else {
            console.warn('[LOG:Staff] При загрузке данных возникли проблемы (возможно, использованы временные данные).');
            // Ставим connected: true, так как хотя бы часть данных (сотрудники) могли загрузиться
            // Или определяем статус на основе загрузки сотрудников
            const staffLoadResult = results[3]; // Результат loadStaff()
            const staffLoaded = staffLoadResult.status === 'fulfilled' && staffLoadResult.value === true;
            setApiStatus(prev => ({
              ...prev,
              connected: staffLoaded, // Статус зависит от загрузки основного списка
              message: staffLoaded ? 'Данные частично загружены (проблемы с доп. справочниками)' : 'Ошибка загрузки основных данных сотрудников',
              checking: false
            }));
            if (!staffLoaded) {
               message.error('Не удалось загрузить основной список сотрудников.');
            } else {
               message.info('Список сотрудников загружен, но возникли проблемы с загрузкой связанных данных (локации, должности).');
            }
        }
        
      } catch (error) {
        // Этот catch маловероятен при использовании Promise.allSettled, но на всякий случай
        console.error('[LOG:Staff] Глобальная ошибка при параллельной загрузке данных:', error);
        message.error('Произошла критическая ошибка при загрузке данных');
        setApiStatus(prev => ({ ...prev, connected: false, message: 'Ошибка загрузки данных', checking: false }));
      } finally {
        setLoading(false);
      }
    } catch (error) {
      console.error('[LOG:Staff] Ошибка при загрузке данных:', error);
      message.error('Не удалось загрузить данные');
      setApiStatus(prev => ({
        ...prev,
        connected: false,
        message: 'Ошибка загрузки данных',
        checking: false
      }));
    }
  }, []);

  // Эффект для загрузки данных при монтировании компонента
  useEffect(() => {
    console.log('[LOG:Staff] Начальная загрузка данных при монтировании');
    fetchData();
  }, [fetchData]);

  // Функция для проверки подключения к API - без зависимостей вообще
  const checkConnection = useCallback(async () => {
    try {
      setApiStatus(prev => ({ ...prev, checking: true }));
      
      // Добавляем параметр, чтобы избежать кеширования
      const timestamp = new Date().getTime();
      console.log(`[LOG:Staff] Проверка подключения к API (${timestamp})...`);
      
      const health = await checkApiHealth();
      console.log('[LOG:Staff] Результат проверки API:', health);
      
      if (health.success) {
        setApiStatus({
          connected: true,
          message: `Соединение с сервером установлено. Получено ${health.data?.length || 0} записей.`,
          checking: false
        });
        return true;
      } else {
        // Более подробное сообщение об ошибке
        let errorMessage = `Ошибка соединения: ${health.message}`;
        if (health.status === 'network_error') {
          errorMessage += ' Проверьте, запущен ли сервер.';
        }
        
        setApiStatus({
          connected: false,
          message: errorMessage,
          checking: false
        });
        return false;
      }
    } catch (error: any) {
      console.error('[LOG:Staff] Непредвиденная ошибка при проверке соединения:', error);
      setApiStatus({
        connected: false,
        message: `Ошибка соединения: ${error.message || 'Неизвестная ошибка'}`,
        checking: false
      });
      return false;
    }
  }, []);

  // Инициализация при первой загрузке компонента - одна функция без зависимостей
  useEffect(() => {
    console.log('[LOG:Staff] Компонент смонтирован, запускаем инициализацию');
    
    let isMounted = true;
    
    // Функция инициализации - запускается один раз при монтировании
    const initComponent = async () => {
      if (!isMounted) return;
      
      // Сначала проверяем соединение
      console.log('[LOG:Staff] Выполняем первичную проверку соединения');
      await checkConnection();
      
      // Затем загружаем данные
      if (isMounted) {
        console.log('[LOG:Staff] Выполняем первичную загрузку данных');
        await fetchData();
      }
    };
    
    // Запускаем инициализацию
    initComponent();
    
    // Отмена запросов при размонтировании
    return () => {
      console.log('[LOG:Staff] Компонент размонтирован, отменяем запросы');
      isMounted = false;
      abortControllerRef.current?.abort();
    };
  }, []);

  // Добавляем обработчик неожиданных ошибок
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      console.error('[LOG:Staff] Неперехваченная ошибка:', event.error);
      message.error('Произошла ошибка в интерфейсе. Посмотрите консоль разработчика для деталей.');
    };

    window.addEventListener('error', handleError);
    
    return () => {
      window.removeEventListener('error', handleError);
    };
  }, []);

  // Фильтрация данных
  const getFilteredStaff = useCallback(() => {
    if (!staff.length) return [];
    
    return staff.filter(item => {
      // Фильтрация по поисковому запросу
      if (searchText) {
        const fullName = `${item.last_name || ''} ${item.first_name || ''} ${item.middle_name || ''}`.toLowerCase();
        const emailSearch = item.email ? item.email.toLowerCase() : '';
        const phoneSearch = item.phone ? item.phone.toLowerCase() : '';
        
        // Исправляем поиск по должности: используем position_id для поиска имени
        const positionName = positions.find(p => p.id === item.position_id)?.name || '';
        const positionSearch = positionName.toLowerCase();
        
        const searchLower = searchText.toLowerCase();
        
        // Поиск по имени, email, телефону или должности
        if (!fullName.includes(searchLower) && 
            !emailSearch.includes(searchLower) && 
            !phoneSearch.includes(searchLower) &&
            !positionSearch.includes(searchLower)) {
          return false;
        }
      }
      
      // Фильтр по организации
      if (filterParams.organization_id && item.organization_id !== filterParams.organization_id) {
        return false;
      }
      
      // Фильтр по должности
      if (filterParams.position_id) {
        // Проверка по position_id (основной способ)
        if (item.position_id !== filterParams.position_id) {
          return false;
        }
        // Убираем проверку по текстовому полю item.position, т.к. его больше нет
        // const positionObj = positions.find(p => p.id === filterParams.position_id);
        // const positionNameMatch = positionObj && item.position === positionObj.name;
        // if (!hasPositionIdMatch && !positionNameMatch) {
        //   return false;
        // }
      }
      
      // Фильтр по активности (только если не null)
      if (filterParams.is_active !== null && item.is_active !== filterParams.is_active) {
        return false;
      }
      
      return true;
    });
  }, [staff, searchText, filterParams, positions]);

  // Обработчики фильтров
  const handleOrganizationFilter = (value: number | null) => {
    setFilterParams(prev => ({ ...prev, organization_id: value }));
  };
  
  const handlePositionFilter = (value: number | null) => {
    setFilterParams(prev => ({ ...prev, position_id: value }));
  };
  
  const handleActiveFilter = (value: boolean | null) => {
    setFilterParams(prev => ({ ...prev, is_active: value }));
  };
  
  const handleSearch = (value: string) => {
    setSearchText(value);
  };
  
  const resetFilters = () => {
    setFilterParams({
      organization_id: null,
      position_id: null,
      is_active: true,
    });
    setSearchText('');
  };

  // Обработчик изменения текста в поле телефона 
  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target;
    // Форматируем телефон с пробелами
    const maskedValue = maskPhoneNumber(value);
    form.setFieldsValue({ phone: maskedValue });
  };

  // Распаковываем адрес при редактировании
  const parseAddressToFields = (addressStr: string | null | undefined): AddressFields | null => {
    if (!addressStr) return null;
    
    try {
      // Формат: "индекс, город, ул. улица, д. дом, корп. корпус, кв./офис квартира"
      const indexMatch = addressStr.match(/^(\d+),\s*/);
      const cityMatch = addressStr.match(/,\s*([^,]+),\s*ул\./);
      const streetMatch = addressStr.match(/ул\.\s*([^,]+),\s*д\./);
      const houseMatch = addressStr.match(/д\.\s*([^,]+)/);
      const buildingMatch = addressStr.match(/корп\.\s*([^,]+)/);
      const apartmentMatch = addressStr.match(/кв\.\/офис\s*([^,]+)/);
      
      return {
        index: indexMatch ? indexMatch[1] : '',
        city: cityMatch ? cityMatch[1].trim() : '',
        street: streetMatch ? streetMatch[1].trim() : '',
        house: houseMatch ? houseMatch[1].trim() : '',
        building: buildingMatch ? buildingMatch[1].trim() : '',
        apartment: apartmentMatch ? apartmentMatch[1].trim() : ''
      };
    } catch (error) {
      console.error('[LOG:Staff] Ошибка при разборе адреса:', error);
      return null;
    }
  };

  // Обработчик открытия модального окна для создания/редактирования
  const handleOpenModal = (item?: Staff) => {
    setEditingItem(item || null);
    form.resetFields();
    
    if (item) {
      // Убираем парсинг адресов - они уже должны быть объектами типа Address | null
      // const regAddress = parseAddressToFields(item.registration_address);
      // const actAddress = parseAddressToFields(item.actual_address);
      
      // Заполняем форму данными редактируемого элемента
      form.setFieldsValue({
        first_name: item.first_name,
        last_name: item.last_name,
        middle_name: item.middle_name,
        email: item.email,
        phone: item.phone,
        // Исправляем получение position_id - теперь это прямое поле
        position_id: item.position_id, 
        organization_id: item.organization_id,
        primary_organization_id: item.primary_organization_id,
        location_id: item.location_id,
        telegram_id: item.telegram_id,
        vk: item.vk, // Теперь это поле есть в типе
        instagram: item.instagram, // Теперь это поле есть в типе
        // Передаем объекты адресов напрямую
        reg_address: item.registration_address, 
        act_address: item.actual_address, 
        description: item.description,
        is_active: item.is_active,
        // !!! ВАЖНО: photo и documents (файлы) нужно обрабатывать отдельно,
        // так как form.setFieldsValue не умеет работать с Upload компонентом.
        // Обычно их состояние управляется отдельно или сбрасывается.
        // Пока оставляем как есть, но это может потребовать доработки.
      });
    }
    
    setIsModalVisible(true);
  };

  // Функция для удаления записи
  const handleDelete = async (id: number) => {
    try {
      console.log('[LOG:Staff] Удаление записи с ID:', id);
      setLoading(true);
      
      const response = await api.delete(`/staff/${id}`);
      console.log('[LOG:Staff] Ответ API при удалении:', response);
      
      message.success('Сотрудник успешно удален');
      
      // Удаляем из локального состояния
      setStaff(staff.filter(item => item.id !== id));
      
      // Обновляем данные для уверенности
      setTimeout(() => {
        console.log('[LOG:Staff] Обновление данных после удаления');
        fetchData();
      }, 300);
      
    } catch (error) {
      console.error('[LOG:Staff] Ошибка при удалении сотрудника:', error);
      message.error('Ошибка при удалении сотрудника');
    } finally {
      setLoading(false);
    }
  };

  // Логика сохранения (создание или обновление)
  const handleSave = async () => {
    try {
      const values = await form.validateFields(); // Валидация формы AntD
      setModalLoading(true);
      
      console.log('[LOG:Staff] Данные формы для сохранения:', values);
      
      // Проверяем основные поля формы
      const requiredFields = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'email': 'Email',
        'position_id': 'Должность',
        'organization_id': 'Организация',
        'telegram_id': 'Telegram ID' // Добавляем поле Telegram
      };
      
      const missingFields: string[] = [];
      
      // Проверяем наличие всех обязательных полей
      Object.entries(requiredFields).forEach(([field, label]) => {
        if (!values[field]) {
          missingFields.push(label);
        }
      });
      
      if (missingFields.length > 0) {
        const fields = missingFields.join(', ');
        message.error({
          content: `Не заполнены обязательные поля: ${fields}`,
          duration: 5,
          style: { marginTop: '20px' }
        });
        
        // Переключаемся на соответствующую вкладку в зависимости от отсутствующих полей
        const tabsElement = document.querySelector('.ant-tabs-nav-list');
        if (missingFields.includes('Организация')) {
          // Переключаемся на вкладку "Информация об организации"
          const orgTab = tabsElement?.querySelectorAll('.ant-tabs-tab')[1];
          if (orgTab) {
            (orgTab as HTMLElement).click();
          }
        } else {
          // Переключаемся на вкладку "Основная информация"
          const basicTab = tabsElement?.querySelectorAll('.ant-tabs-tab')[0];
          if (basicTab) {
            (basicTab as HTMLElement).click();
          }
        }
        
        setModalLoading(false);
        return; // Прерываем выполнение
      }
      
      // Проверка адресных данных
      // Дополнительная проверка адреса - оба адреса должны быть заполнены полностью!
      const regAddress = values.reg_address || {};
      const actAddress = values.act_address || {};
      
      // Проверяем регистрационный адрес
      const regAddressMissing: string[] = [];
      if (!regAddress.index) regAddressMissing.push('индекс');
      if (!regAddress.city) regAddressMissing.push('город');
      if (!regAddress.street) regAddressMissing.push('улица');
      if (!regAddress.house) regAddressMissing.push('дом');
      
      if (regAddressMissing.length > 0) {
        const fields = regAddressMissing.join(', ');
        message.error({
          content: `Адрес регистрации: не заполнены обязательные поля (${fields})`,
          duration: 5,
          style: { marginTop: '20px' }
        });
        
        // Переключаемся на вкладку с адресами
        const tabsElement = document.querySelector('.ant-tabs-nav-list');
        const addressTab = tabsElement?.querySelectorAll('.ant-tabs-tab')[3]; // Индекс вкладки с адресами
        if (addressTab) {
          (addressTab as HTMLElement).click();
        }
        
        setModalLoading(false);
        return; // Прерываем выполнение
      }
      
      // Проверяем фактический адрес
      const actAddressMissing: string[] = [];
      if (!actAddress.index) actAddressMissing.push('индекс');
      if (!actAddress.city) actAddressMissing.push('город');
      if (!actAddress.street) actAddressMissing.push('улица');
      if (!actAddress.house) actAddressMissing.push('дом');
      
      if (actAddressMissing.length > 0) {
        const fields = actAddressMissing.join(', ');
        message.error({
          content: `Фактический адрес: не заполнены обязательные поля (${fields})`,
          duration: 5,
          style: { marginTop: '20px' }
        });
        
        // Переключаемся на вкладку с адресами
        const tabsElement = document.querySelector('.ant-tabs-nav-list');
        const addressTab = tabsElement?.querySelectorAll('.ant-tabs-tab')[3]; // Индекс вкладки с адресами
        if (addressTab) {
          (addressTab as HTMLElement).click();
        }
        
        setModalLoading(false);
        return; // Прерываем выполнение
      }
      
      // Создаем FormData для отправки файлов и данных
      const formData = new FormData();
      
      // Проверяем наличие файлов
      const hasPhoto = values.photo && values.photo.length > 0;
      const hasDocuments = values.documents && values.documents.length > 0;
      
      // Создаем объект с данными сотрудника
      const staffData: Record<string, any> = {
        // Обязательные поля
        first_name: values.first_name,
        last_name: values.last_name,
        email: values.email,
        phone: values.phone, // Уже отформатирован в формате +7 XXX XXX XX XX
        
        // Важное поле position обязательное в бэкенде
        position: values.position_id 
          ? positions.find(pos => pos.id === Number(values.position_id))?.name || 'Должность не указана'
          : 'Должность не указана',
        
        // Опциональные поля, но важные для создания сотрудника
        middle_name: values.middle_name || null,
        
        // Числовые поля - явно преобразуем к number и проверяем на NaN
        organization_id: values.organization_id ? 
          (isNaN(Number(values.organization_id)) ? null : Number(values.organization_id)) : null,
        
        primary_organization_id: values.primary_organization_id ? 
          (isNaN(Number(values.primary_organization_id)) ? null : Number(values.primary_organization_id)) : 
          (values.organization_id ? (isNaN(Number(values.organization_id)) ? null : Number(values.organization_id)) : null),
        
        location_id: values.location_id ? 
          (isNaN(Number(values.location_id)) ? null : Number(values.location_id)) : null,
        
        // Преобразуем структурированные адреса в единые строки
        registration_address: formatAddress(values.reg_address),
        actual_address: formatAddress(values.act_address),
        
        // Дополнительные поля
        telegram_id: values.telegram_id || null,
        vk: values.vk || null,
        instagram: values.instagram || null,
        description: values.description || null,
        
        // Boolean значения
        is_active: Boolean(values.is_active),
      };
      
      // Функция для форматирования адреса
      function formatAddress(addressObj: any): string | null {
        if (!addressObj) return null;
        
        const { index, city, street, house, building, apartment } = addressObj;
        
        // Проверяем наличие обязательных полей
        if (!index || !city || !street || !house) {
          console.error('[LOG:Staff] Ошибка при форматировании адреса: не все обязательные поля заполнены', {
            index, city, street, house
          });
          throw new Error('Не все обязательные поля адреса заполнены. Пожалуйста, проверьте адресные данные.');
        }
        
        // Форматируем в соответствии с требованиями
        let result = `${index}, ${city}, ул. ${street}, д. ${house}`;
        
        if (building) {
          result += `, корп. ${building}`;
        }
        
        if (apartment) {
          result += `, кв./офис ${apartment}`;
        }
        
        console.log('[LOG:Staff] Отформатированный адрес:', result);
        return result;
      }
      
      // Исправлено: проверяем, что объект не null и не undefined перед вызовом Object.keys
      if (staffData) {
        // Удаляем null значения
        Object.keys(staffData).forEach(key => {
          if (staffData[key] === null || staffData[key] === undefined) {
            delete staffData[key];
          }
        });
      }
      
      console.log('[LOG:Staff] Подготовленные данные для отправки:', staffData);
      console.log('[LOG:Staff] Наличие фото:', hasPhoto);
      console.log('[LOG:Staff] Наличие документов:', hasDocuments);
      
      // Если есть файлы, используем FormData
      if (hasPhoto || hasDocuments) {
        // Добавляем все поля данных в FormData
        Object.keys(staffData).forEach(key => {
          formData.append(key, staffData[key]);
        });
        
        // Добавляем фото, если есть
        if (hasPhoto) {
          const photoFile = values.photo[0].originFileObj;
          formData.append('photo', photoFile);
          console.log('[LOG:Staff] Прикрепляем фото:', photoFile.name);
        }
        
        // Добавляем документы, если есть
        if (hasDocuments) {
          values.documents.forEach((doc: any, index: number) => {
            const docFile = doc.originFileObj;
            formData.append(`document_${index}`, docFile);
            console.log(`[LOG:Staff] Прикрепляем документ ${index + 1}:`, docFile.name);
          });
          
          // Добавляем количество документов
          formData.append('document_count', String(values.documents.length));
        }
      }
      
      try {
        let response;
        
        if (editingItem) {
          // Обновление
          if (hasPhoto || hasDocuments) {
            console.log(`[LOG:Staff] Отправляем PUT запрос с файлами на /staff/${editingItem.id}/with-files`);
            response = await api.put(`/staff/${editingItem.id}/with-files`, formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });
          } else {
            console.log(`[LOG:Staff] Отправляем PUT запрос (JSON) на /staff/${editingItem.id}`);
            response = await api.put(`/staff/${editingItem.id}`, staffData);
          }
          
          console.log('[LOG:Staff] Успешный ответ:', response);
          message.success('Сотрудник успешно обновлен');
          
          // Обновляем local state немедленно
          const updatedStaff = staff.map(item => 
            item.id === editingItem.id ? { ...item, ...staffData } : item
          );
          setStaff(updatedStaff);
        } else {
          // Создание
          if (hasPhoto || hasDocuments) {
            console.log('[LOG:Staff] Отправляем POST запрос с файлами на /staff/with-files');
            response = await api.post('/staff/with-files', formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            });
          } else {
            console.log('[LOG:Staff] Отправляем POST запрос (JSON) на /staff');
            response = await api.post('/staff', staffData);
          }
          
          console.log('[LOG:Staff] Успешный ответ:', response);
          message.success('Сотрудник успешно создан');
          
          // Добавляем созданного сотрудника в массив немедленно
          if (response.data && response.data.id) {
            const newStaff = [...staff, response.data];
            setStaff(newStaff);
            console.log('[LOG:Staff] Сотрудник добавлен в локальный массив:', response.data);
          }
        }
        
        setIsModalVisible(false);
        setEditingItem(null);
        
        // Принудительно обновляем данные с задержкой для уверенности
        setTimeout(() => {
          console.log('[LOG:Staff] Первое принудительное обновление данных после сохранения');
          fetchData();
          
          // Двойное обновление с разными задержками для надежности
          setTimeout(() => {
            console.log('[LOG:Staff] Второе принудительное обновление данных после сохранения');
            fetchData();
            
            // РАДИКАЛЬНОЕ РЕШЕНИЕ: принудительная перезагрузка страницы
            setTimeout(() => {
              console.log('[LOG:Staff] ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ СТРАНИЦЫ');
              window.location.reload();
            }, 500);
          }, 500);
        }, 200);
      } catch (apiError: any) {
        console.error('[LOG:Staff] Ошибка API при сохранении:', apiError);
        
        let errorMessage = 'Ошибка при сохранении';
        
        if (apiError.response) {
          console.error('[LOG:Staff] Статус ответа:', apiError.response.status);
          console.error('[LOG:Staff] Данные ответа:', apiError.response.data);
          
          // Обработка ошибок валидации FastAPI
          if (apiError.response.data?.detail) {
            if (Array.isArray(apiError.response.data.detail)) {
              errorMessage = apiError.response.data.detail
                .map((e: any) => `${e.loc.length > 1 ? e.loc[1] : 'field'}: ${e.msg}`)
                .join('; ');
            } else if (typeof apiError.response.data.detail === 'string') {
              errorMessage = apiError.response.data.detail;
            }
          }
          
          // Добавляем код ответа в сообщение об ошибке
          errorMessage = `Ошибка ${apiError.response.status}: ${errorMessage}`;
        } else if (apiError.request) {
          console.error('[LOG:Staff] Запрос был сделан, но ответ не получен:', apiError.request);
          
          // Сервер может не обрабатывать запросы с файлами
          // Попробуем сохранить без файлов
          if (hasPhoto || hasDocuments) {
            message.warning('Сервер может не поддерживать загрузку файлов. Попробуем сохранить без файлов...');
            
            try {
              console.log('[LOG:Staff] Пробуем отправить запрос без файлов');
              
              if (editingItem) {
                // Обновление без файлов
                const response = await api.put(`/staff/${editingItem.id}`, staffData);
                console.log('[LOG:Staff] Успешный ответ (без файлов):', response);
                message.success('Сотрудник обновлен, но без загрузки файлов');
                
                // Обновляем local state
                const updatedStaff = staff.map(item => 
                  item.id === editingItem.id ? { ...item, ...staffData } : item
                );
                setStaff(updatedStaff);
              } else {
                // Создание без файлов
                const response = await api.post('/staff', staffData);
                console.log('[LOG:Staff] Успешный ответ (без файлов):', response);
                message.success('Сотрудник создан, но без загрузки файлов');
                
                // Добавляем созданного сотрудника в массив
                if (response.data && response.data.id) {
                  const newStaff = [...staff, response.data];
                  setStaff(newStaff);
                }
              }
              
              setIsModalVisible(false);
              setEditingItem(null);
              
              // Обновляем данные
              setTimeout(() => fetchData(), 300);
              
              return; // Выходим, чтобы не показывать сообщение об ошибке
            } catch (secondError) {
              console.error('[LOG:Staff] Ошибка при повторной попытке без файлов:', secondError);
              errorMessage = 'Сервер не отвечает. Проверьте подключение и попробуйте позже.';
            }
          } else {
            errorMessage = 'Сервер не отвечает. Проверьте подключение.';
          }
        } else {
          console.error('[LOG:Staff] Ошибка настройки запроса:', apiError.message);
          errorMessage = apiError.message;
        }
        
        message.error(errorMessage);
        
        // В случае ошибки API, создаем объект локально как временное решение
        if (!editingItem) {
          console.log('[LOG:Staff] ВРЕМЕННОЕ РЕШЕНИЕ: Создаю сотрудника локально');
          
          // Создаем локальный объект с временным ID 
          const tempStaff: Staff = {
            ...staffData,
            id: Math.floor(Math.random() * -1000) - 1, // Отрицательный ID
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            // Обязательные поля из интерфейса Staff
            email: staffData.email || 'temp@example.com',
            first_name: staffData.first_name || 'Имя',
            last_name: staffData.last_name || 'Фамилия',
            is_active: Boolean(staffData.is_active)
          };
          
          // Добавляем в state
          const newStaff = [...staff, tempStaff];
          setStaff(newStaff);
          
          message.warning('Сотрудник создан локально (временный режим)');
          console.log('[LOG:Staff] Сотрудник добавлен в локальный массив (временно):', tempStaff);
          
          setIsModalVisible(false);
        }
      }
    } catch (validationError) {
      console.error('[LOG:Staff] Ошибка валидации формы:', validationError);
      
      // Анализ ошибок валидации для показа конкретных сообщений
      const errors = (validationError as any).errorFields || [];
      
      // Создаем подробное сообщение об ошибках
      if (errors.length > 0) {
        // Словарь для перевода имен полей на русский
        const fieldNames: Record<string, string> = {
          'first_name': 'Имя',
          'last_name': 'Фамилия',
          'email': 'Email',
          'phone': 'Телефон',
          'position_id': 'Должность',
          'organization_id': 'Организация',
          'reg_address.index': 'Индекс (адрес регистрации)',
          'reg_address.city': 'Город (адрес регистрации)',
          'reg_address.street': 'Улица (адрес регистрации)',
          'reg_address.house': 'Дом (адрес регистрации)',
          'act_address.index': 'Индекс (фактический адрес)',
          'act_address.city': 'Город (фактический адрес)',
          'act_address.street': 'Улица (фактический адрес)',
          'act_address.house': 'Дом (фактический адрес)',
        };
        
        // Группируем ошибки по категориям
        const basicInfoErrors: string[] = [];
        const organizationErrors: string[] = [];
        const addressErrors: string[] = [];
        const telegramErrors: string[] = []; // Добавляем массив для ошибок Telegram
        
        // Анализируем ошибки и распределяем их по группам
        errors.forEach((error: any) => {
          const fieldPath = Array.isArray(error.name) ? error.name.join('.') : error.name;
          const fieldName = fieldNames[fieldPath] || fieldPath;
          const errorMessage = `${fieldName}: ${error.errors[0]}`;
          
          // Распределяем по категориям для понимания на какой вкладке ошибка
          if (fieldPath.includes('reg_address') || fieldPath.includes('act_address')) {
            addressErrors.push(errorMessage);
          } else if (fieldPath === 'organization_id' || fieldPath === 'location_id') {
            organizationErrors.push(errorMessage);
          } else if (fieldPath === 'telegram_id') { // Добавляем проверку для telegram_id
            telegramErrors.push(errorMessage);
          } else {
            basicInfoErrors.push(errorMessage);
          }
        });
        
        // Переключаемся на нужную вкладку в зависимости от типа ошибок
        const tabsElement = document.querySelector('.ant-tabs-nav-list');
        
        // Определяем, на какую вкладку переключиться
        if (addressErrors.length > 0) {
          // Вкладка "Адресная информация"
          const addressTab = tabsElement?.querySelectorAll('.ant-tabs-tab')[3];
          if (addressTab) {
            (addressTab as HTMLElement).click();
          }
          
          // Выводим подробные сообщения для адресов
          message.error({
            content: (
              <div>
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  Заполните следующие обязательные поля адреса:
                </div>
                <ul style={{ paddingLeft: '20px', margin: 0 }}>
                  {addressErrors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            ),
            duration: 7,
            style: { marginTop: '20px' }
          });
        } else if (organizationErrors.length > 0) {
          // Вкладка "Информация об организации"
          const orgTab = tabsElement?.querySelectorAll('.ant-tabs-tab')[1];
          if (orgTab) {
            (orgTab as HTMLElement).click();
          }
          
          // Выводим подробные сообщения для организации
          message.error({
            content: (
              <div>
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  Заполните следующие обязательные поля организации:
                </div>
                <ul style={{ paddingLeft: '20px', margin: 0 }}>
                  {organizationErrors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            ),
            duration: 7,
            style: { marginTop: '20px' }
          });
        } else if (basicInfoErrors.length > 0) {
          // Вкладка "Основная информация"
          const basicTab = tabsElement?.querySelectorAll('.ant-tabs-tab')[0];
          if (basicTab) {
            (basicTab as HTMLElement).click();
          }
          
          // Выводим подробные сообщения для основной информации
          message.error({
            content: (
              <div>
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  Заполните следующие обязательные поля:
                </div>
                <ul style={{ paddingLeft: '20px', margin: 0 }}>
                  {basicInfoErrors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            ),
            duration: 7,
            style: { marginTop: '20px' }
          });
        } else if (telegramErrors.length > 0) { // Добавляем обработку ошибок Telegram
          // Вкладка "Социальные сети"
          const socialTab = tabsElement?.querySelectorAll('.ant-tabs-tab')[2];
          if (socialTab) {
            (socialTab as HTMLElement).click();
          }
          
          // Выводим подробные сообщения для Telegram ID
          message.error({
            content: (
              <div>
                <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                  Заполните следующие обязательные поля:
                </div>
                <ul style={{ paddingLeft: '20px', margin: 0 }}>
                  {telegramErrors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            ),
            duration: 7,
            style: { marginTop: '20px' }
          });
        } else {
          // Общее сообщение, если категорию определить не удалось
          message.error('Пожалуйста, проверьте правильность заполнения полей формы');
        }
      } else {
        // Общее сообщение, если список ошибок пуст
        message.error('Некоторые поля заполнены некорректно. Пожалуйста, проверьте форму.');
      }
    } finally {
      setModalLoading(false);
    }
  };

  // Обработчик двойного клика по строке таблицы
  const handleRowDoubleClick = (record: Staff) => {
    console.log('[LOG:Staff] Открытие детальной карточки сотрудника:', record);
    setSelectedStaff(record);
    setIsDetailModalVisible(true);
  };

  // Столбцы таблицы
  const columns = [
    {
      title: 'ФИО',
      key: 'fullname',
      sorter: (a: Staff, b: Staff) => {
        const getFullName = (staff: Staff) => 
          `${staff.last_name || ''} ${staff.first_name || ''} ${staff.middle_name || ''}`.trim();
        return getFullName(a).localeCompare(getFullName(b));
      },
      defaultSortOrder: 'ascend' as SortOrder, // Добавляем сортировку по умолчанию
      render: (text: any, record: Staff) => {
        const fullName = [record.last_name, record.first_name, record.middle_name]
          .filter(Boolean) // Удаляем пустые значения
          .join(' ');
        
        const nameDisplay = fullName || 'Имя не указано';
        
        return (
          <Tooltip title={`ID: ${record.id}`}>
            <span style={{ fontWeight: 500 }}>{nameDisplay}</span>
            {!record.is_active && (
              <Tag color="red" style={{ marginLeft: 8 }}>Неактивен</Tag>
            )}
          </Tooltip>
        );
      },
    },
    {
      title: 'Должность',
      dataIndex: 'position',
      key: 'position',
      width: '20%',
      render: (position: string) => position || 'Не указана',
    },
    {
      title: 'Организация',
      key: 'organization',
      width: '20%',
      render: (text: any, record: Staff) => {
        const org = organizations.find(o => o.id === record.organization_id);
        return org ? org.name : 'Не указана';
      },
    },
    {
      title: 'Контакты',
      key: 'contacts',
      width: '25%',
      render: (text: any, record: Staff) => {
        const email = record.email ? (
          <div>
            <MailOutlined style={{ marginRight: 5 }} />
            <a href={`mailto:${record.email}`}>{record.email}</a>
          </div>
        ) : null;

        const phone = record.phone ? (
          <div>
            <PhoneOutlined style={{ marginRight: 5 }} />
            <a href={`tel:${record.phone}`}>{record.phone}</a>
          </div>
        ) : null;

        const telegram = record.telegram_id ? (
          <div>
            <span role="img" aria-label="telegram" style={{ marginRight: 5 }}>📱</span>
            <a href={`https://t.me/${record.telegram_id.replace('@', '')}`} target="_blank" rel="noopener noreferrer">
              {record.telegram_id}
            </a>
          </div>
        ) : null;

        return (
          <div style={{ fontSize: '0.9em' }}>
            {email}
            {phone}
            {telegram}
            {!email && !phone && !telegram && "Контакты не указаны"}
          </div>
        );
      },
    },
    {
      title: 'Действия',
      key: 'action',
      width: '15%',
      render: (text: any, record: Staff) => (
        <Space size="middle">
          <Button 
            icon={<EditOutlined />} 
            onClick={() => handleOpenModal(record)}
            type="text"
          />
          <Popconfirm
            title="Вы уверены, что хотите удалить этого сотрудника?"
            onConfirm={() => handleDelete(record.id)}
            okText="Да"
            cancelText="Нет"
            okButtonProps={{ danger: true }}
          >
            <Button 
              icon={<DeleteOutlined />} 
              type="text"
              danger
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // Функция для обработки файлов в компоненте Upload
  const normFile = (e: any) => {
    if (Array.isArray(e)) {
      return e;
    }
    return e?.fileList;
  };

  // CSS стили для подсветки строк таблицы при наведении
  const tableRowStyles = `
    .clickable-row:hover {
      background-color: #2f2f37 !important; // Чуть более светлый фон при наведении
      cursor: pointer;
    }
  `;

  return (
    <div style={{ padding: '24px' }}>
      <style>{tableRowStyles}</style> { /* Добавляем стили */ }
      <Title level={3}>Сотрудники компании</Title>
      
      <Space style={{ marginBottom: 16 }}>
        <CultNeumorphButton 
          intent="primary"
          onClick={() => handleOpenModal()} 
          className="action-button add-button"
          disabled={!apiStatus.connected}
          size="medium" // Укажем размер явно, т.к. он по умолчанию medium
        >
          <PlusOutlined style={{ marginRight: '8px' }} /> {/* Иконка как children */}
          Добавить сотрудника
        </CultNeumorphButton>
        <CultNeumorphButton
          intent="default" // Используем intent="default"
          onClick={fetchData}
          loading={tableLoading}
          className="action-button refresh-button"
          disabled={!apiStatus.connected}
          size="medium"
        >
          <ReloadOutlined style={{ marginRight: '8px' }} /> {/* Иконка как children */}
          Обновить
        </CultNeumorphButton>
        <CultNeumorphButton
          intent={apiStatus.connected ? "default" : "danger"} // Меняем intent
          onClick={checkConnection} 
          loading={apiStatus.checking}
          className={!apiStatus.connected ? "danger-connection-button" : ""}
          size="medium"
        >
          {apiStatus.connected 
            ? <ApiOutlined style={{ marginRight: '8px' }} /> 
            : <DisconnectOutlined style={{ marginRight: '8px' }} /> 
          } {/* Иконка как children */}
          {apiStatus.connected ? 'Проверить связь' : 'Переподключиться'}
        </CultNeumorphButton>
      </Space>
      
      {!apiStatus.connected && (
        <Alert
          message="Проблема с подключением"
          description={apiStatus.message}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
          action={
            <CultNeumorphButton intent="danger" size="small" onClick={checkConnection} loading={apiStatus.checking}>
              Повторить
            </CultNeumorphButton>
          }
        />
      )}
      
      <Card variant="borderless" style={{ boxShadow: 'none', backgroundColor: '#1A1A20' }}>
        {staff.length > 0 ? (
          <Table 
            columns={columns} 
            dataSource={filteredStaff} 
            rowKey="id" 
            loading={tableLoading}
            pagination={{ pageSize: 10 }}
            scroll={{ x: 'max-content' }}
            style={{ background: 'transparent' }}
            className="clean-table"
            rowClassName={(record, index) => {
              const baseClass = index % 2 === 0 ? 'table-row-dark' : 'table-row-light';
              return `${baseClass} clickable-row`; // Добавляем класс для кликабельности
            }}
            onRow={(record) => {
              return {
                onClick: (event) => {
                  console.log('[LOG:Staff] Клик по строке:', record);
                  setSelectedStaff(record);
                  setIsDetailModalVisible(true);
                }, // Клик для открытия детальной информации
                // onDoubleClick: (event) => {}, // Можно добавить и двойной клик, если нужно
                // onContextMenu: (event) => {}, // Правый клик
                // onMouseEnter: (event) => {}, // Наведение мыши
                // onMouseLeave: (event) => {}, // Увод мыши
              };
            }}
          />
        ) : apiStatus.checking ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>Загрузка данных...</p>
          </div>
        ) : (
          <Result
            status="warning"
            title="Нет данных для отображения"
            subTitle={tableLoading ? "Загрузка..." : "Не удалось загрузить список сотрудников. Попробуйте обновить страницу."}
            extra={
              <CultNeumorphButton intent="primary" onClick={fetchData} loading={tableLoading}>
                 <ReloadOutlined style={{ marginRight: '8px' }} /> {/* Иконка как children */}
                Обновить данные
              </CultNeumorphButton>
            }
          />
        )}
      </Card>

      {/* Модальное окно для создания/редактирования */}
      <Modal
        title={editingItem ? "Редактирование сотрудника" : "Создать сотрудника"}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingItem(null);
          form.resetFields(); // Сбрасываем форму при закрытии
        }}
        footer={[
          <CultNeumorphButton key="cancel" intent="secondary" onClick={() => setIsModalVisible(false)}>
            Отмена
          </CultNeumorphButton>,
          <CultNeumorphButton 
            key="submit" 
            intent="primary" 
            loading={modalLoading}
            onClick={handleSave}
          >
            {editingItem ? 'Сохранить' : 'Создать'}
          </CultNeumorphButton>,
        ]}
        width={800}
        destroyOnClose={true}
        maskClosable={false}
        className="staff-modal" 
      >
        <Spin spinning={modalLoading}>
          {/* Убираем ненужную проверку !form */}
          {/* {!form ? ( ... ) : ( */} 
            <Form
              form={form}
              layout="vertical"
              name="staffForm"
              onFinish={handleSave}
            >
              {/* Рефакторинг Tabs на использование items */}
              <Tabs defaultActiveKey="basic" items={[
                {
                  key: 'basic',
                  label: 'Основная информация',
                  children: (
                    <>
                      <Row gutter={16}>
                        <Col span={8}>
                          <Form.Item
                            name="last_name"
                            label="Фамилия"
                            rules={[{ required: true, message: 'Введите фамилию' }]}
                          >
                            <Input placeholder="Фамилия" />
                          </Form.Item>
                        </Col>
                        <Col span={8}>
                          <Form.Item
                            name="first_name"
                            label="Имя"
                            rules={[{ required: true, message: 'Введите имя' }]}
                          >
                            <Input placeholder="Имя" />
                          </Form.Item>
                        </Col>
                        <Col span={8}>
                          <Form.Item name="middle_name" label="Отчество">
                            <Input placeholder="Отчество" />
                          </Form.Item>
                        </Col>
                      </Row>
                      {/* ... остальные поля вкладки "Основная информация" ... */}
                      <Row gutter={16}>
                        <Col span={8}>
                          <Form.Item
                            name="email"
                            label="Email"
                            rules={[
                              { required: true, message: 'Введите email' },
                              { type: 'email', message: 'Введите корректный email' }
                            ]}
                          >
                            <Input placeholder="email@example.com" />
                          </Form.Item>
                        </Col>
                        <Col span={8}>
                          <Form.Item
                            name="phone"
                            label="Телефон"
                            rules={[
                              { required: false, message: 'Введите телефон' },
                              { pattern: /^\+7 \d{3} \d{3} \d{2} \d{2}$/, message: 'Формат: +7 XXX XXX XX XX' }
                            ]}
                          >
                            <Input 
                              placeholder="+7 XXX XXX XX XX" 
                              onChange={handlePhoneChange}
                            />
                          </Form.Item>
                        </Col>
                        <Col span={8}>
                          <Form.Item
                            name="position_id"
                            label="Должность"
                            rules={[{ required: true, message: 'Выберите должность' }]}
                          >
                            <Select placeholder="Выберите должность">
                              {positions.map(position => (
                                <Option key={position.id} value={position.id}>
                                  {position.name}
                                </Option>
                              ))}
                            </Select>
                          </Form.Item>
                        </Col>
                      </Row>
                      <Row gutter={16}>
                        <Col span={12}>
                          <Form.Item 
                            name="photo" 
                            label="Фотография"
                            valuePropName="fileList"
                            getValueFromEvent={normFile}
                          >
                            <Upload 
                              name="photo"
                              listType="picture-card"
                              beforeUpload={() => false}
                              maxCount={1}
                            >
                              <div>
                                <PlusOutlined />
                                <div style={{ marginTop: 8 }}>Загрузить</div>
                              </div>
                            </Upload>
                          </Form.Item>
                        </Col>
                        <Col span={12}>
                          <Form.Item 
                            name="documents" 
                            label="Документы"
                            valuePropName="fileList"
                            getValueFromEvent={normFile}
                          >
                            <Upload 
                              name="documents"
                              multiple
                              beforeUpload={() => false}
                            >
                              <CultNeumorphButton intent="secondary">
                                <UploadOutlined style={{ marginRight: '8px' }} />
                                Загрузить документы
                              </CultNeumorphButton>
                            </Upload>
                          </Form.Item>
                        </Col>
                      </Row>
                    </>
                  )
                },
                {
                  key: 'organization',
                  label: 'Информация об организации',
                  children: (
                    <>
                      <Row gutter={16}>
                        {/* 1. Основная организация */}
                        <Col span={8}>
                          <Form.Item
                            name="primary_organization_id"
                            label="Основная организация (Холдинг)"
                            // Можно добавить правила валидации, если нужно
                          >
                            <Select 
                              placeholder="Выберите холдинг"
                              allowClear
                            >
                              {organizations
                                .map(org => (
                                  <Option 
                                    key={org.id} 
                                    value={org.id}
                                  >
                                    {org.name}
                                  </Option>
                              ))}
                            </Select>
                          </Form.Item>
                        </Col>
                        {/* 2. Организация */}
                        <Col span={8}>
                          <Form.Item
                            name="organization_id"
                            label="Организация (Юр. лицо)"
                            rules={[{ required: true, message: 'Выберите организацию' }]}
                          >
                            <Select 
                              placeholder="Выберите юр. лицо"
                            >
                              {organizations
                                .map(org => (
                                  <Option 
                                    key={org.id} 
                                    value={org.id}
                                  >
                                    {org.name}
                                  </Option>
                              ))}
                            </Select>
                          </Form.Item>
                        </Col>
                        {/* 3. Локация */}
                        <Col span={8}>
                          <Form.Item
                            name="location_id"
                            label="Локация"
                            // Можно сделать обязательным, если нужно
                          >
                            <Select 
                              placeholder="Выберите локацию"
                              allowClear
                            >
                              {organizations
                                .map(org => (
                                  <Option 
                                    key={org.id} 
                                    value={org.id}
                                  >
                                    {org.name}
                                  </Option>
                              ))}
                              {/* Можно также показывать локации из отдельного списка, если он есть */}
                              {locations && locations.map(loc => (
                                <Option key={`loc-${loc.id}`} value={loc.id}>
                                  {loc.name} (Локация)
                                </Option>
                              ))}
                            </Select>
                          </Form.Item>
                        </Col>
                      </Row>
                    </>
                  )
                },
                {
                  key: 'social',
                  label: 'Социальные сети',
                  children: (
                    <>
                      <Row gutter={16}>
                        <Col span={8}>
                          <Form.Item 
                            name="telegram_id" 
                            label="Telegram ID"
                            rules={[{ required: true, message: 'Введите Telegram ID' }]} // Делаем обязательным
                          >
                            <Input placeholder="@username" />
                          </Form.Item>
                        </Col>
                        <Col span={8}>
                          <Form.Item name="vk" label="ВКонтакте">
                            <Input placeholder="https://vk.com/id..." />
                          </Form.Item>
                        </Col>
                        <Col span={8}>
                          <Form.Item name="instagram" label="Instagram">
                            <Input placeholder="@username" />
                          </Form.Item>
                        </Col>
                      </Row>
                    </>
                  )
                },
                {
                  key: 'address',
                  label: 'Адресная информация',
                  children: (
                    <>
                      <Alert
                        message="Важно: Адресные данные обязательны!"
                        description="Для создания сотрудника необходимо указать полный адрес регистрации и фактический адрес (индекс, город, улица, дом). Без этих данных сотрудник не будет создан."
                        type="warning"
                        showIcon
                        style={{ marginBottom: 16 }}
                      />
                      <Divider orientation="left">Адрес регистрации</Divider>
                      <Row gutter={16}>
                        <Col span={6}>
                          <Form.Item 
                            name={['reg_address', 'index']} 
                            label="Индекс"
                            rules={[{ required: true, message: 'Введите индекс' }]}
                          >
                            <Input placeholder="123456" />
                          </Form.Item>
                        </Col>
                        <Col span={6}>
                          <Form.Item 
                            name={['reg_address', 'city']} 
                            label="Город"
                            rules={[{ required: true, message: 'Введите город' }]}
                          >
                            <Input placeholder="Москва" />
                          </Form.Item>
                        </Col>
                        <Col span={6}>
                          <Form.Item 
                            name={['reg_address', 'street']} 
                            label="Улица"
                            rules={[{ required: true, message: 'Введите улицу' }]}
                          >
                            <Input placeholder="Ленина" />
                          </Form.Item>
                        </Col>
                        <Col span={6}>
                          <Form.Item 
                            name={['reg_address', 'house']} 
                            label="Дом"
                            rules={[{ required: true, message: 'Введите номер дома' }]}
                          >
                            <Input placeholder="10А" />
                          </Form.Item>
                        </Col>
                      </Row>
                      <Row gutter={16}>
                        <Col span={6}>
                          <Form.Item name={['reg_address', 'building']} label="Корпус">
                            <Input placeholder="1" />
                          </Form.Item>
                        </Col>
                        <Col span={6}>
                          <Form.Item name={['reg_address', 'apartment']} label="Квартира/офис">
                            <Input placeholder="42" />
                          </Form.Item>
                        </Col>
                      </Row>
                      
                      <Divider orientation="left">Фактический адрес</Divider>
                      <Row gutter={16}>
                        <Col span={24} style={{ marginBottom: 16 }}>
                          <Form.Item
                            name="same_address"
                            valuePropName="checked"
                            style={{ marginBottom: 0 }}
                          >
                            <Checkbox onChange={(e) => {
                              if (e.target.checked) {
                                // Копируем адрес регистрации в фактический адрес
                                const regAddress = form.getFieldValue('reg_address');
                                form.setFieldsValue({
                                  act_address: { ...regAddress }
                                });
                              }
                            }}>
                              Фактический адрес совпадает с адресом регистрации
                            </Checkbox>
                          </Form.Item>
                        </Col>
                        <Col span={6}>
                          <Form.Item 
                            name={['act_address', 'index']} 
                            label="Индекс"
                            rules={[{ required: true, message: 'Введите индекс' }]}
                          >
                            <Input placeholder="123456" />
                          </Form.Item>
                        </Col>
                        <Col span={6}>
                          <Form.Item 
                            name={['act_address', 'city']} 
                            label="Город"
                            rules={[{ required: true, message: 'Введите город' }]}
                          >
                            <Input placeholder="Москва" />
                          </Form.Item>
                        </Col>
                        <Col span={6}>
                          <Form.Item 
                            name={['act_address', 'street']} 
                            label="Улица"
                            rules={[{ required: true, message: 'Введите улицу' }]}
                          >
                            <Input placeholder="Ленина" />
                          </Form.Item>
                        </Col>
                        <Col span={6}>
                          <Form.Item 
                            name={['act_address', 'house']} 
                            label="Дом"
                            rules={[{ required: true, message: 'Введите номер дома' }]}
                          >
                            <Input placeholder="10А" />
                          </Form.Item>
                        </Col>
                      </Row>
                      <Row gutter={16}>
                        <Col span={6}>
                          <Form.Item name={['act_address', 'building']} label="Корпус">
                            <Input placeholder="1" />
                          </Form.Item>
                        </Col>
                        <Col span={6}>
                          <Form.Item name={['act_address', 'apartment']} label="Квартира/офис">
                            <Input placeholder="42" />
                          </Form.Item>
                        </Col>
                      </Row>
                    </>
                  )
                },
                {
                  key: 'additional',
                  label: 'Дополнительная информация',
                  children: (
                    <>
                      <Row gutter={16}>
                        <Col span={24}>
                          <Form.Item name="description" label="Описание">
                            <Input.TextArea placeholder="Дополнительная информация о сотруднике" rows={4} />
                          </Form.Item>
                        </Col>
                      </Row>
                      <Row gutter={16}>
                        <Col span={8}>
                          <Form.Item
                            name="is_active"
                            label="Статус" // Меняем label на "Статус" для ясности
                            valuePropName="checked"
                            initialValue={true} // Устанавливаем значение по умолчанию
                          >
                            <Switch checkedChildren="Активен" unCheckedChildren="Неактивен" />
                          </Form.Item>
                        </Col>
                      </Row>
                    </>
                  )
                }
              ]} />
            </Form>
          {/* ) */} { /* Закрываем комментирование ненужной проверки */ }
        </Spin>
      </Modal>

      {/* Модальное окно для детальной информации о сотруднике */}
      <Modal
        title="Карточка сотрудника" // Убрали динамическое ФИО
        open={isDetailModalVisible}
        onCancel={() => setIsDetailModalVisible(false)}
        footer={null}
        width={800}
        className="staff-modal"
        centered
      >
        {selectedStaff && (
          <div className="staff-detail">
            {/* Фиолетовая шапка - остается сверху */}
            <div className="staff-detail-header" style={{ padding: '12px 20px' }}>
              <h2>{selectedStaff.last_name} {selectedStaff.first_name} {selectedStaff.middle_name || ''}</h2>
              <p className="staff-subtitle">{positions.find(pos => pos.id === selectedStaff.position_id)?.name || '—'}</p>
            </div>

            {/* Фотография сотрудника - остается сверху */}
            {selectedStaff.photo_path ? (
              <div className="staff-detail-photo-section" style={{ textAlign: 'center', marginBottom: '16px' }}>
                 <img
                   src={selectedStaff.photo_path}
                   alt={`Фото ${selectedStaff.last_name}`}
                   className="staff-photo"
                   style={{ maxWidth: '150px', height: 'auto', borderRadius: '50%', border: '3px solid #4A4A5C' }}
                   onError={(e) => {
                       console.warn(`[LOG:Staff] Не удалось загрузить фото: ${selectedStaff.photo_path}`);
                       (e.target as HTMLImageElement).src = '/placeholder-avatar.png';
                       (e.target as HTMLImageElement).alt = 'Фото не загружено';
                   }}
                 />
              </div>
            ) : (
              <div className="staff-detail-photo-section" style={{ textAlign: 'center', marginBottom: '16px' }}>
                 <UserOutlined style={{ fontSize: '80px', color: '#4A4A5C', border: '3px solid #4A4A5C', borderRadius: '50%', padding: '20px' }} />
               </div>
            )}

            {/* Вкладки с информацией */}
            <Tabs defaultActiveKey="main" className="staff-detail-tabs">
              <Tabs.TabPane tab="Основная информация" key="main">
                <div className="staff-cards-container" style={{ marginTop: '16px' }}>
                    <div className="staff-info-card">
                      <div className="staff-info-card-inner">
                        <p className="staff-info-label">Email</p>
                        <p className="staff-info-value">{selectedStaff.email}</p>
                      </div>
                    </div>
                    <div className="staff-info-card">
                      <div className="staff-info-card-inner">
                        <p className="staff-info-label">Телефон</p>
                        <p className="staff-info-value">{selectedStaff.phone || '—'}</p>
                      </div>
                    </div>
                    <div className="staff-info-card">
                      <div className="staff-info-card-inner">
                        <p className="staff-info-label">Организация (Юр. лицо)</p>
                        <p className="staff-info-value">{organizations.find(org => org.id === selectedStaff.organization_id)?.name || '—'}</p>
                      </div>
                    </div>
                    <div className="staff-info-card"> {/* Добавляем локацию */}
                       <div className="staff-info-card-inner">
                         <p className="staff-info-label">Локация</p>
                         {/* Ищем и в organizations, и в locations, если они есть */}
                         <p className="staff-info-value">
                           {organizations.find(org => org.id === selectedStaff.location_id)?.name || 
                            locations?.find(loc => loc.id === selectedStaff.location_id)?.name || 
                            '—'}
                         </p>
                       </div>
                     </div>
                    <div className="staff-info-card">
                      <div className="staff-info-card-inner">
                        <p className="staff-info-label">Должность</p>
                        <p className="staff-info-value">{positions.find(pos => pos.id === selectedStaff.position_id)?.name || '—'}</p>
                      </div>
                    </div>
                    <div className="staff-info-card"> {/* Добавляем подразделение */}
                       <div className="staff-info-card-inner">
                         <p className="staff-info-label">Подразделение</p>
                         <p className="staff-info-value">{divisions.find(div => div.id === selectedStaff.division_id)?.name || '—'}</p>
                       </div>
                     </div>
                    <div className="staff-info-card">
                      <div className="staff-info-card-inner">
                        <p className="staff-info-label">Статус</p>
                        <p className="staff-info-value">{selectedStaff.is_active ? 'Активен' : 'Неактивен'}</p>
                      </div>
                    </div>
                     <div className="staff-info-card"> {/* Добавляем Telegram ID */}
                       <div className="staff-info-card-inner">
                         <p className="staff-info-label">Telegram ID</p>
                         <p className="staff-info-value">{selectedStaff.telegram_id || '—'}</p>
                       </div>
                     </div>
                  </div>
              </Tabs.TabPane>

              <Tabs.TabPane tab="Адреса" key="address">
                <div style={{ marginTop: '16px' }}>
                  <Row gutter={16}>
                    <Col span={12}>
                      <h4>Адрес регистрации</h4>
                      {(() => { // Используем IIFE для парсинга и отображения
                        const parsedRegAddress = parseAddressToFields(selectedStaff.registration_address as string | null); // Приводим тип к string | null для парсера
                        if (parsedRegAddress) {
                          return (
                            <div className="staff-address-card">
                              <p><strong>Индекс:</strong> {parsedRegAddress.index || '—'}</p>
                              <p><strong>Город:</strong> {parsedRegAddress.city || '—'}</p>
                              <p><strong>Улица:</strong> {parsedRegAddress.street || '—'}</p>
                              <p><strong>Дом:</strong> {parsedRegAddress.house || '—'}</p>
                              {parsedRegAddress.building && <p><strong>Корпус:</strong> {parsedRegAddress.building}</p>}
                              {parsedRegAddress.apartment && <p><strong>Кв./Офис:</strong> {parsedRegAddress.apartment}</p>}
                            </div>
                          );
                        } else {
                          return <p>Нет данных</p>;
                        }
                      })()}
                    </Col>
                    <Col span={12}>
                      <h4>Фактический адрес</h4>
                      {(() => { // Используем IIFE для парсинга и отображения
                        const parsedActAddress = parseAddressToFields(selectedStaff.actual_address as string | null); // Приводим тип к string | null для парсера
                        if (parsedActAddress) {
                          return (
                            <div className="staff-address-card">
                              <p><strong>Индекс:</strong> {parsedActAddress.index || '—'}</p>
                              <p><strong>Город:</strong> {parsedActAddress.city || '—'}</p>
                              <p><strong>Улица:</strong> {parsedActAddress.street || '—'}</p>
                              <p><strong>Дом:</strong> {parsedActAddress.house || '—'}</p>
                              {parsedActAddress.building && <p><strong>Корпус:</strong> {parsedActAddress.building}</p>}
                              {parsedActAddress.apartment && <p><strong>Кв./Офис:</strong> {parsedActAddress.apartment}</p>}
                            </div>
                          );
                        } else {
                          return <p>Нет данных</p>;
                        }
                      })()}
                    </Col>
                  </Row>
                </div>
              </Tabs.TabPane>

              <Tabs.TabPane tab="Документы" key="documents">
                 <div className="staff-description-card" style={{ marginTop: '16px', minHeight: '50px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {/* TODO: Реализовать загрузку и отображение списка документов после доработки бэкенда */}
                    <p style={{ color: '#888' }}>Список документов будет доступен здесь после обновления функционала.</p>
                  </div>
              </Tabs.TabPane>

              <Tabs.TabPane tab="Дополнительно" key="additional">
                 <div style={{ marginTop: '16px' }}>
                  {selectedStaff.description && (
                    <div className="staff-detail-section" style={{ marginBottom: '16px' }}>
                      <h4>Описание</h4>
                      <div className="staff-description-card">
                        <p>{selectedStaff.description}</p>
                      </div>
                    </div>
                  )}
                  <div className="staff-cards-container">
                     <div className="staff-info-card">
                       <div className="staff-info-card-inner">
                         <p className="staff-info-label">Создан</p>
                         <p className="staff-info-value">{new Date(selectedStaff.created_at).toLocaleString()}</p>
                       </div>
                     </div>
                     <div className="staff-info-card">
                       <div className="staff-info-card-inner">
                         <p className="staff-info-label">Обновлен</p>
                         <p className="staff-info-value">{new Date(selectedStaff.updated_at).toLocaleString()}</p>
                       </div>
                     </div>
                   </div>
                 </div>
              </Tabs.TabPane>
            </Tabs>

            {/* Кнопки действий - теперь под вкладками */}
            <div className="staff-detail-actions" style={{ marginTop: '24px' }}>
               {/* ... existing action buttons code ... */}
               <div className="staff-action-buttons">
                 <CultNeumorphButton 
                   intent="primary" 
                   className="staff-button edit-button"
                   onClick={() => {
                     handleOpenModal(selectedStaff);
                     setIsDetailModalVisible(false);
                   }}
                 >
                   <EditOutlined style={{ marginRight: '8px' }} />
                   Редактировать
                 </CultNeumorphButton>
                 
                 <Popconfirm
                   title="Удалить сотрудника?"
                   description={`Вы уверены, что хотите удалить запись №${selectedStaff.id}: "${selectedStaff.last_name} ${selectedStaff.first_name}"?`}
                   onConfirm={async () => {
                     try {
                       setTableLoading(true);
                       await api.delete(`/staff/${selectedStaff.id}`);
                       message.success(`Cотрудник "${selectedStaff.last_name} ${selectedStaff.first_name}" успешно удалён`);
                       setIsDetailModalVisible(false);
                       fetchData(); // Перезагружаем данные
                     } catch (error) {
                       console.error('[LOG:Staff] Ошибка при удалении:', error);
                       message.error('Ошибка при удалении записи сотрудника.');
                       setTableLoading(false);
                     }
                   }}
                   okText="Да, удалить"
                   cancelText="Отмена"
                   okButtonProps={{ danger: true }}
                 >
                   <CultNeumorphButton intent="danger" className="staff-button delete-button">
                     <DeleteOutlined style={{ marginRight: '8px' }} />
                     Удалить
                   </CultNeumorphButton>
                 </Popconfirm>
               </div>
               
               <div className="staff-action-secondary">
                 <CultNeumorphButton intent="secondary" className="staff-button message-button">Отправить сообщение</CultNeumorphButton>
                 <CultNeumorphButton intent="secondary" className="staff-button comment-button">Добавить комментарий</CultNeumorphButton>
                 <CultNeumorphButton intent="secondary" className="staff-button history-button">Просмотреть историю</CultNeumorphButton>
                 <CultNeumorphButton intent="secondary" onClick={() => setIsDetailModalVisible(false)} className="staff-button close-button">Закрыть</CultNeumorphButton>
               </div>
             </div>
          </div>
        )}
      </Modal>

      {/* Фильтры и поиск */}
      <div style={{ 
        background: '#f0f2f5', 
        padding: '16px',
        borderRadius: '4px',
        marginBottom: '16px'
      }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8} md={6}>
            <Input.Search 
              placeholder="Поиск по имени, email, телефону..." 
              value={searchText}
              onChange={e => setSearchText(e.target.value)}
              onSearch={handleSearch}
              allowClear
            />
          </Col>
          <Col xs={24} sm={8} md={5}>
            <Select
              placeholder="Фильтр по организации"
              style={{ width: '100%' }}
              value={filterParams.organization_id}
              onChange={handleOrganizationFilter}
              allowClear
              showSearch
              filterOption={(input, option) =>
                option?.children?.toString().toLowerCase().includes(input.toLowerCase()) || false
              }
            >
              {organizations.map(org => (
                <Select.Option key={org.id} value={org.id}>
                  {org.name}
                </Select.Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={8} md={5}>
            <Select
              placeholder="Фильтр по должности"
              style={{ width: '100%' }}
              value={filterParams.position_id}
              onChange={handlePositionFilter}
              allowClear
              showSearch
              filterOption={(input, option) =>
                option?.children?.toString().toLowerCase().includes(input.toLowerCase()) || false
              }
            >
              {positions.map(pos => (
                <Select.Option key={pos.id} value={pos.id}>
                  {pos.name}
                </Select.Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={8} md={4}>
            <Select
              placeholder="Статус"
              style={{ width: '100%' }}
              value={filterParams.is_active}
              onChange={handleActiveFilter}
              allowClear
            >
              <Select.Option value={true}>Активные</Select.Option>
              <Select.Option value={false}>Неактивные</Select.Option>
            </Select>
          </Col>
          <Col xs={24} sm={8} md={4}>
            <NeoButton 
              icon={<ReloadOutlined />} 
              onClick={resetFilters}
              style={{ marginRight: 8 }}
            >
              Сбросить
            </NeoButton>
            <NeoButton 
              buttonType="primary" 
              icon={<SearchOutlined />} 
              onClick={() => fetchData()}
            >
              Обновить
            </NeoButton>
          </Col>
        </Row>
      </div>
    </div>
  );
};

// !!! Убираем старое предупреждение о переименовании !!!
export default AdminStaffPage; 