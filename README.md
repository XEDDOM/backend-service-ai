# Backend-сервис для лендинг-презентации разработчика

Backend-сервис с REST API, интеграцией AI (OpenAI) и файловой системой хранения данных.

## 1. Как запустить проект

``` bash
# Клонировать репозиторий и перейти в папку
git clone https://github.com/XEDDOM/backend-service-ai.git
cd backend-service-ai

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env

# Запуск сервера
uvicorn app.main:app --reload --port 8000
```

### После запуска

Открыть файл **index.html**

## 2. Стек технологий

**Backend**: Python/FastAPI

**AI**: OpenAI API (модель gpt-3.5-turbo)

**Frontend**: HTML/CSS/JS - для демонстрации взаимодействия с API

## 3. Архитектура

```
app/
├── main.py
├── core/
│    └── config.py
├── routers/
│   └── contact.py
├── schemas/
│   └── contact.py
├── services/
│   ├── contact_service.py
│   ├── ai_service.py
│   └── email_service.py
├── repositories/
│   └── file_repository.py
└── utils/
    └── rate_limiter.py
```

### Паттерны проектирования

- **Слоистая архитектура (Layered Architecture)**: `Controllers > Services > Repositories`. Четкое разделение ответственности: роутеры не знают о деталях хранения, сервисы не знают о HTTP
- **Dependency Inversion**: сервисы зависят от абстракций (репозитории), а не от конкретных реализаций
- **Graceful Degradation**: AI-сервис всегда возвращает fallback-ответ, никогда не падает
- **Repository Pattern**: вся работа с файлами инкапсулирована в `file_repository.py` - легко заменить на БД

### Почему FastAPI?

1. Встроенная генерация Swagger/OpenAPI
2. Строгая валидация через Pydantic "из коробки"
3. Нативная async-поддержка (важно для I/O-операций с AI и SMTP)
4. Высокая производительность (на уровне Node.js/Go)

## 4. Реализация API

### Эндпоинты

`POST /api/contact` - Отправка формы обратной связи

`GET /api/health` - Проверка статуса сервиса

`GET /api/metrics` - Статистика обращений

### Валидация входных данных

- `name`: строка, 2–50 символов
- `phone`: строка (пример: +79876543210)
- `email`: валидный email (Pydantic EmailStr)
- `comment`: строка, 10–1000 символов

### Пример запроса (curl)

``` bash
curl -X 'POST' \
  'http://localhost:8000/api/contact' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Иван",
  "phone": "+79876543210",
  "email": "test@test.com",
  "comment": "Хочу обсудить разработку!"
}'
```

### Пример успешного ответа (200 OK)

``` bash
{
  "status": "success",
  "message": "Ваша заявка успешно отправлена!",
  "ai_sentiment": "positive",
  "ai_generated_reply": "Здравствуйте, Иван! Спасибо за интерес к сотрудничеству..."
}
```

### Примеры ошибок

- **422 Unprocessable Entity** - невалидные данные (например, короткий комментарий)
- **429 Too Many Requests** - превышен rate limit
- **500 Internal Server Error** - глобальный error handler

### Другие примеры запросов

``` bash
curl http://localhost:8000/api/health
# Ответ: {"status": "ok"}
```

``` bash
curl http://localhost:8000/api/metrics
# Ответ: {"total_requests": 15, "successful_contacts": 12, "ai_fallbacks": 1, "last_updated": "..."}
```

## 5. AI-интеграция

### Какие AI-инструменты и для чего

Используется OpenAI API (gpt-3.5-turbo) для двух задач за один запрос:

1. Анализ тональности комментария (positive/negative/neutral)
2. Генерация вежливого ответа пользователю на русском языке

### Промпт

```
Проанализируй тональность сообщения пользователя (positive, negative, neutral) 
и сгенерируй вежливый, профессиональный ответ на русском языке.
Верни результат СТРОГО в формате JSON: {"sentiment": "...", "reply": "..."}
Сообщение пользователя: "{comment}"
```

### Fallback-механизм

Реализован в `app/services/ai_service.py`:

- Если нет API-ключа > возвращается дефолтный нейтральный ответ
- Если таймаут / сеть недоступна > fallback
- Если OpenAI вернул ошибку (5xx, rate limit) > fallback
- Если ответ не парсится как JSON > fallback

## 6. Что сделано с помощью AI

### Сгенерировано AI

- Базовый boilerplate для FastAPI-приложения и структура папок
- Pydantic-схемы с валидацией полей
- Регулярные выражения для валидации телефона
- CSS-стили для frontend (градиенты, анимации)

### Использованные промпты (примеры)

1. *"Напиши Pydantic-модель для валидации контактной формы с именем, телефоном в международном формате, email и комментарием"*
2. *"Сгенерируй regex для валидации телефона в формате +79876543210"*
3. *"Напиши CSS для адаптивной формы с градиентным фоном и анимациями"*

### Что исправлял вручную

1. **Потокобезопасность файловых операций**: AI сгенерировал код с обычным open()/write(), который не безопасен при конкурентных запросах. Заменил на filelock.FileLock для корректной работы в async-среде.
2. **Graceful fallback для OpenAI**: AI предложил просто пробрасывать исключения. Переписал логику так, чтобы любая ошибка AI приводила к безопасному fallback-ответу.
3. **Структура сервисов**: AI поместил всю бизнес-логику в роутер. Вынес в отдельный contact_service.py как оркестратор — для соответствия слоистой архитектуре.
4. **Детектирование fallback**: добавил явный флаг is_fallback в ответ AI-сервиса, чтобы корректно считать метрики.

## 7. Хранение данных

### Логи запросов

- **Файл**: `logs/app.log`
- **Что логируется**: старт приложения, все ошибки (с `exc_info`), вызовы fallback, неудачные отправки email, предупреждения

### Rate Limiting

- **Файл**: `data/rate_limit.json`
- **Алгоритм**: скользящее окно (sliding window). При каждом запросе удаляются временные метки старше `RATE_LIMIT_WINDOW_SECONDS`, затем проверяется количество оставшихся.
- **Потокобезопасность**: `filelock.FileLock` гарантирует атомарность чтения-изменения-записи при конкурентных запросах.
- **Параметры**: 5 запросов за 60 секунд (настраивается через `.env`)

### Статистика

- **Файл**: `data/stats.json`
- **Структура**:
``` bash
{
  "total_requests": 15,
  "successful_contacts": 12,
  "ai_fallbacks": 1,
  "last_updated": "2026-07-18T10:30:00"
}
```
- **Доступ**: через эндпоинт `GET /api/metrics`
- **Потокобезопасность**: отдельный `FileLock` для `stats.json`