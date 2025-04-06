# 🔄 План Миграции с MUI на Ant Design

## 📋 Чеклист Миграции на Ant Design

### 1️⃣ Базовая настройка ✅
- [x] Установить зависимости Ant Design:
  ```bash
  npm install antd @ant-design/icons
  ```
- [x] Добавить импорт стилей в главный файл:
  ```jsx
  import 'antd/dist/reset.css'; // В main.tsx
  ```
- [x] Настроить тему Ant Design (создать файл `theme.ts`):
  ```typescript
  // frontend/src/theme.ts
  export const theme = {
    token: {
      colorPrimary: '#9D6AF5', // Фиолетовый цвет
      borderRadius: 8,
      colorBgLayout: '#121215',
      colorBgContainer: '#1A1A20',
    },
  };
  ```
- [x] Обернуть приложение в ConfigProvider:
  ```jsx
  import { ConfigProvider } from 'antd';
  import { theme } from './theme';
  
  <ConfigProvider theme={theme}>
    <App />
  </ConfigProvider>
  ```

### 2️⃣ Миграция базовых компонентов ✅
- [x] Создать маппинг MUI → Ant Design компонентов (шпаргалка для упрощения)
- [x] Заменить все импорты MUI на Ant Design:
  - [x] `@mui/material` → `antd`
  - [x] `@mui/icons-material` → `@ant-design/icons`
- [x] Мигрировать основные глобальные компоненты:
  - [x] Layout и навигация (`MainLayout.tsx`)
    - [x] **Исправить ошибку парсинга JSX после миграции.** (✅ Решено: убрали комментарии после JSX тегов)
    - [x] Проверить/мигрировать зависимости (`TopBar.tsx`, `MenuListItems.tsx`)
  - [x] Модальные окна (Dialog → Modal)
  - [x] Формы (TextField → Input, Select и т.д.)
  - [x] Таблицы (Table компоненты)
  - [x] Кнопки и иконки

### 3️⃣ Миграция по страницам (по приоритету) ✅
- [x] Аутентификация (высший приоритет):
  - [x] `LoginPage.tsx`
  - [x] `RegisterPage.tsx`
  - [x] `ProtectedRoute.tsx`
- [x] Основные страницы:
  - [x] `AdminOrganizationsPage.tsx`
  - [x] `AdminStaffPage.tsx`
  - [x] `AdminPositionsPage.tsx` (уже использует Ant Design)
  - [x] `AdminDivisionsPage.tsx` (уже использует Ant Design)
- [x] Вспомогательные компоненты:
  - [x] Компоненты таблиц
  - [x] Компоненты поиска и фильтрации
  - [x] `StaffList.tsx`
  - [x] `DivisionList.tsx`
  - [x] `DivisionEditModal.tsx` 
  - [x] `PositionList.tsx`
  - [x] `PositionEditModal.tsx`
  - [x] `StaffForm.tsx` - большая форма для создания/редактирования сотрудников
  - [x] Другие компоненты (см. раздел "Оставшиеся компоненты")

### 4️⃣ Специфические компоненты Ant Design ✅
- [x] Заменить MUI Tables на Ant Design Table с пагинацией и сортировкой
- [x] Внедрить Ant Design Forms вместо форм на MUI
- [x] Использовать Ant Design Notification вместо Snackbar
- [x] Обновить IconButton на Button с иконками из @ant-design/icons

### 5️⃣ Стилизация и миграция CSS ✅
- [x] Заменить `sx` prop на стили Ant Design:
  - [x] Встроенные пропсы (style={{ marginBottom: 16 }})
  - [x] CSS-модули или styled-components
- [x] Перенести цветовую схему в новый theme.ts
- [x] Обновить отступы и размеры согласно системе Ant Design
- [x] Добавить глобальные стили (например, для скроллбаров Webkit) в dark-theme.css

### 6️⃣ Тестирование и исправление ошибок ✅
- [x] Проверить работу всех форм и отправку данных
- [x] Проверить работу кнопок и событий
- [x] Тестирование работы авторизации
- [x] Проверка отображения на разных размерах экрана

---

## 🔍 Оставшиеся компоненты

### Компоненты графиков и структуры
Эти компоненты более сложные и могут требовать специальных библиотек:

1. **Организационная структура:**
   - [x] `ReactFlowGraph.tsx` - полностью мигрирован с MUI на Ant Design
   - [x] `OrganizationTree.tsx` - создан новый компонент `AntOrganizationTree.tsx` на Ant Design
   - [x] `OrganizationStructure.tsx` - комплексный компонент полностью мигрирован

2. **Страницы графиков и структур:**
   - [x] `OrganizationStructurePage.tsx` - мигрирована с использованием AntOrganizationTree
   - [x] `FunctionalRelationsPage.tsx` - мигрирована базовая страница

### Формы и модальные окна
Эти компоненты используют более сложную логику форм:

1. **Формы связей:**
   - [x] `FunctionalRelationList.tsx` - список функциональных связей с таблицей и фильтрами
   - [x] `FunctionalRelationsManager.tsx` - управление функциональными связями на странице сотрудника

### Остальные страницы
Эти компоненты используют базовые элементы MUI:

1. **Страницы:**
   - [x] `Dashboard.tsx`
   - [x] `TelegramBotPage.tsx`
   - [x] `NotFoundPage.tsx` - мигрирована с использованием компонента Result
   - [x] `DivisionsPage.tsx` (в папке pages/divisions)
   - [x] `PositionsPage.tsx` (в папке pages/positions)

---

## 🗺️ Дорожная карта миграции

### Этап 1: Подготовка (1-2 дня) ✅
- Установка зависимостей и базовая настройка
- Создание ветки разработки для миграции
- Настройка темы и основных стилей
- Создание маппинга компонентов MUI → Ant Design

### Этап 2: Базовая структура (2-3 дня) ✅
- Миграция MainLayout и всей навигации
- Создание базовых компонентов форм и таблиц
- Миграция модальных окон и общих компонентов

### Этап 3: Страницы и логика (3-5 дней) ✅
- Миграция страницы организаций (приоритет #1)
- Миграция страниц аутентификации
- Миграция других админ-страниц

### Этап 4: Визуализация и графики (2-3 дня) ✅
- [x] Изучение возможностей библиотек визуализации для Ant Design
- [x] Создание компонента `AntOrgChart.tsx` для организационной структуры
- [x] Создание компонента `AntOrganizationTree.tsx` на основе `OrganizationTree.tsx`
- [x] Миграция страницы организационной структуры
- [x] Адаптация ReactFlow компонентов для использования с Ant Design

### Этап 5: Тестирование и оптимизация (2-3 дня) ✅
- [x] Тестирование работы всех функций
- [x] Исправление визуальных несоответствий
- [x] Оптимизация бандла и производительности

## 📚 Ключевая документация
- [Ant Design Components](https://ant.design/components/overview/)
- [Ant Design Icons](https://ant-design.antgroup.com/components/icon)
- [Миграция с Material UI](https://ant.design/docs/react/migration-v5) (общие принципы)

## 💡 Бонусы Ant Design для вашего проекта
- **Table** с встроенными фильтрами, сортировкой и пагинацией
- **Form** с встроенной валидацией и авто-привязкой полей
- **Notification API** для красивых уведомлений
- **Tree** и **TreeSelect** для отображения иерархических структур (отделы, орг. структура)
- **ConfigProvider** для глобальной настройки темы

## 📋 Следующие шаги

### Приоритет 1: Завершение критических страниц
1. ✅ Мигрировать `DivisionEditModal.tsx`
2. ✅ Мигрировать `AdminPositionsPage.tsx` (уже использует Ant Design)
3. ✅ Мигрировать `AdminDivisionsPage.tsx` (уже использует Ant Design)

### Приоритет 2: Формы и модальные окна
4. ✅ Мигрировать `PositionList.tsx` - список должностей с таблицей и фильтрами
5. ✅ Мигрировать `PositionEditModal.tsx` - модальное окно для должностей
6. ✅ Мигрировать `StaffForm.tsx` - важная форма для создания/редактирования сотрудников
7. ✅ Мигрировать `FunctionalRelationsManager.tsx` - управление функциональными связями

### Приоритет 3: Графики и структуры
8. Изучить возможности Ant Design для графиков:
   - Рассмотреть `@ant-design/charts` для графиков
   - Рассмотреть `@ant-design/pro-components` для иерархических структур
9. Поэтапная миграция компонентов структуры:
   - `OrganizationTree.tsx`
   - `ReactFlowGraph.tsx` (может потребоваться сохранение ReactFlow + адаптация к Ant Design)

### Приоритет 4: Оставшиеся страницы
10. Мигрировать простые страницы:
   - [x] `Dashboard.tsx`
   - [x] `NotFoundPage.tsx`
   - [x] `DivisionsPage.tsx`
   - [x] `PositionsPage.tsx`
   - [x] Другие страницы с простым UI

### Финальные шаги
11. [x] Комплексное тестирование всего интерфейса
12. [x] Оптимизация производительности и размера бандла
13. [x] Документация по новой UI системе 
14. [x] Удаление пакетов Material UI из проекта (включая @mui/material, @mui/icons-material, @emotion/react, @emotion/styled)

## 📋 Следующие шаги

### Приоритет 1: Завершение критических страниц
1. ✅ Мигрировать `DivisionEditModal.tsx`
2. ✅ Мигрировать `AdminPositionsPage.tsx` (уже использует Ant Design)
3. ✅ Мигрировать `AdminDivisionsPage.tsx` (уже использует Ant Design)

### Приоритет 2: Формы и модальные окна
4. ✅ Мигрировать `PositionList.tsx` - список должностей с таблицей и фильтрами
5. ✅ Мигрировать `PositionEditModal.tsx` - модальное окно для должностей
6. ✅ Мигрировать `StaffForm.tsx` - важная форма для создания/редактирования сотрудников
7. ✅ Мигрировать `FunctionalRelationsManager.tsx` - управление функциональными связями

### Приоритет 3: Графики и структуры
8. Изучить возможности Ant Design для графиков:
   - Рассмотреть `@ant-design/charts` для графиков
   - Рассмотреть `@ant-design/pro-components` для иерархических структур
9. Поэтапная миграция компонентов структуры:
   - `OrganizationTree.tsx`
   - `ReactFlowGraph.tsx` (может потребоваться сохранение ReactFlow + адаптация к Ant Design)

### Приоритет 4: Оставшиеся страницы
10. Мигрировать простые страницы:
   - [x] `Dashboard.tsx`
   - [x] `NotFoundPage.tsx`
   - [x] `DivisionsPage.tsx`
   - [x] `PositionsPage.tsx`
   - [x] Другие страницы с простым UI

### Финальные шаги
11. [x] Комплексное тестирование всего интерфейса
12. [x] Оптимизация производительности и размера бандла
13. [x] Документация по новой UI системе 
14. [x] Удаление пакетов Material UI из проекта (включая @mui/material, @mui/icons-material, @emotion/react, @emotion/styled) 