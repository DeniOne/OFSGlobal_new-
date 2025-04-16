# План разработки функций и функциональных связей

## 1. Создание базовых таблиц в БД

### Таблица для функций
```sql
CREATE TABLE IF NOT EXISTS functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Таблица для связи функций с должностями
```sql
CREATE TABLE IF NOT EXISTS functional_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_id INTEGER NOT NULL,
    function_id INTEGER NOT NULL,
    percentage INTEGER DEFAULT 100,
    is_primary BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE,
    FOREIGN KEY (function_id) REFERENCES functions(id) ON DELETE CASCADE
);
```

## 2. Модели для бэкенда (Pydantic)

### Модели для функций
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FunctionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    is_active: bool = True

class FunctionCreate(FunctionBase):
    pass

class FunctionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class Function(FunctionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

### Модели для функциональных назначений
```python
class FunctionalAssignmentBase(BaseModel):
    position_id: int
    function_id: int
    percentage: int = 100
    is_primary: bool = False

class FunctionalAssignmentCreate(FunctionalAssignmentBase):
    pass

class FunctionalAssignmentUpdate(BaseModel):
    position_id: Optional[int] = None
    function_id: Optional[int] = None
    percentage: Optional[int] = None
    is_primary: Optional[bool] = None

class FunctionalAssignment(FunctionalAssignmentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

## 3. Файлы CRUD операций

### crud_function.py
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import List, Optional, Dict, Any
from app.schemas.function import FunctionCreate, FunctionUpdate
from app.models.function import Function

class CRUDFunction:
    async def create(self, db: AsyncSession, *, obj_in: FunctionCreate) -> Function:
        db_obj = Function(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: int) -> Optional[Function]:
        result = await db.execute(select(Function).where(Function.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Function]:
        result = await db.execute(select(Function).offset(skip).limit(limit))
        return result.scalars().all()

    async def update(self, db: AsyncSession, *, id: int, obj_in: FunctionUpdate) -> Optional[Function]:
        update_data = obj_in.dict(exclude_unset=True)
        if not update_data:
            return await self.get(db, id)
        
        await db.execute(
            update(Function)
            .where(Function.id == id)
            .values(**update_data)
        )
        await db.commit()
        return await self.get(db, id)

    async def delete(self, db: AsyncSession, *, id: int) -> bool:
        result = await db.execute(delete(Function).where(Function.id == id))
        await db.commit()
        return result.rowcount > 0

function = CRUDFunction()
```

### crud_functional_assignment.py
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from typing import List, Optional, Dict, Any
from app.schemas.functional_assignment import FunctionalAssignmentCreate, FunctionalAssignmentUpdate
from app.models.functional_assignment import FunctionalAssignment

class CRUDFunctionalAssignment:
    async def create(self, db: AsyncSession, *, obj_in: FunctionalAssignmentCreate) -> FunctionalAssignment:
        db_obj = FunctionalAssignment(**obj_in.dict())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: int) -> Optional[FunctionalAssignment]:
        result = await db.execute(select(FunctionalAssignment).where(FunctionalAssignment.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, position_id: Optional[int] = None, function_id: Optional[int] = None
    ) -> List[FunctionalAssignment]:
        query = select(FunctionalAssignment)
        
        if position_id is not None:
            query = query.where(FunctionalAssignment.position_id == position_id)
            
        if function_id is not None:
            query = query.where(FunctionalAssignment.function_id == function_id)
            
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update(self, db: AsyncSession, *, id: int, obj_in: FunctionalAssignmentUpdate) -> Optional[FunctionalAssignment]:
        update_data = obj_in.dict(exclude_unset=True)
        if not update_data:
            return await self.get(db, id)
        
        await db.execute(
            update(FunctionalAssignment)
            .where(FunctionalAssignment.id == id)
            .values(**update_data)
        )
        await db.commit()
        return await self.get(db, id)

    async def delete(self, db: AsyncSession, *, id: int) -> bool:
        result = await db.execute(delete(FunctionalAssignment).where(FunctionalAssignment.id == id))
        await db.commit()
        return result.rowcount > 0

functional_assignment = CRUDFunctionalAssignment()
```

## 4. Эндпоинты API

### Роутер для функций
```python
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.api import deps
from app.crud.crud_function import function
from app.schemas.function import Function, FunctionCreate, FunctionUpdate

router = APIRouter()

@router.post("/", response_model=Function)
async def create_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    function_in: FunctionCreate,
):
    """
    Создать новую функцию.
    """
    return await function.create(db=db, obj_in=function_in)

@router.get("/", response_model=List[Function])
async def read_functions(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Получить список функций.
    """
    return await function.get_multi(db=db, skip=skip, limit=limit)

@router.get("/{id}", response_model=Function)
async def read_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
):
    """
    Получить конкретную функцию по ID.
    """
    result = await function.get(db=db, id=id)
    if not result:
        raise HTTPException(status_code=404, detail="Function not found")
    return result

@router.put("/{id}", response_model=Function)
async def update_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    function_in: FunctionUpdate,
):
    """
    Обновить функцию.
    """
    result = await function.get(db=db, id=id)
    if not result:
        raise HTTPException(status_code=404, detail="Function not found")
    return await function.update(db=db, id=id, obj_in=function_in)

@router.delete("/{id}", response_model=bool)
async def delete_function(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
):
    """
    Удалить функцию.
    """
    result = await function.get(db=db, id=id)
    if not result:
        raise HTTPException(status_code=404, detail="Function not found")
    return await function.delete(db=db, id=id)
```

## 5. Интерфейс для функций на фронтенде

### Создать сервис для работы с API функций
```typescript
// functionsService.ts
import api from './api';

export interface Function {
  id: number;
  name: string;
  code: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FunctionCreateDTO {
  name: string;
  code: string;
  description?: string;
  is_active?: boolean;
}

export interface FunctionUpdateDTO {
  name?: string;
  code?: string;
  description?: string;
  is_active?: boolean;
}

const functionsService = {
  /**
   * Получить все функции с возможностью фильтрации
   */
  async getFunctions(skip = 0, limit = 100): Promise<Function[]> {
    try {
      const { data } = await api.get('/functions', {
        params: { skip, limit }
      });
      return data;
    } catch (error) {
      console.error('Ошибка при получении списка функций:', error);
      throw error;
    }
  },

  /**
   * Получить функцию по ID
   */
  async getFunctionById(id: number): Promise<Function> {
    try {
      const { data } = await api.get(`/functions/${id}`);
      return data;
    } catch (error) {
      console.error(`Ошибка при получении функции с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Создать новую функцию
   */
  async createFunction(functionData: FunctionCreateDTO): Promise<Function> {
    try {
      const { data } = await api.post('/functions', functionData);
      return data;
    } catch (error) {
      console.error('Ошибка при создании функции:', error);
      throw error;
    }
  },

  /**
   * Обновить функцию по ID
   */
  async updateFunction(id: number, functionData: FunctionUpdateDTO): Promise<Function> {
    try {
      const { data } = await api.put(`/functions/${id}`, functionData);
      return data;
    } catch (error) {
      console.error(`Ошибка при обновлении функции с ID ${id}:`, error);
      throw error;
    }
  },

  /**
   * Удалить функцию по ID
   */
  async deleteFunction(id: number): Promise<boolean> {
    try {
      const { data } = await api.delete(`/functions/${id}`);
      return data;
    } catch (error) {
      console.error(`Ошибка при удалении функции с ID ${id}:`, error);
      throw error;
    }
  }
};

export default functionsService;
```

### Создать страницу для управления функциями
```typescript
// AdminFunctionsPage.tsx
import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Space, 
  Typography, 
  Input, 
  Modal, 
  Form, 
  Switch, 
  message 
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined, 
  SearchOutlined, 
  ReloadOutlined 
} from '@ant-design/icons';
import functionsService, { Function, FunctionCreateDTO, FunctionUpdateDTO } from '../services/functionsService';

const { Title } = Typography;

const AdminFunctionsPage: React.FC = () => {
  const [functions, setFunctions] = useState<Function[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentFunction, setCurrentFunction] = useState<Function | null>(null);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchFunctions();
  }, []);

  const fetchFunctions = async () => {
    setLoading(true);
    try {
      const data = await functionsService.getFunctions();
      setFunctions(data);
    } catch (error) {
      message.error('Не удалось загрузить функции');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchText(value);
  };

  const filteredFunctions = functions.filter(
    (func) =>
      func.name.toLowerCase().includes(searchText.toLowerCase()) ||
      func.code.toLowerCase().includes(searchText.toLowerCase()) ||
      (func.description && func.description.toLowerCase().includes(searchText.toLowerCase()))
  );

  const showCreateModal = () => {
    setCurrentFunction(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const showEditModal = (func: Function) => {
    setCurrentFunction(func);
    form.setFieldsValue({
      name: func.name,
      code: func.code,
      description: func.description,
      is_active: func.is_active
    });
    setIsModalVisible(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await functionsService.deleteFunction(id);
      message.success('Функция успешно удалена');
      fetchFunctions();
    } catch (error) {
      message.error('Ошибка при удалении функции');
      console.error(error);
    }
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (currentFunction) {
        // Обновление существующей функции
        await functionsService.updateFunction(currentFunction.id, values as FunctionUpdateDTO);
        message.success('Функция успешно обновлена');
      } else {
        // Создание новой функции
        await functionsService.createFunction(values as FunctionCreateDTO);
        message.success('Функция успешно создана');
      }
      
      setIsModalVisible(false);
      fetchFunctions();
    } catch (error) {
      console.error('Не удалось сохранить функцию:', error);
    }
  };

  const handleModalCancel = () => {
    setIsModalVisible(false);
  };

  const columns = [
    {
      title: 'Название',
      dataIndex: 'name',
      key: 'name',
      sorter: (a: Function, b: Function) => a.name.localeCompare(b.name)
    },
    {
      title: 'Код',
      dataIndex: 'code',
      key: 'code'
    },
    {
      title: 'Описание',
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: 'Активна',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (is_active: boolean) => (is_active ? 'Да' : 'Нет')
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record: Function) => (
        <Space>
          <Button 
            icon={<EditOutlined />} 
            onClick={() => showEditModal(record)}
            type="primary"
            size="small"
          />
          <Button 
            icon={<DeleteOutlined />} 
            onClick={() => handleDelete(record.id)}
            danger
            size="small"
          />
        </Space>
      )
    }
  ];

  return (
    <div>
      <Space direction="vertical" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
          <Title level={3}>Управление функциями</Title>
          <Space>
            <Input
              placeholder="Поиск функций"
              prefix={<SearchOutlined />}
              onChange={(e) => handleSearch(e.target.value)}
              style={{ width: 300 }}
            />
            <Button 
              icon={<PlusOutlined />} 
              onClick={showCreateModal}
              type="primary"
            >
              Добавить функцию
            </Button>
            <Button 
              icon={<ReloadOutlined />} 
              onClick={fetchFunctions}
              loading={loading}
            />
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={filteredFunctions}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />

        <Modal
          title={currentFunction ? 'Редактировать функцию' : 'Создать функцию'}
          visible={isModalVisible}
          onOk={handleModalOk}
          onCancel={handleModalCancel}
          okText={currentFunction ? 'Обновить' : 'Создать'}
          cancelText="Отмена"
        >
          <Form
            form={form}
            layout="vertical"
          >
            <Form.Item
              name="name"
              label="Название"
              rules={[{ required: true, message: 'Введите название функции' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="code"
              label="Код"
              rules={[{ required: true, message: 'Введите код функции' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="description"
              label="Описание"
            >
              <Input.TextArea rows={4} />
            </Form.Item>
            <Form.Item
              name="is_active"
              label="Активна"
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>
          </Form>
        </Modal>
      </Space>
    </div>
  );
};

export default AdminFunctionsPage;
```

## 6. Дальнейшие шаги

1. Добавить API и компоненты для функциональных назначений
2. Расширить API оргструктуры для поддержки функциональных связей
3. Обновить визуализацию оргструктуры для отображения функциональных связей
4. Добавить фильтрацию и настройки отображения по типам связей 