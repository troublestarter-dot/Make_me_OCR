# Make.com Сценарий для OCR Factory

## Обзор

Этот документ описывает, как настроить автоматизацию в Make.com для работы с OCR Factory.

## Архитектура интеграции

```
OCR Factory → Make.com Webhook → Автоматизация
```

## Сценарий 1: Обработка документов

### Модули Make.com

1. **Webhook** (Trigger)
   - URL: Скопируйте и добавьте в `.env` как `MAKE_WEBHOOK_URL`
   - Метод: POST
   - Ожидает JSON с событиями от OCR Factory

2. **Router** (Маршрутизатор)
   - Направляет события по типам:
     - `document_processed` → Обработка успешного документа
     - `duplicate_found` → Обработка дубликата
     - `anomaly_detected` → Обработка аномалии
     - `processing_error` → Обработка ошибки

3. **Google Sheets** (для document_processed)
   - Действие: Update a Row
   - Обновляет статус обработки
   - Добавляет метаданные

4. **Slack/Email** (для anomaly_detected)
   - Действие: Send Message
   - Уведомляет команду об аномалиях

5. **Error Handler** (для processing_error)
   - Действие: Create Issue (Jira/GitHub)
   - Автоматически создает задачу на исправление

## Формат событий

### document_processed

```json
{
  "event_type": "document_processed",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "document_id": "DOC_20240101_120000_abc123",
    "file_name": "invoice_2024.pdf",
    "page_count": 5,
    "file_size": 1048576,
    "ocr_status": "completed",
    "supplier": "ACME Corp",
    "document_type": "invoice",
    "duplicate": false,
    "drive_link": "https://drive.google.com/file/d/...",
    "gpt_analysis": {
      "document_type": "invoice",
      "supplier": "ACME Corp",
      "confidence": 0.95,
      "key_info": {
        "date": "2024-01-01",
        "amount": "1000.00",
        "currency": "USD"
      }
    }
  }
}
```

### duplicate_found

```json
{
  "event_type": "duplicate_found",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "document_id": "DOC_20240101_120000_xyz789",
    "file_name": "duplicate_invoice.pdf",
    "duplicate": true,
    "duplicate_matches": [
      {
        "document_id": "DOC_20231215_100000_abc123",
        "similarity": 0.98,
        "file_name": "original_invoice.pdf",
        "timestamp": "2023-12-15T10:00:00.000Z"
      }
    ]
  }
}
```

### anomaly_detected

```json
{
  "event_type": "anomaly_detected",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "document_id": "DOC_20240101_120000_def456",
    "anomalies": [
      "Unusual document format detected",
      "Missing expected date field",
      "Supplier information inconsistent with historical data"
    ]
  }
}
```

### processing_error

```json
{
  "event_type": "processing_error",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "data": {
    "document_id": "DOC_20240101_120000_err999",
    "file_name": "problematic_file.pdf",
    "error_type": "OCRError",
    "error_message": "Failed to process PDF: file corrupted",
    "processing_stage": "ocr"
  }
}
```

## Пример сценария: Автоматическая сортировка

### Цель
Автоматически сортировать обработанные документы по поставщикам в разные папки Google Drive.

### Модули

1. **Webhook** ← получает событие `document_processed`
2. **Router** → проверяет `data.supplier`
3. **Google Drive: Create Folder** (если папка не существует)
4. **Google Drive: Move File** → перемещает в папку поставщика
5. **Google Sheets: Update Row** → обновляет местоположение

## Пример сценария: Уведомления

### Цель
Отправлять уведомления команде о важных событиях.

### Модули

1. **Webhook** ← получает все события
2. **Router**:
   - `anomaly_detected` → Slack (канал #alerts)
   - `duplicate_found` → Email (менеджеру)
   - `processing_error` → Создать задачу в Jira
3. **Data Store** → сохранить статистику

## Пример сценария: Обработка счетов

### Цель
Автоматически обрабатывать счета (invoices) и создавать записи в ERP.

### Модули

1. **Webhook** ← событие `document_processed`
2. **Filter** → только `document_type == "invoice"`
3. **HTTP: Make Request** → отправить в ERP API
4. **Google Sheets: Add Row** → логировать в отчет
5. **Slack: Send Message** → уведомить бухгалтерию

## Настройка в Make.com

### Шаг 1: Создание сценария

1. Войдите в Make.com
2. Создайте новый сценарий
3. Добавьте модуль "Webhooks" → "Custom webhook"
4. Скопируйте URL webhook

### Шаг 2: Настройка OCR Factory

Добавьте URL в `.env`:
```env
MAKE_WEBHOOK_URL=https://hook.make.com/xxxxxxxxxxxxx
```

### Шаг 3: Добавление логики

1. Добавьте Router после Webhook
2. Создайте маршруты для каждого типа события
3. Добавьте действия для каждого маршрута
4. Настройте фильтры и условия

### Шаг 4: Тестирование

1. Запустите OCR Factory
2. Поместите тестовый PDF в `data/input/`
3. Проверьте выполнение в Make.com
4. Настройте по необходимости

## Продвинутые сценарии

### Машинное обучение на данных

1. Webhook → Google BigQuery (сохранение данных)
2. Scheduled Trigger → Python Script (обучение модели)
3. HTTP → Update OCR Factory с новыми правилами

### Интеграция с CRM

1. Webhook → Filter (только `document_type == "contract"`)
2. HTTP → CRM API (создание сделки)
3. Google Sheets → Обновление статуса
4. Email → Уведомление менеджера

### Мультиязычная обработка

1. Webhook → GPT (определение языка)
2. Router → по языкам
3. CloudConvert OCR → с нужным языком
4. Google Translate → перевод (если нужно)

## Мониторинг и аналитика

### Дашборд в Google Sheets

Создайте сценарий для агрегации данных:

1. **Scheduled Trigger** (каждый день)
2. **Google Sheets: Search Rows** (за период)
3. **Tools: Aggregator** (подсчет метрик)
4. **Google Sheets: Update Row** (обновление дашборда)

### Метрики для отслеживания

- Количество обработанных документов
- Процент дубликатов
- Типы документов (распределение)
- Поставщики (топ-10)
- Аномалии (частота)
- Ошибки (по типам)

## Примеры фильтров

### Только важные документы
```
{{data.gpt_analysis.confidence}} > 0.9
AND
{{data.duplicate}} = false
```

### Только счета больше 1000
```
{{data.document_type}} = "invoice"
AND
{{parseNumber(data.gpt_analysis.key_info.amount)}} > 1000
```

### Только новые поставщики
```
{{data.supplier_classification.reliability_score}} < 0.5
```

## Советы и рекомендации

1. **Используйте Data Store** для хранения состояний между запусками
2. **Настройте Error Handling** для всех критичных модулей
3. **Логируйте всё** в Google Sheets или БД для аудита
4. **Тестируйте на малых объемах** перед production
5. **Мониторьте использование операций** Make.com
6. **Делайте резервные копии** сценариев

## Ограничения Make.com

- **Free план**: 1,000 операций/месяц
- **Core план**: 10,000 операций/месяц
- **Pro план**: 10,000+ операций/месяц

Одна обработка документа = примерно 5-10 операций в Make.com

## Troubleshooting

### Webhook не получает данные
- Проверьте URL в `.env`
- Проверьте, что OCR Factory запущен
- Проверьте логи: `tail -f logs/ocr_factory.log`

### Данные приходят, но сценарий не срабатывает
- Проверьте фильтры в Router
- Проверьте формат данных в webhook
- Используйте "Run once" для отладки

### Превышен лимит операций
- Оптимизируйте сценарий (меньше модулей)
- Используйте batch processing
- Обновите план Make.com

## Дополнительные ресурсы

- [Make.com Documentation](https://www.make.com/en/help)
- [Webhook Best Practices](https://www.make.com/en/help/webhooks)
- [Google Sheets Integration](https://www.make.com/en/help/app/google-sheets)
