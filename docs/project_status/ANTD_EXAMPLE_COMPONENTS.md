# 🔄 Примеры Конвертации Компонентов из MUI в Ant Design

Этот документ содержит практические примеры замены компонентов MUI на их аналоги в Ant Design для нашего проекта OFS Global.

## 📋 Таблица (Table)

### 🔴 Material UI:
```tsx
<TableContainer component={Paper}>
  <Table>
    <TableHead>
      <TableRow>
        <TableCell>ID</TableCell>
        <TableCell>Название</TableCell>
        <TableCell>Код</TableCell>
        <TableCell>Активна</TableCell>
        <TableCell>Действия</TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      {organizations.map((org) => (
        <TableRow key={org.id}>
          <TableCell>{org.id}</TableCell>
          <TableCell>{org.name}</TableCell>
          <TableCell>{org.code}</TableCell>
          <TableCell>{org.is_active ? 'Да' : 'Нет'}</TableCell>
          <TableCell>
            <IconButton onClick={() => handleEditItem(org)}>
              <EditIcon />
            </IconButton>
            <IconButton onClick={() => handleDeleteItem(org)}>
              <DeleteIcon />
            </IconButton>
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  </Table>
</TableContainer>
```

### 🟢 Ant Design:
```tsx
import { Table, Button, Space } from 'antd';
import { EditOutlined, DeleteOutlined } from '@ant-design/icons';

const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    key: 'id',
    sorter: (a, b) => a.id - b.id,
  },
  {
    title: 'Название',
    dataIndex: 'name',
    key: 'name',
    sorter: (a, b) => a.name.localeCompare(b.name),
  },
  {
    title: 'Код',
    dataIndex: 'code',
    key: 'code',
  },
  {
    title: 'Активна',
    dataIndex: 'is_active',
    key: 'is_active',
    render: (isActive) => (isActive ? 'Да' : 'Нет'),
    filters: [
      { text: 'Да', value: true },
      { text: 'Нет', value: false },
    ],
    onFilter: (value, record) => record.is_active === value,
  },
  {
    title: 'Действия',
    key: 'actions',
    render: (_, record) => (
      <Space>
        <Button 
          type="primary" 
          icon={<EditOutlined />} 
          onClick={() => handleEditItem(record)}
          size="small"
        />
        <Button 
          danger 
          icon={<DeleteOutlined />} 
          onClick={() => handleDeleteItem(record)}
          size="small"
        />
      </Space>
    ),
  },
];

// В компоненте:
<Table 
  columns={columns} 
  dataSource={organizations} 
  rowKey="id" 
  pagination={{ pageSize: 10 }}
  loading={loading}
/>
```

## 🪟 Модальное окно (Dialog/Modal)

### 🔴 Material UI:
```tsx
<Dialog
  open={editDialogOpen}
  onClose={() => !loading && setEditDialogOpen(false)}
  maxWidth="sm"
  fullWidth
>
  <DialogTitle>
    {currentItem.id ? 'Редактировать организацию' : 'Создать организацию'}
  </DialogTitle>
  <DialogContent dividers>
    <Box sx={{ mt: 1, mb: 1 }}>
      <TextField
        fullWidth
        required
        margin="dense"
        name="name"
        label="Название"
        value={currentItem.name || ''}
        onChange={(e) => setCurrentItem({ ...currentItem, [e.target.name]: e.target.value })}
        error={!currentItem.name?.trim()}
        helperText={!currentItem.name?.trim() ? 'Обязательное поле' : ''}
        disabled={loading}
        autoFocus
      />
      {/* Другие поля формы */}
    </Box>
  </DialogContent>
  <DialogActions sx={{ px: 3, py: 2 }}>
    <Button
      variant="outlined"
      onClick={() => setEditDialogOpen(false)}
      disabled={loading}
      startIcon={<CancelIcon />}
    >
      Отмена
    </Button>
    <Button
      variant="contained"
      color="primary"
      onClick={handleSaveItem}
      disabled={loading || !isFormValid}
      startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
    >
      {loading ? 'Сохранение...' : 'Сохранить'}
    </Button>
  </DialogActions>
</Dialog>
```

### 🟢 Ant Design:
```tsx
import { Modal, Form, Input, Button, Switch, Space, Spin } from 'antd';
import { SaveOutlined, CloseOutlined } from '@ant-design/icons';

<Modal
  title={currentItem?.id ? 'Редактировать организацию' : 'Создать организацию'}
  open={editDialogOpen}
  onCancel={() => !loading && setEditDialogOpen(false)}
  footer={null}
  width={600}
>
  <Form 
    layout="vertical"
    initialValues={currentItem}
    onFinish={handleSaveItem}
  >
    <Form.Item
      name="name"
      label="Название"
      rules={[{ required: true, message: 'Введите название организации' }]}
    >
      <Input 
        placeholder="Введите название" 
        disabled={loading}
        autoFocus
      />
    </Form.Item>
    
    {/* Другие поля формы */}
    
    <div style={{ marginTop: 24, textAlign: 'right' }}>
      <Space>
        <Button 
          onClick={() => setEditDialogOpen(false)}
          disabled={loading}
          icon={<CloseOutlined />}
        >
          Отмена
        </Button>
        <Button
          type="primary"
          htmlType="submit"
          disabled={loading}
          icon={loading ? <Spin size="small" /> : <SaveOutlined />}
        >
          {loading ? 'Сохранение...' : 'Сохранить'}
        </Button>
      </Space>
    </div>
  </Form>
</Modal>
```

## 📝 Форма с валидацией

### 🔴 Material UI:
```tsx
const [values, setValues] = useState({
  email: '',
  password: '',
});
const [errors, setErrors] = useState({
  email: '',
  password: '',
});

const handleChange = (e) => {
  setValues({ ...values, [e.target.name]: e.target.value });
};

const validate = () => {
  let valid = true;
  const newErrors = { email: '', password: '' };
  
  if (!values.email) {
    newErrors.email = 'Email обязателен';
    valid = false;
  }
  
  if (!values.password) {
    newErrors.password = 'Пароль обязателен';
    valid = false;
  }
  
  setErrors(newErrors);
  return valid;
};

const handleSubmit = (e) => {
  e.preventDefault();
  if (validate()) {
    // Отправка данных
  }
};

// В JSX:
<form onSubmit={handleSubmit}>
  <TextField
    fullWidth
    margin="normal"
    label="Email"
    name="email"
    type="email"
    value={values.email}
    onChange={handleChange}
    error={!!errors.email}
    helperText={errors.email}
  />
  <TextField
    fullWidth
    margin="normal"
    label="Пароль"
    name="password"
    type="password"
    value={values.password}
    onChange={handleChange}
    error={!!errors.password}
    helperText={errors.password}
  />
  <Button
    type="submit"
    fullWidth
    variant="contained"
    sx={{ mt: 3, mb: 2 }}
  >
    Войти
  </Button>
</form>
```

### 🟢 Ant Design:
```tsx
import { Form, Input, Button } from 'antd';

const onFinish = (values) => {
  // Отправка данных, значения уже проверены
  console.log('Success:', values);
};

// В JSX:
<Form
  name="login"
  initialValues={{ remember: true }}
  onFinish={onFinish}
  layout="vertical"
>
  <Form.Item
    label="Email"
    name="email"
    rules={[
      { required: true, message: 'Email обязателен' },
      { type: 'email', message: 'Введите корректный email' }
    ]}
  >
    <Input />
  </Form.Item>

  <Form.Item
    label="Пароль"
    name="password"
    rules={[{ required: true, message: 'Пароль обязателен' }]}
  >
    <Input.Password />
  </Form.Item>

  <Form.Item>
    <Button type="primary" htmlType="submit" style={{ width: '100%' }}>
      Войти
    </Button>
  </Form.Item>
</Form>
```

## 📱 Навигационное меню

### 🔴 Material UI:
```tsx
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Divider } from '@mui/material';
import { Home as HomeIcon, People as PeopleIcon, Settings as SettingsIcon } from '@mui/icons-material';

<Drawer
  variant="permanent"
  open={open}
>
  <List>
    <ListItem button component={Link} to="/dashboard">
      <ListItemIcon>
        <HomeIcon />
      </ListItemIcon>
      <ListItemText primary="Дашборд" />
    </ListItem>
    <ListItem button component={Link} to="/staff">
      <ListItemIcon>
        <PeopleIcon />
      </ListItemIcon>
      <ListItemText primary="Сотрудники" />
    </ListItem>
  </List>
  <Divider />
  <List>
    <ListItem button component={Link} to="/settings">
      <ListItemIcon>
        <SettingsIcon />
      </ListItemIcon>
      <ListItemText primary="Настройки" />
    </ListItem>
  </List>
</Drawer>
```

### 🟢 Ant Design:
```tsx
import { Layout, Menu } from 'antd';
import { HomeOutlined, UserOutlined, SettingOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

const { Sider } = Layout;

const location = useLocation();
const selectedKey = location.pathname;

<Sider width={200} theme="light" collapsible>
  <Menu
    mode="inline"
    selectedKeys={[selectedKey]}
    style={{ height: '100%', borderRight: 0 }}
  >
    <Menu.Item key="/dashboard" icon={<HomeOutlined />}>
      <Link to="/dashboard">Дашборд</Link>
    </Menu.Item>
    <Menu.Item key="/staff" icon={<UserOutlined />}>
      <Link to="/staff">Сотрудники</Link>
    </Menu.Item>
    <Menu.Divider />
    <Menu.Item key="/settings" icon={<SettingOutlined />}>
      <Link to="/settings">Настройки</Link>
    </Menu.Item>
  </Menu>
</Sider>
```

## 🚨 Обработка ошибок и уведомления

### 🔴 Material UI:
```tsx
const [error, setError] = useState(null);
const [success, setSuccess] = useState(null);

// В компоненте:
<Snackbar
  open={!!error}
  autoHideDuration={6000}
  onClose={() => setError(null)}
>
  <Alert severity="error" onClose={() => setError(null)}>
    {error}
  </Alert>
</Snackbar>

<Snackbar
  open={!!success}
  autoHideDuration={4000}
  onClose={() => setSuccess(null)}
>
  <Alert severity="success" onClose={() => setSuccess(null)}>
    {success}
  </Alert>
</Snackbar>

// Где-то в коде:
try {
  // Действие
  setSuccess('Операция успешно выполнена');
} catch (err) {
  setError('Произошла ошибка: ' + err.message);
}
```

### 🟢 Ant Design:
```tsx
import { message, notification } from 'antd';

// В компоненте не нужны состояния и JSX для уведомлений

// Где-то в коде:
try {
  // Действие
  message.success('Операция успешно выполнена');
  // или более детально:
  notification.success({
    message: 'Успех',
    description: 'Операция успешно выполнена',
    duration: 4,
  });
} catch (err) {
  message.error('Произошла ошибка: ' + err.message);
  // или более детально:
  notification.error({
    message: 'Ошибка',
    description: 'Произошла ошибка: ' + err.message,
    duration: 6,
  });
}
```

## 🔄 Загрузка данных и индикаторы

### 🔴 Material UI:
```tsx
const [loading, setLoading] = useState(false);

// В JSX:
<Box sx={{ position: 'relative' }}>
  {loading && (
    <LinearProgress sx={{ position: 'absolute', top: 0, left: 0, right: 0 }} />
  )}
  <Paper sx={{ p: 2, mt: 2 }}>
    {/* Контент */}
    {loading ? (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    ) : (
      <TableComponent data={data} />
    )}
  </Paper>
</Box>

<Button
  variant="contained"
  disabled={loading}
  startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
>
  {loading ? 'Загрузка...' : 'Сохранить'}
</Button>
```

### 🟢 Ant Design:
```tsx
import { Spin, Button, Card, Progress } from 'antd';
import { SaveOutlined } from '@ant-design/icons';

const [loading, setLoading] = useState(false);

// В JSX:
<div style={{ position: 'relative' }}>
  {loading && (
    <Progress percent={100} status="active" showInfo={false} style={{ position: 'absolute', top: 0, left: 0, right: 0 }} />
  )}
  <Card style={{ marginTop: 16 }}>
    <Spin spinning={loading}>
      <TableComponent data={data} />
    </Spin>
  </Card>
</div>

<Button
  type="primary"
  loading={loading}
  icon={!loading && <SaveOutlined />}
>
  {loading ? 'Загрузка...' : 'Сохранить'}
</Button>
```

## 🎨 Темы и стили

### 🔴 Material UI:
```tsx
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
  },
});

// В JSX:
<ThemeProvider theme={theme}>
  <App />
</ThemeProvider>

// Стили компонента
<Box 
  sx={{ 
    padding: 2, 
    backgroundColor: 'primary.light',
    '&:hover': {
      backgroundColor: 'primary.main',
    },
  }}
>
  <Typography variant="h4" sx={{ mb: 2, fontWeight: 'bold' }}>
    Заголовок
  </Typography>
</Box>
```

### 🟢 Ant Design:
```tsx
import { ConfigProvider } from 'antd';

const theme = {
  token: {
    colorPrimary: '#1976d2',
    colorInfo: '#1976d2',
    colorError: '#dc004e',
    borderRadius: 4,
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    Typography: {
      fontWeightStrong: 600,
    },
  },
};

// В JSX:
<ConfigProvider theme={theme}>
  <App />
</ConfigProvider>

// Стили компонента
<div 
  style={{ 
    padding: 16,
    backgroundColor: '#e3f2fd',
  }}
  className="custom-box" // + CSS файл с hover стилями
>
  <Typography.Title level={4} style={{ marginBottom: 16, fontWeight: 'bold' }}>
    Заголовок
  </Typography.Title>
</div>
```

Эти примеры иллюстрируют, как конвертировать основные компоненты из Material UI в их аналоги в Ant Design, сохраняя аналогичную функциональность. 