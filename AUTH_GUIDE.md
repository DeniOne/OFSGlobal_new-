### Памятка по связке Фронтенда и Бэкенда для Аутентификации (OFS Global)

Эта памятка описывает **текущую рабочую конфигурацию** для регистрации и входа пользователей. Если что-то опять сломается, сверяйся с ней в первую очередь!

**1. Бэкенд (`backend/full_api.py`):**

*   **Основной файл:** Вся логика API, включая аутентификацию, теперь находится в **`backend/full_api.py`**. Файл `auth_api.py` удален.
*   **Фреймворк:** Используется **FastAPI**.
*   **Запуск:** Сервер запускается через `uvicorn` (например, командой `uvicorn full_api:app`). Батник `run_servers.bat` настроен на запуск именно этого файла.
*   **Порт:** Бэкенд работает на порту **`8001`**! Мы перешли на него, так как порт `8000` был постоянно занят чем-то другим. Батник `run_servers.bat` также поправлен на запуск на порту `8001` и **без** флага `--reload`.
*   **База данных:** Используется SQLite файл `backend/full_api_new.db`. Таблица `user` для аутентификации находится там же.
*   **Эндпоинты аутентификации:**
    *   **Регистрация:** `POST /register`
        *   Принимает: JSON с полями `email`, `password`, `full_name`.
        *   Возвращает: JSON с данными созданного пользователя (модель `User`).
    *   **Логин:** `POST /login/access-token`
        *   Принимает: Данные в формате **`application/x-www-form-urlencoded`** (не JSON!) с полями `username` (это email) и `password`. Это важно, т.к. используется `OAuth2PasswordRequestForm` из FastAPI.
        *   Возвращает: JSON с `access_token` и `token_type`.
    *   **Проверка токена / Получение текущего пользователя:** `GET /users/me`
        *   Требует: Заголовок `Authorization: Bearer <токен>`.
        *   Возвращает: JSON с данными текущего пользователя (модель `User`).
*   **Префиксы:** Все эндпоинты (и аутентификации, и основного API типа `/staff/`, `/organizations/`) определены **БЕЗ** префикса `/api`.
*   **Роутер:** Эндпоинты аутентификации вынесены в `auth_router = APIRouter(tags=["Authentication"])` и подключены к основному приложению через `app.include_router(auth_router)`.

**2. Фронтенд (`frontend/`):**

*   **Конфигурация URL бэкенда:**
    *   Основной способ задания URL бэкенда — через файл **`.env`** в папке `frontend`. Там должна быть строка:
        ```
        VITE_API_URL=http://localhost:8001
        ```
        **(Важно: 8001!)**
    *   Файл `frontend/src/config.ts` использует эту переменную:
        ```typescript
        export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
        ```
        Значение из `.env` имеет приоритет! Если фронт стучится не туда, первым делом проверь `.env` и перезапусти Vite!
*   **API Сервис (`frontend/src/services/api.ts`):**
    *   Создает инстанс `axios` с `baseURL: API_URL`.
    *   Все вызовы API (например, `api.post('/register', ...)` или `api.get('/staff')`) используют **относительные пути** (без `http://...` и без `/api`). Axios сам подставит `baseURL`.
*   **Логика аутентификации (`frontend/src/hooks/useAuth.ts`):**
    *   Функция `login()` отправляет запрос на `/login/access-token`, используя `URLSearchParams`, чтобы данные были в формате `application/x-www-form-urlencoded`.
    *   Функция `checkAuth()` проверяет токен при загрузке защищенных страниц, делая запрос `GET /users/me`.
    *   Используется состояние `loading`, чтобы `ProtectedRoute` дожидался результата `checkAuth`.
*   **Защита роутов (`frontend/src/components/auth/ProtectedRoute.tsx`):**
    *   Получает `isAuthenticated` и `loading` из `useAuth()`.
    *   Показывает "Загрузка...", пока `loading === true`.
    *   Редиректит на `/login`, если `loading === false` и `isAuthenticated === false`.
    *   Показывает дочерний компонент, если `loading === false` и `isAuthenticated === true`.

**3. Схема взаимодействия (для аутентификации):**

1.  Пользователь вводит данные в форму (Регистрация или Логин).
2.  Компонент страницы (`RegisterPage` или `LoginPage`) вызывает соответствующую функцию из `useAuth`.
3.  Функция `useAuth` вызывает `api.post('/register', jsonData)` или `api.post('/login/access-token', formData)`.
4.  `axios` (из `api.ts`) берет `baseURL` (`http://localhost:8001`) и добавляет относительный путь (`/register` или `/login/access-token`).
5.  Запрос уходит **напрямую** на `http://localhost:8001/register` или `http://localhost:8001/login/access-token`. **Прокси Vite НЕ ИСПОЛЬЗУЕТСЯ** для этих запросов.
6.  Бэкенд (`full_api.py`) обрабатывает запрос и возвращает ответ.
7.  `useAuth` обрабатывает ответ (сохраняет токен в `localStorage`, меняет `isAuthenticated`).
8.  При переходе на защищенный роут `ProtectedRoute` ждет завершения `checkAuth` (который делает `GET /users/me`) и решает, пускать или нет.

**4. Ключевые моменты и грабли, на которые наступали:**

*   **Порт бэкенда:** Убедись, что бэкенд запущен на **8001**.
*   **`.env` файл:** `VITE_API_URL` в `frontend/.env` **переопределяет** `config.ts`. Проверяй его в первую очередь, если фронт стучится не туда.
*   **Перезапуск Vite:** После изменений в `.env`, `vite.config.ts` или `config.ts` **всегда перезапускай** сервер Vite (`npm run dev`).
*   **Формат данных для логина:** На бэке `/login/access-token` ждет `x-www-form-urlencoded`. Фронт должен использовать `URLSearchParams`.
*   **Проверка токена:** Используется эндпоинт `GET /users/me`.
*   **Асинхронность на фронте:** `ProtectedRoute` должен ждать завершения начальной проверки аутентификации (`checkAuth`), используя `loading` состояние.
*   **Кэш браузера:** Иногда помогает жесткая перезагрузка (`Ctrl+Shift+R`).