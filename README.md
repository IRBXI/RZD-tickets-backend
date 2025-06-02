# RZD-tickets-backend

## Стек бэкенда:

- FastAPI
- httpx
- Pydantic
- Tortoise ORM

### Для работы бекэнда необходимо сделать следующее:

Установить все необходимые библиотеки из файла ``requirements.txt``

Создать файл ``.env`` рядом c ``main.py``, имеющий следующие поля:

```env
SECRET_KEY
ALGORITHM for example HS256
ACCESS_TOKEN_EXPIRES_MINUTES
REFRESH_TOKEN_EXPIRES_MINUTES


POSTGRES_SERVER
POSTGRES_PORT
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
```

Для запуска контейнера с базой данных использовать команду:
```bash
docker-compose --env-file ./app/.env up
```

Для запуска тестов использовать команду:

```bash
pytest
```

Для запуска API в режиме отладки:

```bash
fastapi dev ./app/main.py
```

Для запуска API в ``production``:

```bash
fastapi run ./app/main.py
```

На ``localhost:8000/docs`` будет доступна open-api документация
