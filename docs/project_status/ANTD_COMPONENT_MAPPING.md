# 📊 Маппинг Компонентов Material UI → Ant Design

Эта шпаргалка поможет быстро найти замену компонентов MUI на аналогичные в Ant Design.

## 📑 Основные компоненты

| Material UI | Ant Design | Примечания |
|-------------|------------|------------|
| `Box` | `<div>` + style или `<Flex>` | Ant Design использует `<Flex>` как аналог Box с flex-свойствами |
| `Container` | `<div>` + style или `<Layout>` | В Ant Design нет прямого аналога Container |
| `Grid` | `<Row>` и `<Col>` | Ant Design использует 24-колоночную сетку |
| `Paper` | `<Card>` | Card в Ant Design более богатый функционалом |
| `Card` | `<Card>` | Очень похожи по функциональности |
| `Typography` | `<Typography.Title>` и `<Typography.Text>` | Более специализированные компоненты |
| `Divider` | `<Divider>` | Аналогичны |

## 🖲️ Элементы управления

| Material UI | Ant Design | Примечания |
|-------------|------------|------------|
| `Button` | `<Button>` | Схожий API, но различные варианты типов |
| `IconButton` | `<Button icon={<Icon />}>` | В Ant Design используется свойство `icon` |
| `Fab` | `<FloatButton>` | В Ant Design называется FloatButton |
| `TextField` | `<Input>` | Базовое текстовое поле |
| `TextField multiline` | `<Input.TextArea>` | Многострочное текстовое поле |
| `Select` | `<Select>` | В Ant Design более мощный функционал фильтрации |
| `Checkbox` | `<Checkbox>` | Схожи |
| `Radio` | `<Radio>` | Схожи |
| `Switch` | `<Switch>` | Схожи |
| `Slider` | `<Slider>` | Схожи |
| `Autocomplete` | `<AutoComplete>` | Схожи, но с разным API |

## 📋 Таблицы и данные

| Material UI | Ant Design | Примечания |
|-------------|------------|------------|
| `Table` | `<Table>` | Ant Design Table намного мощнее и имеет встроенную сортировку/пагинацию |
| `TableContainer` | Не требуется | Table в Ant Design не требует контейнера |
| `TableHead` | Через props `columns` | В Ant Design заголовки определяются через columns |
| `TableBody` | Через props `dataSource` | В Ant Design данные определяются через dataSource |
| `TableRow` / `TableCell` | Не требуются | В Ant Design строки и ячейки генерируются автоматически |
| `Pagination` | `<Pagination>` или встроенная в Table | Часто используется внутри Table |

## 🪟 Модальные окна и уведомления

| Material UI | Ant Design | Примечания |
|-------------|------------|------------|
| `Dialog` | `<Modal>` | API немного отличается |
| `DialogTitle` | `<Modal title="...">` | В Ant Design заголовок - это пропс Modal |
| `DialogContent` | Children в `<Modal>` | Просто содержимое Modal |
| `DialogActions` | Свойство `footer` у `<Modal>` | В Ant Design можно задать через props |
| `AlertDialog` | `<Modal>` + API модальных действий | Dialog в Ant Design обеспечивает API для модальных диалогов |
| `Snackbar` | `message.info()` / `notification.open()` | В Ant Design это глобальные методы |
| `Alert` | `<Alert>` или `message.success/error()` | Есть компонент и API |
| `Backdrop` | `<Spin>` с prop `fullscreen` | Для блокировки экрана при загрузке |

## 🎯 Навигация

| Material UI | Ant Design | Примечания |
|-------------|------------|------------|
| `AppBar` | `<Layout.Header>` | Часть компонента Layout |
| `Drawer` | `<Drawer>` | Схожи |
| `Menu` | `<Menu>` | В Ant Design более мощный функционал для меню |
| `Tabs` | `<Tabs>` | Схожи |
| `BottomNavigation` | Нет прямого аналога | Можно собрать из `<Menu>` |
| `Stepper` | `<Steps>` | В Ant Design называется Steps |
| `Breadcrumbs` | `<Breadcrumb>` | Схожи |

## 📊 Формы

| Material UI | Ant Design | Примечания |
|-------------|------------|------------|
| `FormControl` | `<Form>` | В Ant Design более мощная система форм |
| `FormLabel` / `InputLabel` | `<Form.Item label="...">` | В Ant Design лейблы - часть Form.Item |
| `FormHelperText` | Через props `help` у `<Form.Item>` | Для отображения подсказок и ошибок |
| `InputAdornment` | Свойства `prefix`/`suffix` у Input | В Ant Design это пропсы компонента Input |
| `FormGroup` | `<Form.Item>` | Для группировки элементов формы |

## 🎨 Индикаторы состояния

| Material UI | Ant Design | Примечания |
|-------------|------------|------------|
| `CircularProgress` | `<Spin>` | В Ant Design это компонент Spin |
| `LinearProgress` | `<Progress>` | В Ant Design более мощный с разными вариантами |
| `Badge` | `<Badge>` | Схожи |
| `Chip` | `<Tag>` | В Ant Design называется Tag |
| `Avatar` | `<Avatar>` | Схожи |
| `Skeleton` | `<Skeleton>` | Для заполнителей при загрузке |

## 📱 Отзывчивость и медиа

| Material UI | Ant Design | Примечания |
|-------------|------------|------------|
| `useMediaQuery` | `useBreakpoint()` из @ant-design/pro-components | Хук для определения брейкпоинтов |
| `Hidden` | CSS media queries | В Ant Design рекомендуется использовать CSS |
| `ImageList` | `<Image.PreviewGroup>` | Не прямой аналог, но похожий функционал |

## 🔖 Переход со стилей MUI на Ant Design

| Material UI | Ant Design | Примечания |
|-------------|------------|------------|
| `sx` prop | `style` prop | В Ant Design используется обычный style объект |
| `styled` | CSS-модули / styled-components | Ant Design рекомендует использовать CSS-модули |
| `makeStyles` | CSS-модули / styled-components | В экосистеме Ant Design редко используется |
| `ThemeProvider` | `<ConfigProvider theme={...}>` | Для настройки глобальной темы |
| MUI темы | `theme` объект для ConfigProvider | Разная структура тем | 