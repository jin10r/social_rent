# Устранение неполадок

## Проблема: ConnectionRefusedError при запуске backend

### Описание проблемы
```
ConnectionRefusedError: [Errno 111] Connection refused
```

### Причины
1. База данных PostgreSQL еще не готова к работе
2. Неправильная конфигурация сети Docker
3. Проблемы с переменными окружения

### Решения

#### 1. Использование исправленной конфигурации
Мы внесли следующие изменения:

- **Добавлен healthcheck для базы данных** в `docker-compose.yml`
- **Улучшены зависимости** между сервисами
- **Добавлена retry логика** в `backend/database.py`
- **Создан скрипт ожидания** `backend/wait_for_db.py`

#### 2. Запуск с исправлениями
```bash
# Остановить все контейнеры
docker-compose down

# Удалить volumes (если нужно)
docker-compose down -v

# Запустить заново
docker-compose up --build
```

#### 3. Проверка статуса сервисов
```bash
# Проверить статус всех сервисов
docker-compose ps

# Проверить логи базы данных
docker-compose logs db

# Проверить логи backend
docker-compose logs backend
```

#### 4. Ручная проверка подключения к базе данных
```bash
# Подключиться к контейнеру backend
docker-compose exec backend python test_db_connection.py
```

#### 5. Проверка сети Docker
```bash
# Проверить сети
docker network ls

# Проверить подключение между контейнерами
docker-compose exec backend ping db
```

### Дополнительные настройки

#### Увеличение времени ожидания
Если база данных запускается медленно, можно увеличить время ожидания в `backend/database.py`:

```python
async def wait_for_database(max_retries: int = 60, delay: float = 5.0):
```

#### Проверка переменных окружения
Убедитесь, что в `docker-compose.yml` правильно настроены переменные:

```yaml
environment:
  DATABASE_URL: postgresql+asyncpg://postgres:postgres123@db:5432/social_rent
  DB_HOST: db
  DB_PORT: 5432
  DB_USER: postgres
  DB_PASSWORD: postgres123
  DB_NAME: social_rent
```

### Логи для диагностики

#### Успешный запуск
```
backend-1   | Starting database connection check with 30 max retries...
backend-1   | Attempt 1/30: Connecting to database...
backend-1   | ✅ Database is ready after 1 attempts
backend-1   | Starting database initialization...
backend-1   | Database initialization completed successfully
```

#### Проблемный запуск
```
backend-1   | ❌ Database connection attempt 1 failed: ConnectionRefusedError: [Errno 111] Connection refused
backend-1   | ⏳ Waiting 2.0 seconds before next attempt...
```

### Контакты
Если проблема не решается, проверьте:
1. Версию Docker и Docker Compose
2. Доступность портов
3. Логи всех сервисов