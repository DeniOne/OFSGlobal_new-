import { EntityNode, EntityRelation } from '../components/organization/types';

// Бизнес структура
export const mockBusinessNodes: EntityNode[] = [
  {
    id: 'node_1',
    name: 'Генеральный директор',
    position: 'CEO',
    type: 'business',
    manager: '',
    avatar: '',
  },
  {
    id: 'node_2',
    name: 'Финансовый директор',
    position: 'CFO',
    type: 'business',
    manager: 'Генеральный директор',
    avatar: '',
  },
  {
    id: 'node_3',
    name: 'Технический директор',
    position: 'CTO',
    type: 'business',
    manager: 'Генеральный директор',
    avatar: '',
  },
  {
    id: 'node_4',
    name: 'Главный бухгалтер',
    position: 'Chief Accountant',
    type: 'business',
    manager: 'Финансовый директор',
    avatar: '',
  },
  {
    id: 'node_5',
    name: 'IT отдел',
    position: 'IT Department',
    type: 'business',
    manager: 'Технический директор',
    avatar: '',
  },
  {
    id: 'node_6',
    name: 'Отдел разработки',
    position: 'Development Team',
    type: 'business',
    manager: 'IT отдел',
    avatar: '',
  },
  {
    id: 'node_7',
    name: 'Финансовый отдел',
    position: 'Finance Department',
    type: 'business',
    manager: 'Финансовый директор',
    avatar: '',
  },
  {
    id: 'node_8',
    name: 'Бухгалтерия',
    position: 'Accounting',
    type: 'business',
    manager: 'Главный бухгалтер',
    avatar: '',
  },
];

export const mockBusinessEdges: EntityRelation[] = [
  {
    id: 'edge_1',
    from: 'node_1',
    to: 'node_2',
    type: 'manager',
  },
  {
    id: 'edge_2',
    from: 'node_1',
    to: 'node_3',
    type: 'manager',
  },
  {
    id: 'edge_3',
    from: 'node_2',
    to: 'node_4',
    type: 'manager',
  },
  {
    id: 'edge_4',
    from: 'node_3',
    to: 'node_5',
    type: 'manager',
  },
  {
    id: 'edge_5',
    from: 'node_5',
    to: 'node_6',
    type: 'manager',
  },
  {
    id: 'edge_6',
    from: 'node_2',
    to: 'node_7',
    type: 'manager',
  },
  {
    id: 'edge_7',
    from: 'node_4',
    to: 'node_8',
    type: 'manager',
  },
  {
    id: 'edge_8',
    from: 'node_5',
    to: 'node_2',
    type: 'functional',
  },
];

// Юридическая структура
export const mockLegalNodes: EntityNode[] = [
  {
    id: 'legal_1',
    name: 'ООО "Главная Компания"',
    position: 'Головная организация',
    type: 'legal',
    manager: '',
    avatar: '',
  },
  {
    id: 'legal_2',
    name: 'ООО "Дочернее предприятие 1"',
    position: '100% владения',
    type: 'legal',
    manager: 'ООО "Главная Компания"',
    avatar: '',
  },
  {
    id: 'legal_3',
    name: 'ООО "Дочернее предприятие 2"',
    position: '75% владения',
    type: 'legal',
    manager: 'ООО "Главная Компания"',
    avatar: '',
  },
  {
    id: 'legal_4',
    name: 'ЗАО "Партнер"',
    position: '50% владения',
    type: 'legal',
    manager: 'ООО "Главная Компания"',
    avatar: '',
  },
];

export const mockLegalEdges: EntityRelation[] = [
  {
    id: 'legal_edge_1',
    from: 'legal_1',
    to: 'legal_2',
    type: 'department',
  },
  {
    id: 'legal_edge_2',
    from: 'legal_1',
    to: 'legal_3',
    type: 'department',
  },
  {
    id: 'legal_edge_3',
    from: 'legal_1',
    to: 'legal_4',
    type: 'department',
  },
];

// Территориальная структура
export const mockTerritorialNodes: EntityNode[] = [
  {
    id: 'territory_1',
    name: 'Головной офис (Москва)',
    position: 'Центральный офис',
    type: 'territorial',
    manager: '',
    avatar: '',
  },
  {
    id: 'territory_2',
    name: 'Офис в Санкт-Петербурге',
    position: 'Региональный офис',
    type: 'territorial',
    manager: 'Головной офис (Москва)',
    avatar: '',
  },
  {
    id: 'territory_3',
    name: 'Офис в Новосибирске',
    position: 'Региональный офис',
    type: 'territorial',
    manager: 'Головной офис (Москва)',
    avatar: '',
  },
  {
    id: 'territory_4',
    name: 'Офис в Екатеринбурге',
    position: 'Региональный офис',
    type: 'territorial',
    manager: 'Головной офис (Москва)',
    avatar: '',
  },
  {
    id: 'territory_5',
    name: 'Представительство в Казани',
    position: 'Представительство',
    type: 'territorial',
    manager: 'Офис в Новосибирске',
    avatar: '',
  },
];

export const mockTerritorialEdges: EntityRelation[] = [
  {
    id: 'territory_edge_1',
    from: 'territory_1',
    to: 'territory_2',
    type: 'department',
  },
  {
    id: 'territory_edge_2',
    from: 'territory_1',
    to: 'territory_3',
    type: 'department',
  },
  {
    id: 'territory_edge_3',
    from: 'territory_1',
    to: 'territory_4',
    type: 'department',
  },
  {
    id: 'territory_edge_4',
    from: 'territory_3',
    to: 'territory_5',
    type: 'department',
  },
]; 