// Типы данных для организационной структуры

// Организация (юрлицо или локация)
export interface Organization {
  id: number;
  name: string;
  description: string;
  parent_id: number | null;
  org_type: 'LEGAL_ENTITY' | 'LOCATION';
  is_active: boolean;
  legal_address?: string;
  physical_address?: string;
  inn?: string;
  kpp?: string;
}

// Структурное подразделение (департамент, отдел, группа)
export interface Division {
  id: number;
  name: string;
  code?: string;
  description: string;
  parent_id: number | null;
  level: number;
  is_active: boolean;
  children?: Division[];
}

// Сотрудник
export interface Staff {
  id: number;
  name: string;
  position: string;
  division: string;
  division_id: number;
  organization_id: number;
  legal_entity_id?: number;
  location_id?: number;
  level: number;
  email?: string;
  phone?: string;
}

// Функциональные связи
export interface FunctionalRelation {
  id: number;
  manager_id: number;
  subordinate_id: number;
  relation_type: 'ADMINISTRATIVE' | 'FUNCTIONAL' | 'PROJECT' | 'TERRITORIAL' | 'MENTORING';
  description?: string;
}

// Данные для визуализаций

// Иерархия (используется для tree layout)
export interface HierarchyNode {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  level?: number;
  code?: string;
  children?: HierarchyNode[];
}

// Узел для силовой визуализации
export interface NetworkNode {
  id: number;
  name: string;
  level: number;
  division?: string;
  position?: string;
}

// Связь для силовой визуализации
export interface NetworkLink {
  source: number;
  target: number;
  type: string;
}

// Сеть (используется для force-directed graph)
export interface Network {
  nodes: NetworkNode[];
  links: NetworkLink[];
}

// Mock данные
class OrganizationData {
  // Организации (юрлица и локации)
  organizations: Organization[] = [
    {
      id: 1,
      name: 'ОФС Глобал',
      description: 'Головная организация холдинга ОФС',
      parent_id: null,
      org_type: 'LEGAL_ENTITY',
      is_active: true,
      legal_address: 'г. Москва, ул. Ленина, д. 1',
      inn: '7701234567',
      kpp: '770101001',
    },
    {
      id: 2,
      name: 'ОФС-Москва',
      description: 'Московское подразделение ОФС',
      parent_id: 1,
      org_type: 'LEGAL_ENTITY',
      is_active: true,
      legal_address: 'г. Москва, ул. Тверская, д. 10',
      inn: '7702345678',
      kpp: '770201001',
    },
    {
      id: 3,
      name: 'ОФС-Питер',
      description: 'Санкт-Петербургское подразделение ОФС',
      parent_id: 1,
      org_type: 'LEGAL_ENTITY',
      is_active: true,
      legal_address: 'г. Санкт-Петербург, Невский проспект, д. 20',
      inn: '7803456789',
      kpp: '780301001',
    },
    {
      id: 4,
      name: 'ОФС-Сибирь',
      description: 'Сибирское подразделение ОФС',
      parent_id: 1,
      org_type: 'LEGAL_ENTITY',
      is_active: false,
      legal_address: 'г. Новосибирск, ул. Красная, д. 5',
      inn: '5404567890',
      kpp: '540401001',
    },
    {
      id: 5,
      name: 'БЦ Метрополис',
      description: 'Головной офис в Москве',
      parent_id: 1,
      org_type: 'LOCATION',
      is_active: true,
      physical_address: 'г. Москва, Ленинградское шоссе, д. 16А, стр. 1',
    },
    {
      id: 6,
      name: 'БЦ Невский',
      description: 'Офис в Санкт-Петербурге',
      parent_id: 3,
      org_type: 'LOCATION',
      is_active: true,
      physical_address: 'г. Санкт-Петербург, Невский проспект, д. 100',
    },
    {
      id: 7,
      name: 'Технопарк',
      description: 'Производственное подразделение в Москве',
      parent_id: 2,
      org_type: 'LOCATION',
      is_active: true,
      physical_address: 'г. Москва, ул. Академика Королева, д. 12',
    },
  ];

  // Подразделения
  divisions: Division[] = [
    {
      id: 1,
      name: 'Правление',
      code: 'BOARD',
      description: 'Руководство компании',
      parent_id: null,
      level: 1,
      is_active: true,
      children: [],
    },
    {
      id: 2,
      name: 'Департамент ИТ',
      code: 'IT',
      description: 'Департамент информационных технологий',
      parent_id: 1,
      level: 2,
      is_active: true,
      children: [],
    },
    {
      id: 3,
      name: 'Департамент Финансов',
      code: 'FIN',
      description: 'Департамент финансов и бухгалтерии',
      parent_id: 1,
      level: 2,
      is_active: true,
      children: [],
    },
    {
      id: 4,
      name: 'Департамент HR',
      code: 'HR',
      description: 'Департамент управления персоналом',
      parent_id: 1,
      level: 2,
      is_active: true,
      children: [],
    },
    {
      id: 5,
      name: 'Отдел разработки',
      code: 'DEV',
      description: 'Отдел разработки ПО',
      parent_id: 2,
      level: 3,
      is_active: true,
      children: [],
    },
    {
      id: 6,
      name: 'Отдел тестирования',
      code: 'QA',
      description: 'Отдел тестирования и контроля качества',
      parent_id: 2,
      level: 3,
      is_active: true,
      children: [],
    },
    {
      id: 7,
      name: 'Отдел инфраструктуры',
      code: 'INFRA',
      description: 'Отдел ИТ-инфраструктуры',
      parent_id: 2,
      level: 3,
      is_active: true,
      children: [],
    },
    {
      id: 8,
      name: 'Бухгалтерия',
      code: 'ACCT',
      description: 'Бухгалтерия',
      parent_id: 3,
      level: 3,
      is_active: true,
      children: [],
    },
    {
      id: 9,
      name: 'Отдел бюджетирования',
      code: 'BUDG',
      description: 'Отдел планирования и бюджетирования',
      parent_id: 3,
      level: 3,
      is_active: true,
      children: [],
    },
    {
      id: 10,
      name: 'Отдел найма',
      code: 'RECR',
      description: 'Отдел рекрутинга и найма',
      parent_id: 4,
      level: 3,
      is_active: true,
      children: [],
    },
    {
      id: 11,
      name: 'Отдел обучения',
      code: 'TRAIN',
      description: 'Отдел обучения и развития',
      parent_id: 4,
      level: 3,
      is_active: true,
      children: [],
    },
    {
      id: 12,
      name: 'Команда Frontend',
      code: 'FE',
      description: 'Команда разработки Frontend',
      parent_id: 5,
      level: 4,
      is_active: true,
      children: [],
    },
    {
      id: 13,
      name: 'Команда Backend',
      code: 'BE',
      description: 'Команда разработки Backend',
      parent_id: 5,
      level: 4,
      is_active: true,
      children: [],
    },
  ];

  // Сотрудники
  staff: Staff[] = [
    {
      id: 1,
      name: 'Иванов Иван Иванович',
      position: 'Генеральный директор',
      division: 'Правление',
      division_id: 1,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 1,
      email: 'ivanov@ofs.ru',
      phone: '+7 (900) 123-45-67',
    },
    {
      id: 2,
      name: 'Петров Петр Петрович',
      position: 'Финансовый директор',
      division: 'Правление',
      division_id: 1,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 1,
      email: 'petrov@ofs.ru',
      phone: '+7 (900) 234-56-78',
    },
    {
      id: 3,
      name: 'Сидоров Сидор Сидорович',
      position: 'ИТ-директор',
      division: 'Правление',
      division_id: 1,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 1,
      email: 'sidorov@ofs.ru',
      phone: '+7 (900) 345-67-89',
    },
    {
      id: 4,
      name: 'Козлов Козьма Петрович',
      position: 'Директор по персоналу',
      division: 'Правление',
      division_id: 1,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 1,
      email: 'kozlov@ofs.ru',
      phone: '+7 (900) 456-78-90',
    },
    {
      id: 5,
      name: 'Смирнов Алексей Владимирович',
      position: 'Руководитель департамента ИТ',
      division: 'Департамент ИТ',
      division_id: 2,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 2,
      email: 'smirnov@ofs.ru',
      phone: '+7 (900) 567-89-01',
    },
    {
      id: 6,
      name: 'Кузнецов Дмитрий Сергеевич',
      position: 'Руководитель департамента финансов',
      division: 'Департамент Финансов',
      division_id: 3,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 2,
      email: 'kuznetsov@ofs.ru',
      phone: '+7 (900) 678-90-12',
    },
    {
      id: 7,
      name: 'Соколова Мария Ивановна',
      position: 'Руководитель HR-департамента',
      division: 'Департамент HR',
      division_id: 4,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 2,
      email: 'sokolova@ofs.ru',
      phone: '+7 (900) 789-01-23',
    },
    {
      id: 8,
      name: 'Новиков Андрей Петрович',
      position: 'Начальник отдела разработки',
      division: 'Отдел разработки',
      division_id: 5,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 3,
      email: 'novikov@ofs.ru',
      phone: '+7 (900) 890-12-34',
    },
    {
      id: 9,
      name: 'Морозова Екатерина Александровна',
      position: 'Начальник отдела тестирования',
      division: 'Отдел тестирования',
      division_id: 6,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 3,
      email: 'morozova@ofs.ru',
      phone: '+7 (900) 901-23-45',
    },
    {
      id: 10,
      name: 'Волков Игорь Владимирович',
      position: 'Начальник отдела инфраструктуры',
      division: 'Отдел инфраструктуры',
      division_id: 7,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 3,
      email: 'volkov@ofs.ru',
      phone: '+7 (900) 012-34-56',
    },
    {
      id: 11,
      name: 'Васильева Ольга Николаевна',
      position: 'Главный бухгалтер',
      division: 'Бухгалтерия',
      division_id: 8,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 3,
      email: 'vasilyeva@ofs.ru',
      phone: '+7 (900) 123-45-67',
    },
    {
      id: 12,
      name: 'Зайцев Артём Дмитриевич',
      position: 'Руководитель отдела бюджетирования',
      division: 'Отдел бюджетирования',
      division_id: 9,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 3,
      email: 'zaitsev@ofs.ru',
      phone: '+7 (900) 234-56-78',
    },
    {
      id: 13,
      name: 'Павлова Наталья Сергеевна',
      position: 'Руководитель отдела найма',
      division: 'Отдел найма',
      division_id: 10,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 3,
      email: 'pavlova@ofs.ru',
      phone: '+7 (900) 345-67-89',
    },
    {
      id: 14,
      name: 'Семенов Кирилл Алексеевич',
      position: 'Руководитель отдела обучения',
      division: 'Отдел обучения',
      division_id: 11,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 3,
      email: 'semenov@ofs.ru',
      phone: '+7 (900) 456-78-90',
    },
    {
      id: 15,
      name: 'Голубев Михаил Владимирович',
      position: 'Руководитель Frontend команды',
      division: 'Команда Frontend',
      division_id: 12,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 4,
      email: 'golubev@ofs.ru',
      phone: '+7 (900) 567-89-01',
    },
    {
      id: 16,
      name: 'Виноградов Николай Иванович',
      position: 'Руководитель Backend команды',
      division: 'Команда Backend',
      division_id: 13,
      organization_id: 1,
      legal_entity_id: 1,
      location_id: 5,
      level: 4,
      email: 'vinogradov@ofs.ru',
      phone: '+7 (900) 678-90-12',
    },
    // Сотрудники питерского офиса
    {
      id: 17,
      name: 'Григорьев Станислав Петрович',
      position: 'Директор Санкт-Петербургского офиса',
      division: 'Правление',
      division_id: 1,
      organization_id: 3,
      legal_entity_id: 3,
      location_id: 6,
      level: 2,
      email: 'grigoriev@ofs.ru',
      phone: '+7 (900) 789-01-23',
    },
  ];

  // Функциональные связи
  functionalRelations: FunctionalRelation[] = [
    // Административные связи
    { id: 1, manager_id: 1, subordinate_id: 2, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 2, manager_id: 1, subordinate_id: 3, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 3, manager_id: 1, subordinate_id: 4, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 4, manager_id: 1, subordinate_id: 17, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение руководителя филиала' },
    { id: 5, manager_id: 3, subordinate_id: 5, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 6, manager_id: 2, subordinate_id: 6, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 7, manager_id: 4, subordinate_id: 7, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 8, manager_id: 5, subordinate_id: 8, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 9, manager_id: 5, subordinate_id: 9, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 10, manager_id: 5, subordinate_id: 10, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 11, manager_id: 6, subordinate_id: 11, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 12, manager_id: 6, subordinate_id: 12, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 13, manager_id: 7, subordinate_id: 13, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 14, manager_id: 7, subordinate_id: 14, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 15, manager_id: 8, subordinate_id: 15, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    { id: 16, manager_id: 8, subordinate_id: 16, relation_type: 'ADMINISTRATIVE', description: 'Прямое подчинение' },
    
    // Функциональные связи
    { id: 17, manager_id: 1, subordinate_id: 5, relation_type: 'FUNCTIONAL', description: 'Стратегическое руководство' },
    { id: 18, manager_id: 1, subordinate_id: 6, relation_type: 'FUNCTIONAL', description: 'Стратегическое руководство' },
    { id: 19, manager_id: 1, subordinate_id: 7, relation_type: 'FUNCTIONAL', description: 'Стратегическое руководство' },
    { id: 20, manager_id: 3, subordinate_id: 8, relation_type: 'FUNCTIONAL', description: 'Техническое руководство' },
    { id: 21, manager_id: 3, subordinate_id: 9, relation_type: 'FUNCTIONAL', description: 'Техническое руководство' },
    { id: 22, manager_id: 3, subordinate_id: 10, relation_type: 'FUNCTIONAL', description: 'Техническое руководство' },
    
    // Проектные связи
    { id: 23, manager_id: 5, subordinate_id: 11, relation_type: 'PROJECT', description: 'Проект автоматизации бухгалтерии' },
    { id: 24, manager_id: 8, subordinate_id: 14, relation_type: 'PROJECT', description: 'Проект обучения разработчиков' },
    { id: 25, manager_id: 9, subordinate_id: 15, relation_type: 'PROJECT', description: 'Тестирование Frontend' },
    { id: 26, manager_id: 9, subordinate_id: 16, relation_type: 'PROJECT', description: 'Тестирование Backend' },
    
    // Территориальные связи
    { id: 27, manager_id: 17, subordinate_id: 10, relation_type: 'TERRITORIAL', description: 'Инфраструктура СПб офиса' },
    
    // Менторство
    { id: 28, manager_id: 8, subordinate_id: 16, relation_type: 'MENTORING', description: 'Профессиональное развитие' },
    { id: 29, manager_id: 15, subordinate_id: 9, relation_type: 'MENTORING', description: 'Обучение автоматизации тестирования UI' },
  ];

  // Получение структурированного дерева юрлиц
  getLegalEntityHierarchy(): HierarchyNode[] {
    return this._buildHierarchy(
      this.organizations.filter(org => org.org_type === 'LEGAL_ENTITY'),
      'LEGAL_ENTITY'
    );
  }

  // Получение структурированного дерева локаций
  getLocationHierarchy(): HierarchyNode[] {
    return this._buildHierarchy(
      this.organizations.filter(org => org.org_type === 'LOCATION'),
      'LOCATION'
    );
  }

  // Получение структурированного дерева подразделений
  getDivisionHierarchy(): HierarchyNode[] {
    return this._buildDivisionHierarchy(this.divisions);
  }

  // Получение данных для сетевой визуализации
  getFunctionalRelationsNetwork(): Network {
    const nodes: NetworkNode[] = this.staff.map(person => ({
      id: person.id,
      name: person.name,
      level: person.level,
      division: person.division,
      position: person.position
    }));

    const links: NetworkLink[] = this.functionalRelations.map(rel => ({
      source: rel.manager_id,
      target: rel.subordinate_id,
      type: rel.relation_type
    }));

    return { nodes, links };
  }

  // Построение иерархии из плоского списка
  private _buildHierarchy(items: Organization[], type: 'LEGAL_ENTITY' | 'LOCATION'): HierarchyNode[] {
    const map = new Map<number, HierarchyNode>();
    
    // Создаем карту объектов
    items.forEach(item => {
      map.set(item.id, {
        id: item.id,
        name: item.name,
        description: item.description,
        is_active: item.is_active,
        children: []
      });
    });

    // Устанавливаем родительские связи
    const roots: HierarchyNode[] = [];
    items.forEach(item => {
      if (item.parent_id === null) {
        // Это корневой элемент
        roots.push(map.get(item.id)!);
      } else {
        // Если родитель не того же типа (смешанная структура), находим родителя среди всех организаций
        let parent: HierarchyNode | undefined;
        const parentOrg = this.organizations.find(org => org.id === item.parent_id);
        if (parentOrg) {
          if (parentOrg.org_type === type) {
            // Родитель того же типа
            parent = map.get(item.parent_id);
          } else {
            // Родитель другого типа, ищем ближайшего предка нужного типа
            let currentParentId = parentOrg.parent_id;
            while (currentParentId !== null) {
              const ancestor = this.organizations.find(org => org.id === currentParentId);
              if (ancestor && ancestor.org_type === type) {
                parent = map.get(ancestor.id);
                break;
              }
              currentParentId = ancestor ? ancestor.parent_id : null;
            }

            // Если родитель не найден, это корневой элемент
            if (!parent) {
              roots.push(map.get(item.id)!);
              return;
            }
          }
        }

        // Если нашли родителя, добавляем к нему
        if (parent && parent.children) {
          parent.children.push(map.get(item.id)!);
        } else {
          // Иначе считаем корневым элементом
          roots.push(map.get(item.id)!);
        }
      }
    });

    // Если у корня нет дочерних элементов, добавляем все элементы без родителя
    if (roots.length === 0 && items.length > 0) {
      items.filter(item => !item.parent_id || !map.has(item.parent_id)).forEach(item => {
        roots.push(map.get(item.id)!);
      });
    }

    return roots;
  }

  // Построение иерархии подразделений
  private _buildDivisionHierarchy(divisions: Division[]): HierarchyNode[] {
    // Копируем все подразделения для безопасного изменения
    const divisionsCopy = JSON.parse(JSON.stringify(divisions)) as Division[];
    
    // Строим дерево подразделений
    const divisionMap = new Map<number, Division>();
    divisionsCopy.forEach(div => {
      divisionMap.set(div.id, div);
      div.children = [];
    });
    
    const roots: Division[] = [];
    divisionsCopy.forEach(div => {
      if (div.parent_id === null) {
        // Корневой элемент
        roots.push(div);
      } else {
        // Подчиненный элемент
        const parent = divisionMap.get(div.parent_id);
        if (parent) {
          if (!parent.children) parent.children = [];
          parent.children.push(div);
        } else {
          // Если родитель не найден, считаем корневым
          roots.push(div);
        }
      }
    });
    
    // Преобразуем деревья в формат для визуализации
    const result: HierarchyNode[] = roots.map(div => this._divisionToHierarchyNode(div));
    
    return result;
  }
  
  // Преобразование Division в HierarchyNode
  private _divisionToHierarchyNode(division: Division): HierarchyNode {
    return {
      id: division.id,
      name: division.name,
      description: division.description,
      is_active: division.is_active,
      level: division.level,
      code: division.code,
      children: division.children ? division.children.map(child => this._divisionToHierarchyNode(child)) : undefined
    };
  }
}

// Создаем экземпляр данных
const organizationData = new OrganizationData();

export default organizationData; 