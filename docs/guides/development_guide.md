# Руководство по разработке OFS Global

## Настройка окружения

### Требования

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Git

### Настройка бэкенда

1. Клонирование репозитория:
```bash
git clone <repository-url>
cd ofs_project
```

2. Создание виртуального окружения:
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/MacOS
venv\Scripts\activate     # Для Windows
```

3. Установка зависимостей:
```bash
pip install -r requirements.txt
```

4. Настройка переменных окружения:
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

5. Применение миграций:
```bash
alembic upgrade head
```

6. Запуск сервера разработки:
```bash
uvicorn app.main:app --reload
```

### Настройка фронтенда

1. Переход в директорию фронтенда:
```bash
cd ofs_new/frontend
```

2. Установка зависимостей:
```bash
npm install
```

3. Запуск сервера разработки:
```bash
npm run dev
```

## Структура проекта

### Бэкенд

```
ofs_new/backend/
├── alembic/              # Миграции базы данных
├── app/                  # Основной код приложения
│   ├── api/              # API эндпоинты
│   │   └── api_v1/       # API версии 1
│   │       ├── endpoints/# API эндпоинты по модулям
│   │       └── api.py    # Регистрация всех эндпоинтов
│   ├── core/             # Ядро приложения
│   │   ├── config.py     # Конфигурация
│   │   └── security.py   # Безопасность и аутентификация
│   ├── crud/             # CRUD операции для сущностей
│   ├── db/               # Настройки базы данных
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   ├── utils/            # Вспомогательные функции
│   └── main.py           # Точка входа в приложение
├── tests/                # Тесты
└── requirements.txt      # Зависимости
```

### Фронтенд

```
ofs_new/frontend/
├── node_modules/         # Зависимости Node.js
├── public/               # Статические файлы
├── src/                  # Исходный код
│   ├── api/              # API-клиенты
│   ├── assets/           # Ресурсы (изображения, шрифты)
│   ├── components/       # React-компоненты
│   │   ├── staff/    # Компоненты для сотрудников
│   │   ├── organization/ # Компоненты для организации
│   │   └── ...
│   ├── context/          # React контексты
│   ├── hooks/            # Кастомные React-хуки
│   ├── pages/            # Страницы приложения
│   ├── styles/           # CSS стили
│   ├── types/            # TypeScript типы
│   ├── utils/            # Вспомогательные функции
│   ├── App.tsx           # Главный компонент
│   └── main.tsx          # Точка входа
├── package.json          # Зависимости и скрипты
└── vite.config.ts        # Конфигурация Vite
```

## Стандарты кодирования

### Общие правила

- Используйте линтеры и форматтеры (ESLint, Prettier, Black, Flake8)
- Следуйте принципам чистого кода
- Пишите тесты для критичных компонентов
- Документируйте публичные API

### Бэкенд (Python)

- Следуйте PEP 8 для стиля кода
- Используйте типизацию
- Документируйте функции и методы
- Используйте асинхронные функции (async/await) где возможно
- Пример:

```python
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db)
) -> Staff:
    """
    Получает сотрудника по ID.
    
    Args:
        employee_id: ID сотрудника
        db: Сессия базы данных
        
    Returns:
        Объект сотрудника
        
    Raises:
        HTTPException: Если сотрудник не найден
    """
    staff = await crud.staff.get(db, id=employee_id)
    if not staff:
        raise HTTPException(
            status_code=404,
            detail="Staff not found"
        )
    return staff
```

### Фронтенд (TypeScript/React)

- Используйте функциональные компоненты и хуки
- Разделяйте бизнес-логику и отображение
- Типизируйте пропсы и состояния
- Используйте CSS-модули или styled-components
- Пример:

```tsx
interface EmployeeCardProps {
  staff: Staff;
  onEdit: (id: number) => void;
}

const EmployeeCard: React.FC<EmployeeCardProps> = ({ 
  staff, 
  onEdit 
}) => {
  return (
    <Card className="staff-card">
      <CardHeader 
        title={staff.name}
        subheader={staff.position}
      />
      <CardContent>
        <Typography>{staff.email}</Typography>
        <Typography>{staff.phone}</Typography>
      </CardContent>
      <CardActions>
        <Button 
          onClick={() => onEdit(staff.id)}
          variant="contained"
        >
          Редактировать
        </Button>
      </CardActions>
    </Card>
  );
};
```

## Работа с API

### Бэкенд

- Используйте Dependency Injection (FastAPI)
- Документируйте эндпоинты с использованием OpenAPI
- Валидируйте входные данные с помощью Pydantic
- Обрабатывайте ошибки с нужными HTTP-кодами

### Фронтенд

- Используйте axios или fetch для запросов к API
- Обрабатывайте состояния загрузки, успеха и ошибки
- Кешируйте результаты где это уместно
- Пример:

```tsx
const fetchEmployees = async () => {
  setLoading(true);
  try {
    const response = await api.get('/staff/');
    setEmployees(response.data);
  } catch (error) {
    setError('Не удалось загрузить список сотрудников');
    console.error(error);
  } finally {
    setLoading(false);
  }
};
```

## Рабочий процесс Git

1. Создавайте ветку для каждой новой задачи
2. Делайте небольшие коммиты с понятными сообщениями
3. Создавайте Pull Request в main/develop
4. Проходите код-ревью
5. Сливайте ветку после проверки

Пример:
```bash
git checkout -b feature/staff-management
# Внесите изменения
git add .
git commit -m "Add staff CRUD operations"
git push origin feature/staff-management
# Создайте Pull Request на GitHub
```

## Отладка и исправление ошибок

### Бэкенд

- Используйте логгер вместо print
- Настройте дебаггер (например, pdb или IDE)
- Включите подробные логи на время отладки
- Используйте инструменты профилирования для оптимизации

### Фронтенд

- Используйте React Developer Tools
- Добавьте инструментацию с помощью консольных логов (но удаляйте их перед коммитом)
- Используйте режим разработчика в браузере
- Тестируйте в разных браузерах

## Известные проблемы и их решения

### Проблема: Ошибка импорта MainLayout в App.tsx

**Ошибка:**
```
Failed to resolve import "./components/layout/MainLayout" from "src\App.tsx". Does the file exist?
```

**Решение:**

1. Проверьте, что файл существует по указанному пути
2. Убедитесь, что имена файлов и директорий соответствуют регистру
3. Если файл был только что создан, попробуйте перезапустить сервер разработки

### Проблема: Ошибка импорта NodeEditModal в OrganizationTree.tsx

**Ошибка:**
```
Failed to resolve import "./NodeEditModal" from "src\components\organization\OrganizationTree.tsx". Does the file exist?
```

**Решение:**

1. Создайте файл NodeEditModal.tsx, если он отсутствует
2. Исправьте путь импорта, если файл находится в другом месте
3. Проверьте правильность экспорта компонента

## Развертывание

### Подготовка к продакшену

1. Сборка фронтенда:
```bash
cd ofs_new/frontend
npm run build
```

2. Настройка базы данных продакшена:
```bash
alembic upgrade head
```

3. Запуск бэкенда:
```bash
cd ofs_new/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker

Проект можно запустить с помощью Docker:

```bash
docker-compose up -d
```

### CI/CD

Для CI/CD можно использовать GitHub Actions, GitLab CI или другие инструменты, которые будут:

1. Запускать тесты при каждом пуше
2. Проверять код с помощью линтеров
3. Собирать и публиковать образы Docker
4. Деплоить на сервер

## Вопросы и поддержка

По всем вопросам обращайтесь:
- Создавайте issue в репозитории
- Обращайтесь к тех-лиду проекта 