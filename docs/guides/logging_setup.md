# Настройка логирования в проекте OFS Global

## Логирование в бэкенде (Python/FastAPI)

### Установка требуемых библиотек
```bash
pip install loguru python-json-logger
```

### Настройка логирования в FastAPI

Добавьте следующий код в файл `backend/app/core/logging.py`:

```python
import os
import sys
from pathlib import Path
from loguru import logger
import json
from datetime import datetime

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Настройка формата логов
def format_record(record):
    """
    Пользовательский формат для логов
    """
    timestamp = datetime.fromtimestamp(record["time"].timestamp()).strftime("%Y-%m-%d %H:%M:%S")
    log_data = {
        "timestamp": timestamp,
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }
    
    # Добавляем дополнительные атрибуты, если они есть
    if record["extra"]:
        log_data["extra"] = record["extra"]
    
    # Форматируем исключение, если оно есть
    if record["exception"]:
        log_data["exception"] = record["exception"]
    
    return json.dumps(log_data)

# Конфигурация логгера
def setup_logging():
    # Удаляем стандартный обработчик
    logger.remove()
    
    # Консольный вывод для разработки
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format="{time} | {level} | {message} | {extra}",
        backtrace=True,
        diagnose=True,
    )
    
    # Файлы логов
    logger.add(
        LOG_DIR / "app.log",
        rotation="10 MB",
        retention="7 days",
        level=LOG_LEVEL,
        format=format_record,
        serialize=True,
    )
    
    # Отдельный файл для ошибок
    logger.add(
        LOG_DIR / "error.log",
        rotation="10 MB",
        retention="7 days",
        level="ERROR",
        format=format_record,
        serialize=True,
    )
    
    return logger

# Инициализация логгера
app_logger = setup_logging()
```

### Использование в приложении

В файле `backend/app/main.py` импортируйте логгер:

```python
from app.core.logging import app_logger as logger

# Пример использования
@app.on_event("startup")
async def startup_event():
    logger.info("Приложение запущено", extra={"environment": settings.ENVIRONMENT})

# Пример использования в эндпоинтах
@app.get("/health")
async def health_check():
    logger.debug("Запрос к эндпоинту health_check")
    return {"status": "ok"}
```

## Логирование во фронтенде (TypeScript/React)

### Установка библиотеки
```bash
npm install --save loglevel
```

### Настройка логирования

Создайте файл `frontend/src/utils/logger.ts`:

```typescript
import log from 'loglevel';

// Получаем режим из переменных окружения
const isProduction = import.meta.env.PROD;

// Устанавливаем уровень логирования
if (isProduction) {
  log.setLevel(log.levels.WARN);  // В продакшене только предупреждения и ошибки
} else {
  log.setLevel(log.levels.DEBUG); // В разработке все логи
}

// Расширенное логирование с дополнительной информацией
export const logger = {
  debug: (message: string, data?: any) => {
    if (data) {
      log.debug(`${message}`, data);
    } else {
      log.debug(message);
    }
  },
  info: (message: string, data?: any) => {
    if (data) {
      log.info(`${message}`, data);
    } else {
      log.info(message);
    }
  },
  warn: (message: string, data?: any) => {
    if (data) {
      log.warn(`${message}`, data);
    } else {
      log.warn(message);
    }
  },
  error: (message: string, error?: any) => {
    if (error) {
      log.error(`${message}`, error);
    } else {
      log.error(message);
    }
  }
};

// Перехват необработанных ошибок
window.addEventListener('error', (event) => {
  logger.error('Необработанная ошибка:', {
    message: event.message,
    source: event.filename,
    lineNumber: event.lineno,
    columnNumber: event.colno,
    stack: event.error?.stack
  });
});

export default logger;
```

### Использование в компонентах

```tsx
import React, { useEffect } from 'react';
import { logger } from '../utils/logger';

const ExampleComponent: React.FC = () => {
  useEffect(() => {
    logger.info('ExampleComponent был смонтирован');
    
    return () => {
      logger.debug('ExampleComponent был размонтирован');
    };
  }, []);
  
  const handleClick = () => {
    try {
      // Какая-то логика
      logger.debug('Кнопка была нажата');
    } catch (error) {
      logger.error('Ошибка при обработке клика', error);
    }
  };
  
  return (
    <button onClick={handleClick}>Нажми меня</button>
  );
};

export default ExampleComponent;
```

## Анализ логов

### Инструменты для анализа логов
1. Kibana + Elasticsearch - для продакшн-окружения
2. [Grafana Loki](https://grafana.com/oss/loki/) - легковесная альтернатива
3. [LogDNA](https://www.logdna.com/) - облачное решение

### Примеры запросов для анализа

#### Поиск ошибок
```
level:ERROR
```

#### Ошибки в конкретном модуле
```
level:ERROR module:app.api.endpoints.divisions
```

#### Запросы конкретного пользователя
```
extra.user_id:12345
```

## Рекомендации

1. Логируйте важные бизнес-события и ошибки
2. Избегайте логирования чувствительной информации (пароли, токены)
3. Используйте структурированное логирование (JSON)
4. Регулярно проверяйте и анализируйте логи
5. Настройте оповещения о критических ошибках 