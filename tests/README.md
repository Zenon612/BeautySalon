# Тестирование проекта BeautySalon

## Обзор

Проект покрыт интеграционными тестами для всех CRUD эндпоинтов API. Тесты используют SQLite in-memory базу данных для скорости и изоляции.

## Структура тестов

```
tests/
├── conftest.py          # Фикстуры и конфигурация pytest
├── test_auth.py         # Тесты аутентификации и авторизации
├── test_contact.py      # Тесты контактной информации
├── test_health.py       # Тесты health check
├── test_masters.py      # Тесты мастеров
├── test_portfolio.py    # Тесты портфолио
└── test_service.py      # Тесты услуг
```

## Запуск тестов

### Быстрый запуск

```bash
# Активировать виртуальное окружение
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Запустить все тесты
pytest

# Запустить все тесты с подробным выводом
pytest -v

# Запустить тесты с покрытием (требуется pytest-cov)
pytest --cov=app --cov-report=html
```

### Запуск отдельных тестов

```bash
# Все тесты аутентификации
pytest tests/test_auth.py -v

# Конкретный тест
pytest tests/test_auth.py::TestAuthLogin::test_login_success -v

# Тесты по ключевому слову
pytest -k "login" -v

# Тесты с маркером (если добавлены)
pytest -m asyncio -v
```

## Конфигурация

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
addopts = -v --tb=short -p no:warnings
```

### .env.test

Файл с тестовыми настройками:
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=test-secret-key-for-testing-only-min-32-characters-long
DEBUG=true
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
```

## Фикстуры

### Основные фикстуры (conftest.py)

| Фикстура | Описание |
|----------|----------|
| `client` | HTTP клиент для тестирования API |
| `db_session` | Тестовая сессия БД с автосбросом |
| `admin_user` | Пользователь с правами администратора |
| `regular_user` | Обычный пользователь |
| `admin_token` | JWT токен администратора |
| `user_token` | JWT токен обычного пользователя |
| `auth_headers` | Заголовки с токеном администратора |
| `user_auth_headers` | Заголовки с токеном пользователя |
| `test_services` | Тестовые услуги (3 активные) |
| `test_masters` | Тестовые мастера (3 активных) |
| `test_portfolio` | Тестовые элементы портфолио (3 элемента) |
| `test_contact` | Тестовая контактная информация |

### Пример использования фикстур

```python
import pytest

@pytest.mark.asyncio
async def test_example(client, auth_headers, test_services):
    # client - HTTP клиент
    # auth_headers - заголовки авторизации администратора
    # test_services - тестовые данные
    
    response = await client.post(
        "/api/v1/services",
        json={"name": "Test", "category": "hair", "price": 1000},
        headers=auth_headers
    )
    assert response.status_code == 201
```

## Покрытие тестами

### Auth (test_auth.py)
- ✅ Регистрация пользователя
- ✅ Вход в систему
- ✅ Валидация токенов
- ✅ Права администратора
- ✅ Защита эндпоинтов

### Services (test_service.py)
- ✅ Получение списка услуг (с пагинацией и фильтрами)
- ✅ Получение услуги по ID
- ✅ Создание услуги (admin only)
- ✅ Обновление услуги (admin only)
- ✅ Деактивация услуги (admin only)

### Masters (test_masters.py)
- ✅ Получение списка мастеров
- ✅ Получение мастера по ID
- ✅ Создание мастера (admin only)
- ✅ Обновление мастера (admin only)
- ✅ Деактивация мастера (admin only)

### Portfolio (test_portfolio.py)
- ✅ Получение списка портфолио
- ✅ Получение элемента по ID
- ✅ Создание элемента (admin only)
- ✅ Обновление элемента (admin only)
- ✅ Деактивация элемента (admin only)

### Contact (test_contact.py)
- ✅ Получение контактной информации
- ✅ Создание контакта (admin only)
- ✅ Обновление контакта (admin only)
- ✅ Обработка отсутствия контакта

### Health (test_health.py)
- ✅ Проверка состояния API
- ✅ Проверка подключения к БД

## Принципы тестирования

### 1. Изоляция тестов
Каждый тест работает в отдельной транзакции, которая откатывается после завершения. Это обеспечивает независимость тестов друг от друга.

### 2. Использование фикстур
Все общие данные (пользователи, услуги, мастера) создаются через фикстуры в `conftest.py`.

### 3. Асинхронность
Все тесты асинхронные (`@pytest.mark.asyncio`), используется `httpx.AsyncClient`.

### 4. Полнота проверок
Каждый тест проверяет:
- Статус код ответа
- Структуру данных
- Конкретные значения полей
- Обработку ошибок

## Добавление новых тестов

### Шаг 1: Создать файл теста
```python
# tests/test_new_entity.py
import pytest

class TestNewEntity:
    """Тесты для новой сущности."""
    
    @pytest.mark.asyncio
    async def test_example(self, client, auth_headers):
        response = await client.get("/api/v1/new-entity")
        assert response.status_code == 200
```

### Шаг 2: Добавить фикстуру (если нужна)
```python
# tests/conftest.py
@pytest_asyncio.fixture(scope="function")
async def test_new_entities(db_session):
    entities = [...]
    db_session.add_all(entities)
    await db_session.commit()
    yield entities
    await db_session.delete_all(entities)
    await db_session.commit()
```

### Шаг 3: Запустить тесты
```bash
pytest tests/test_new_entity.py -v
```

## Устранение проблем

### Тесты падают с ошибкой авторизации
Проверьте, что фикстуры `admin_user` и `regular_user` создают пользователей с правильными паролями.

### Тесты не изолированы
Убедитесь, что `clean_db` фикстура помечена как `autouse=True` и выполняется перед каждым тестом.

### Медленное выполнение тестов
- Используйте SQLite in-memory (`sqlite+aiosqlite:///:memory:`)
- Отключите логирование SQLAlchemy (`echo=False`)
- Используйте фикстуры с правильным `scope`

## Статистика

- **Всего тестов:** 75
- **Время выполнения:** ~30 секунд
- **Покрытие:** Все CRUD эндпоинты
- **Статус:** ✅ Все тесты проходят
