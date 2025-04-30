# Customer Complaints API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)

API сервис для автоматической обработки и классификации жалоб клиентов с использованием искусственного интеллекта.

## 🔍 Основные возможности

- **Автоматическая классификация** жалоб с помощью GPT-4
- **Анализ тональности** текста (положительная/нейтральная/отрицательная)
- **Спам-фильтрация** с использованием AI
- **Геолокация** по IP-адресу
- **Гибкая фильтрация** жалоб по параметрам
- **REST API** с документацией Swagger/OpenAPI

## 🛠 Технологии

| Технология         | Назначение                     |
|--------------------|--------------------------------|
| FastAPI            | Веб-фреймворк                 |
| SQLAlchemy         | ORM для работы с БД           |
| OpenAI GPT-4       | Классификация жалоб и спама   |
| APILayer           | Анализ тональности текста     |
| IP-API             | Геолокация по IP              |
| Uvicorn            | ASGI-сервер                   |

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.8+
- API ключи от OpenAI и APILayer

### Установка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/your-username/customer-complaints-api.git
cd customer-complaints-api

# 2. Настройте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Настройте переменные окружения
cp .env.example .env
Пример .env
  APILAYER_KEY=kmgZE3QZ0jbqdnlqQCOtZM6WzUG251mp
  OPENAI_API_KEY=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
  EXTERNAL_SERVICE_API_KEY=tfaGdu5JuMcgy3pa2JpViZ8T1GC7y6E5EBDwiOd2L50Td0
# Отредактируйте .env файл
Запуск
bash
uvicorn main:app --reload
После запуска откройте:

Документация API: http://localhost:8000/docs

Интерфейс Swagger: http://localhost:8000/redoc

📚 API Endpoints
Создание жалобы
POST /complaints/
Параметры:

X-Forwarded-For - IP адрес клиента

text - Текст жалобы

Получение жалобы
GET /complaints/{complaint_id}
Фильтрация жалоб
GET /complaints/
Параметры:

status (open/closed)

category (техническая/оплата/другое)

is_spam (true/false)

start_date, end_date (формат: YYYY-MM-DD)

limit, offset - пагинация

🗄 Структура данных
Поля жалобы:

json
{
  "id": 1,
  "text": "Не приходит SMS-код",
  "status": "open",
  "sentiment": "negative",
  "category": "техническая",
  "is_spam": false,
  "ip_address": "8.8.8.8",
  "location": "Moscow, Russia",
  "timestamp": "2023-10-01T12:00:00"
}
🌍 Примеры запросов
Создание жалобы
bash
curl -X POST "http://localhost:8000/complaints/" \
     -H "Content-Type: application/json" \
     -H "X-Forwarded-For: 8.8.8.8" \
     -d '{"text": "Не приходит SMS-код"}'
Фильтрация по дате
bash
curl "http://localhost:8000/complaints/?start_date=2023-10-01&end_date=2023-10-31"
📂 Структура проекта
customer-complaints-api/
├── main.py           # Основной код приложения
├── database.py       # Настройки базы данных
├── models.py         # SQLAlchemy модели
├── schemas.py        # Pydantic схемы
├── requirements.txt  # Зависимости
├── .env.example      # Шаблон переменных окружения
└── README.md         # Документация

Данные по телеграм-боту
  Токен:
  7385370202:AAGKmTcsRHKqlATpok01yoAV8NwDGj8mhyQ
  
  Ссылка:
  t.me/ppolzatest_bot

📜 Лицензия
Распространяется под MIT License.
