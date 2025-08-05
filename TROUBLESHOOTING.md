# Troubleshooting Guide

## Ошибка подключения к базе данных

### Проблема
```
ConnectionRefusedError: [Errno 111] Connection refused
```

### Причины
1. База данных PostgreSQL не запущена
2. Неправильные настройки подключения
3. База данных еще не готова к подключению при запуске приложения

### Решения

#### 1. Использование Docker Compose (рекомендуется)

```bash
# Остановить все контейнеры
docker compose down

# Удалить старые тома (если нужно)
docker volume rm workspace_postgres_data

# Запустить с нуля
docker compose up --build
```

#### 2. Локальный запуск без Docker

##### Установка PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql postgis
brew services start postgresql
```

**Windows:**
Скачайте и установите PostgreSQL с официального сайта.

##### Настройка базы данных

```bash
# Создать пользователя и базу данных
sudo -u postgres createuser --interactive
sudo -u postgres createdb social_rent

# Применить схему базы данных
sudo -u postgres psql -d social_rent -f init.sql
```

##### Запуск приложения

```bash
# Установить зависимости
cd backend
pip install -r requirements.txt

# Запустить приложение
python start_local.py
```

#### 3. Проверка подключения

```bash
# Проверить статус PostgreSQL
sudo systemctl status postgresql

# Проверить подключение
psql -h localhost -U postgres -d social_rent
```

### Улучшения в коде

#### 1. Ожидание готовности базы данных
Добавлена функция `wait_for_database()` в `database.py`, которая:
- Пытается подключиться к базе данных с интервалами
- Логирует попытки подключения
- Продолжает попытки до успеха или исчерпания лимита

#### 2. Улучшенная конфигурация пула соединений
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Проверка здоровья соединений
    pool_recycle=300,    # Пересоздание соединений каждые 5 минут
    pool_size=10,        # Размер пула
    max_overflow=20,     # Дополнительные соединения
)
```

#### 3. Healthcheck в Docker Compose
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d social_rent"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 30s
```

#### 4. Улучшенные зависимости
```yaml
depends_on:
  db:
    condition: service_healthy
```

### Логирование

Добавлено детальное логирование для отслеживания проблем:

```python
import logging
logger = logging.getLogger(__name__)

# В database.py
logger.info("Waiting for database to be ready...")
logger.warning(f"Database connection attempt {attempt} failed: {e}")
logger.error(f"Failed to connect to database after {max_retries} attempts")
```

### Переменные окружения

Убедитесь, что установлены правильные переменные окружения:

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent"
export BOT_TOKEN="your_bot_token"
export WEBAPP_URL="http://localhost:3000"
```

### Проверка работоспособности

После запуска проверьте:

1. **Backend API:**
```bash
curl http://localhost:8001/health
```

2. **База данных:**
```bash
curl http://localhost:8001/
```

### Дополнительные советы

1. **Проверьте порты:** Убедитесь, что порт 5432 не занят другими сервисами
2. **Firewall:** Проверьте настройки файрвола
3. **Логи:** Проверьте логи PostgreSQL: `sudo tail -f /var/log/postgresql/postgresql-*.log`
4. **Перезапуск:** Иногда помогает полный перезапуск системы

### Контакты

Если проблемы продолжаются, проверьте:
- Логи приложения
- Логи PostgreSQL
- Настройки сети
- Версии зависимостей