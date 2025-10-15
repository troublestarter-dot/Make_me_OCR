# OCR Factory - Quick Start Guide

## Быстрый старт за 5 шагов

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

```bash
cp .env.example .env
```

Отредактируйте `.env` и добавьте необходимые ключи API:

```env
# Минимальная конфигурация
GOOGLE_SERVICE_ACCOUNT_FILE=service-account.json
CLOUDCONVERT_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

### 3. Настройка Google Service Account

1. Создайте Service Account в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Sheets API и Google Drive API
3. Скачайте JSON-ключ и сохраните как `service-account.json`
4. Создайте Google таблицу и предоставьте доступ service account email
5. Создайте папку в Google Drive и предоставьте доступ
6. Добавьте ID таблицы и папки в `.env`

### 4. Проверка установки

```bash
python setup.py
```

### 5. Запуск

```bash
python src/main.py
```

## Тестирование

1. Поместите PDF-файл в папку `data/input/`
2. Система автоматически:
   - Скопирует оригинал в `data/originals/`
   - Удалит пустые страницы
   - Выполнит OCR
   - Проанализирует GPT
   - Загрузит в Google Drive
   - Добавит запись в Google Sheets
   - Отправит webhook в Make.com (если настроено)

## Примеры использования

```bash
# Посмотреть примеры работы с модулями
python example_usage.py
```

## Структура данных в Google Sheets

### Document Index
После обработки документа в таблице появится строка с данными:

| Поле | Описание |
|------|----------|
| Document ID | Уникальный идентификатор |
| File Name | Имя файла |
| Timestamp | Время обработки |
| Page Count | Количество страниц |
| OCR Status | Статус OCR (completed/failed/skipped) |
| Supplier | Поставщик (определен GPT) |
| Document Type | Тип документа (invoice/receipt/contract...) |
| Duplicate | true/false |
| Drive Link | Ссылка на файл в Drive |

## Webhook Make.com

Если настроен `MAKE_WEBHOOK_URL`, система отправляет события:

```json
{
  "event_type": "document_processed",
  "timestamp": "2024-01-01T12:00:00",
  "data": {
    "document_id": "DOC_20240101_120000_abc123",
    "file_name": "invoice.pdf",
    "document_type": "invoice",
    "supplier": "Company Name",
    "duplicate": false
  }
}
```

## GPT-анализ

GPT автоматически:
- ✅ Определяет тип документа
- ✅ Извлекает поставщика/контрагента
- ✅ Классифицирует поставщиков по отраслям
- ✅ Обнаруживает аномалии
- ✅ Учится на ошибках
- ✅ Прогнозирует типы документов

## Мониторинг дубликатов

Система использует перцептивное хеширование (pHash) для поиска дубликатов:
- Сравнивает визуальное содержимое документов
- Порог схожести: 95% (настраивается)
- Работает даже если документы разного размера или качества

## Обработка ошибок

Все ошибки:
- Логируются в `logs/ocr_factory.log`
- Сохраняются в Google Sheets (Error Log)
- Анализируются GPT для выявления паттернов
- Отправляются в Make.com webhook

## Продвинутые настройки

### Изменить порог пустых страниц
```env
MIN_PAGE_CONTENT_THRESHOLD=0.05  # 5% контента минимум
```

### Изменить порог дубликатов
```env
DUPLICATE_SIMILARITY_THRESHOLD=0.95  # 95% схожести
```

### Изменить модель GPT
```env
OPENAI_MODEL=gpt-4-turbo  # или gpt-3.5-turbo для экономии
```

## Устранение неполадок

### "Configuration errors: GOOGLE_SERVICE_ACCOUNT_FILE is not set"
- Убедитесь, что файл `.env` создан
- Проверьте путь к service account JSON

### "Error connecting to Google Sheet"
- Проверьте, что Service Account имеет доступ к таблице
- Проверьте правильность GOOGLE_SHEETS_ID

### "OCR failed"
- Проверьте CloudConvert API ключ
- Проверьте баланс API credits

### Нет ответа от GPT
- Проверьте OpenAI API ключ
- Проверьте, что модель доступна для вашего аккаунта

## Поддержка

Для вопросов и проблем создайте issue в GitHub репозитории.
