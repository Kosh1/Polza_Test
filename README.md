# Customer Complaints API

API сервис для обработки и классификации жалоб клиентов с использованием AI.

## Функциональность

- Прием и обработка жалоб клиентов
- Автоматическая классификация жалоб с помощью GPT-4
- Анализ тональности текста через APILayer
- Сохранение данных в SQLite
- REST API с FastAPI

## Технологии

- Python 3.8+
- FastAPI
- SQLAlchemy
- OpenAI GPT-4
- APILayer Sentiment Analysis

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/customer-complaints-api.git
cd customer-complaints-api
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env в корневой директории:
```
APILAYER_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key
```

## Запуск

```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу: http://localhost:8000

## API Endpoints

### POST /complaints/
Создание новой жалобы:
```bash
curl -X POST "http://localhost:8000/complaints/" \
     -H "Content-Type: application/json" \
     -d '{"text": "Не приходит SMS-код"}'
```

### GET /complaints/{complaint_id}
Получение информации о жалобе:
```bash
curl "http://localhost:8000/complaints/1"
```

## Документация API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Структура проекта

```
.
├── main.py           # Основной файл приложения
├── database.py       # Конфигурация базы данных
├── models.py         # Модели данных
├── requirements.txt  # Зависимости
└── README.md        # Документация
```

## Лицензия

MIT 