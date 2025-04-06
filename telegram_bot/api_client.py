import logging
import aiohttp
from typing import List, Dict, Any, Optional
from config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
config = Config()

class ApiClient:
    """Класс для взаимодействия с API основной системы"""
    
    def __init__(self):
        self.base_url = config.API_URL
        self.webhook_endpoint = config.API_WEBHOOK_ENDPOINT
        self.token_validation_endpoint = config.API_TOKEN_VALIDATION_ENDPOINT
        self.organizations_endpoint = config.API_ORGANIZATIONS_ENDPOINT
        
        # Новые эндпоинты для работы с обновленной структурой API
        self.positions_endpoint = f"{self.base_url}/positions"
        self.divisions_endpoint = f"{self.base_url}/divisions"
        self.staff_endpoint = f"{self.base_url}/staff"
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """
        Получает список всех должностей из основной системы
        
        Returns:
            List[Dict[str, Any]]: Список словарей с данными о должностях
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.positions_endpoint) as response:
                    if response.status == 200:
                        positions = await response.json()
                        logger.info(f"Получено {len(positions)} должностей из API")
                        return positions
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка при получении должностей: {response.status} - {error_text}")
                        return []
        except Exception as e:
            logger.error(f"Исключение при получении должностей: {str(e)}")
            return []
    
    async def get_position_by_id(self, position_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о должности по ID
        
        Args:
            position_id: ID должности
            
        Returns:
            Optional[Dict[str, Any]]: Словарь с данными о должности или None при ошибке
        """
        position_endpoint = f"{self.positions_endpoint}/{position_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(position_endpoint) as response:
                    if response.status == 200:
                        position = await response.json()
                        logger.info(f"Получена должность с ID {position_id}")
                        return position
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка при получении должности: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logger.error(f"Исключение при получении должности: {str(e)}")
            return None
    
    async def get_organizations(self) -> List[Dict[str, Any]]:
        """
        Получает список всех организаций из основной системы
        
        Returns:
            List[Dict[str, Any]]: Список словарей с данными об организациях
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.organizations_endpoint) as response:
                    if response.status == 200:
                        organizations = await response.json()
                        logger.info(f"Получено {len(organizations)} организаций из API")
                        return organizations
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка при получении организаций: {response.status} - {error_text}")
                        # Возвращаем заглушку в случае ошибки
                        logger.info("Возвращаем заглушку для организаций")
                        return [
                            {"id": 1, "name": "OFS Global", "description": "Основная организация"}
                        ]
        except Exception as e:
            logger.error(f"Исключение при получении организаций: {str(e)}")
            # Возвращаем заглушку в случае ошибки соединения
            logger.info("Возвращаем заглушку для организаций")
            return [
                {"id": 1, "name": "OFS Global", "description": "Основная организация"}
            ]
    
    async def get_divisions(self) -> List[Dict[str, Any]]:
        """
        Получает список всех отделов (divisions) из основной системы
        
        Returns:
            List[Dict[str, Any]]: Список словарей с данными об отделах
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.divisions_endpoint) as response:
                    if response.status == 200:
                        divisions = await response.json()
                        logger.info(f"Получено {len(divisions)} отделов из API")
                        return divisions
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка при получении отделов: {response.status} - {error_text}")
                        return []
        except Exception as e:
            logger.error(f"Исключение при получении отделов: {str(e)}")
            return []
    
    async def send_employee_data(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Отправляет данные о сотруднике в основную систему
        
        Args:
            employee_data: Словарь с данными сотрудника
            
        Returns:
            Dict[str, Any]: Результат операции
        """
        # Адаптация данных под новую структуру API
        # Преобразуем "division" в "division" если есть
        if "division" in employee_data and "division" not in employee_data:
            employee_data["division"] = employee_data.pop("division")
        
        # Убедимся, что используем правильные поля
        adapted_data = {
            "name": employee_data.get("name", ""),
            "email": employee_data.get("email", ""),
            "phone": employee_data.get("phone", ""),
            "position": employee_data.get("position", ""),
            "division_id": employee_data.get("division_id", None),
            "telegram_id": employee_data.get("telegram_id", ""),
            "organization_id": employee_data.get("organization_id", 1),
            "photo_path": employee_data.get("photo_path", None),
            "competencies": employee_data.get("competencies", [])
        }
        
        # Удаляем None поля, чтобы не отправлять их в API
        adapted_data = {k: v for k, v in adapted_data.items() if v is not None}
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Отправка данных сотрудника: {adapted_data}")
                async with session.post(self.webhook_endpoint, json=adapted_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Данные сотрудника успешно отправлены: {result}")
                        return {
                            "success": True,
                            "message": "Данные успешно отправлены",
                            "result": result
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка при отправке данных сотрудника: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "message": f"Ошибка {response.status}: {error_text}",
                            "result": None
                        }
        except Exception as e:
            error_message = str(e)
            logger.error(f"Исключение при отправке данных сотрудника: {error_message}")
            return {
                "success": False,
                "message": f"Ошибка соединения: {error_message}",
                "result": None
            }
    
    async def validate_token(self, token: str) -> bool:
        """
        Проверяет валидность токена бота
        
        Args:
            token: Токен для проверки
            
        Returns:
            bool: True если токен валиден, False в противном случае
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.token_validation_endpoint, 
                    json={"token": token}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("status") == "valid":
                            logger.info("Токен успешно валидирован")
                            return True
                        else:
                            logger.error(f"Неверный статус валидации токена: {result}")
                            return False
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка валидации токена: {response.status} - {error_text}")
                        # В случае ошибки разрешаем использование бота
                        logger.warning("Временно разрешаем использование бота без валидации токена")
                        return True
        except Exception as e:
            logger.error(f"Исключение при валидации токена: {str(e)}")
            # В случае ошибки соединения разрешаем использование бота
            logger.warning("Временно разрешаем использование бота из-за ошибки соединения")
            return True
            
    async def create_staff(self, staff_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Создаёт нового сотрудника в системе через эндпоинт /staff
        
        Args:
            staff_data: Словарь с данными сотрудника
            
        Returns:
            Dict[str, Any]: Результат операции
        """
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Создание сотрудника через эндпоинт /staff: {staff_data}")
                async with session.post(self.staff_endpoint, json=staff_data) as response:
                    if response.status in (200, 201):
                        result = await response.json()
                        logger.info(f"Сотрудник успешно создан: {result}")
                        return {
                            "success": True,
                            "message": "Сотрудник успешно создан",
                            "result": result
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка при создании сотрудника: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "message": f"Ошибка {response.status}: {error_text}",
                            "result": None
                        }
        except Exception as e:
            error_message = str(e)
            logger.error(f"Исключение при создании сотрудника: {error_message}")
            return {
                "success": False,
                "message": f"Ошибка соединения: {error_message}",
                "result": None
            }
            
    async def generate_invitation_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерирует инвайт-код для сотрудника через API
        
        Args:
            data: Словарь с данными для генерации инвайт-кода
                {
                    "position_id": int,
                    "division_id": int или null,
                    "telegram_id": str,
                    "user_full_name": str,
                    "organization_id": int
                }
            
        Returns:
            Dict[str, Any]: Результат операции с кодом приглашения
        """
        invitation_endpoint = f"{self.base_url}/telegram-bot/generate-invitation"
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Генерация инвайт-кода: {data}")
                async with session.post(invitation_endpoint, json=data) as response:
                    if response.status in (200, 201):
                        result = await response.json()
                        logger.info(f"Инвайт-код успешно сгенерирован: {result}")
                        return {
                            "success": True,
                            "message": "Инвайт-код успешно сгенерирован",
                            "code": result.get("code"),
                            "expires_at": result.get("expires_at"),
                            "result": result
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка при генерации инвайт-кода: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "message": f"Ошибка {response.status}: {error_text}",
                            "result": None
                        }
        except Exception as e:
            error_message = str(e)
            logger.error(f"Исключение при генерации инвайт-кода: {error_message}")
            return {
                "success": False,
                "message": f"Ошибка соединения: {error_message}",
                "result": None
            }
            
    async def validate_invitation_code(self, code: str, telegram_id: int) -> Dict[str, Any]:
        """
        Проверяет валидность инвайт-кода через API
        
        Args:
            code: Код приглашения
            telegram_id: ID пользователя в Telegram
            
        Returns:
            Dict[str, Any]: Результат проверки
        """
        validation_endpoint = f"{self.base_url}/telegram-bot/validate-invitation"
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Проверка инвайт-кода: {code} для пользователя {telegram_id}")
                async with session.post(
                    validation_endpoint, 
                    json={"code": code, "telegram_id": telegram_id}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Инвайт-код успешно проверен: {result}")
                        return {
                            "success": True,
                            "message": "Инвайт-код действителен",
                            "position": result.get("position"),
                            "division": result.get("division"),
                            "organization": result.get("organization"),
                            "result": result
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Ошибка при проверке инвайт-кода: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "message": f"Ошибка {response.status}: {error_text}",
                            "result": None
                        }
        except Exception as e:
            error_message = str(e)
            logger.error(f"Исключение при проверке инвайт-кода: {error_message}")
            return {
                "success": False,
                "message": f"Ошибка соединения: {error_message}",
                "result": None
            }

# Создаем глобальный экземпляр API клиента
api_client = ApiClient() 