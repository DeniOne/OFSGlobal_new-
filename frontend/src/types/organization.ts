/**
 * Типы данных для работы с организационной структурой
 */

// Типы организаций
export enum OrgType {
  BOARD = "board",
  HOLDING = "holding",
  LEGAL_ENTITY = "legal_entity",
  LOCATION = "location"
}

// Организация
export interface Organization {
  id: number;
  name: string;
  code: string;
  description?: string;
  org_type: OrgType;
  is_active: boolean;
  parent_id?: number | null;
  ckp?: string;
  inn?: string;
  kpp?: string;
  legal_address?: string;
  physical_address?: string;
  created_at: string;
  updated_at: string;
  
  // Дополнительные поля для UI
  children?: Organization[];
}

// Отдел/дивизион
export interface Division {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  organization_id: number;
  parent_id?: number | null;
  ckp?: string;
  created_at: string;
  updated_at: string;
  
  // Дополнительные поля для UI
  children?: Division[];
  hasChildren?: boolean;
}

// Отдел
export interface Section {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  ckp?: string;
  created_at: string;
  updated_at: string;
}

// Связь Division-Section
export interface DivisionSection {
  id: number;
  division_id: number;
  section_id: number;
  is_primary: boolean;
  created_at: string;
}

// Функция
export interface Function {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Связь Section-Function
export interface SectionFunction {
  id: number;
  section_id: number;
  function_id: number;
  is_primary: boolean;
  created_at: string;
}

// Должность
export interface Position {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  function_id?: number | null;
  created_at: string;
  updated_at: string;
}

// Тип функциональной связи
export enum RelationType {
  FUNCTIONAL = 'functional',
  ADMINISTRATIVE = 'administrative',
  PROJECT = 'project',
  TERRITORIAL = 'territorial',
  MENTORING = 'mentoring',
  STRATEGIC = 'strategic',
  GOVERNANCE = 'governance'
}

// Функциональная связь
export interface FunctionalRelation {
  id: number;
  manager_id: number;
  subordinate_id: number;
  relation_type: RelationType;
  description?: string;
  is_active: boolean;
  start_date: string;
  end_date?: string;
  extra_field1?: string;
  created_at: string;
  updated_at: string;
  
  // Дополнительные поля для UI
  manager_name?: string;
  subordinate_name?: string;
}

// Интерфейс для структурированного адреса
export interface Address {
  index?: string | null;
  city?: string | null;
  street?: string | null;
  house?: string | null;
  building?: string | null;
  apartment?: string | null;
  // Можно добавить строковое представление, если нужно
  full_address?: string | null; 
}

// Сотрудник
export interface Staff {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone?: string;
  description?: string;
  is_active: boolean;
  organization_id?: number | null;
  primary_organization_id?: number | null;
  created_at: string;
  updated_at: string;
  
  // Добавляем недостающие поля, используемые в UI
  registration_address?: Address | null;
  actual_address?: Address | null;
  photo_path?: string | null;
  telegram_id?: string | null;
  position_id?: number | null; // Хотя может быть в positions
  division_id?: number | null; // Хотя может быть в positions
  location_id?: number | null; // Хотя может быть в locations/positions
  vk?: string | null; // Добавляем VK
  instagram?: string | null; // Добавляем Instagram
  
  // Дополнительные поля для UI
  full_name?: string;
  positions?: StaffPosition[];
  locations?: StaffLocation[];
  functions?: StaffFunction[];
  managers?: FunctionalRelation[];
  subordinates?: FunctionalRelation[];
}

// Связь Сотрудника и Должности
export interface StaffPosition {
  id: number;
  staff_id: number;
  position_id: number;
  division_id?: number | null;
  location_id?: number | null;
  is_primary: boolean;
  is_active: boolean;
  start_date: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
  
  // Дополнительные поля для UI
  position_name?: string;
  division_name?: string;
}

// Связь Сотрудника и Локации
export interface StaffLocation {
  id: number;
  staff_id: number;
  location_id: number;
  is_current: boolean;
  date_from: string;
  date_to?: string;
  created_at: string;
  updated_at: string;
  
  // Дополнительные поля для UI
  location_name?: string;
}

// Связь Сотрудника и Функции
export interface StaffFunction {
  id: number;
  staff_id: number;
  function_id: number;
  commitment_percent: number;
  is_primary: boolean;
  date_from: string;
  date_to?: string;
  created_at: string;
  updated_at: string;
  
  // Дополнительные поля для UI
  function_name?: string;
}

// Узел организационной структуры (для иерархического отображения)
export interface OrgStructureNode {
  id: number;
  name: string;
  code: string;
  entity_type: 'organization' | 'division' | 'section' | 'function';
  org_type?: string;
  children: OrgStructureNode[];
}

// Узел сотрудника (для иерархического отображения)
export interface StaffNode {
  id: number;
  name: string;
  position: string;
  email?: string;
  relations: {
    id: number;
    manager_id: number;
    manager_name: string;
    relation_type: RelationType;
    description?: string;
  }[];
  children: StaffNode[];
}

// Матричное отношение между сотрудниками
export interface MatrixRelation {
  id: number;
  from_id: number;
  to_id: number;
  from_name: string;
  to_name: string;
  relation_type: RelationType;
  description?: string;
  extra_info?: string;
} 