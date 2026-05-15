## FastAPI Session-Based Authentication.

#### Данный проект демонстрирует реализацию session-based authentication на FastAPI

Проект создан как учебная демонстрация современного backend-подхода к реализации серверных сессий с хранением session state в Redis.

### Проект реализует:
* регистрацию пользователей
* login и logout
* хранение сессий в Redis
* аутентификацию через HttpOnly cookies
* sliding sessions (обновление времени жизни сессии при активности пользователя)
* безопасное хранение session token через SHA-256 hash

### Технологии
* Python 3.12
* FastAPI
* PostgreSQL
* SQLAlchemy Async
* Redis Async
* Docker / Docker Compose
* Passlib (bcrypt)


## Архитектура аутентификации
Проект использует server-side session authentication.


#### Логин. После успешного логина:

1. Backend генерирует криптографически безопасный session token через secrets.token_urlsafe()
2. Токен хешируется через SHA-256
3. Хеш сохраняется в Redis, ключ -хеш токена: значение user_id
4. Оригинальный token отправляется клиенту в HttpOnly cookie 


#### Последующие запросы. При каждом запросе:

1. Браузер автоматически отправляет cookie
2. Backend извлекает session token
3. Хеширует token
4. Проверяет наличие сессии в Redis
5. Возвращает текущего пользователя SQL-запрос в БД по индексированному полю.


#### Sliding Sessions. При активности пользователя:

1. Redis TTL продлевается
2. Cookie expiration обновляется
3. Это предотвращает сброс активного пользователя по абсолютному тайм-ауту.

#### Logout. При logout:
1. сессия удаляется из Redis
2. cookie удаляется в браузере