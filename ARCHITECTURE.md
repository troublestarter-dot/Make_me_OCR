# OCR Factory - Архитектура системы

## Обзор

OCR Factory - это модульная система автоматической обработки документов с интеграцией AI и облачных сервисов.

## Архитектурная схема

```
┌─────────────────────────────────────────────────────────────────┐
│                        OCR FACTORY                               │
│                                                                  │
│  ┌──────────────┐         ┌─────────────────────────┐          │
│  │   INPUT      │         │   FOLDER MONITOR        │          │
│  │   FOLDER     │────────▶│   (Watchdog)            │          │
│  │ (data/input) │         └─────────────────────────┘          │
│  └──────────────┘                     │                         │
│                                       ▼                         │
│                          ┌────────────────────────┐             │
│                          │   MAIN ORCHESTRATOR    │             │
│                          │      (main.py)         │             │
│                          └────────────────────────┘             │
│                                    │                            │
│              ┌─────────────────────┼─────────────────────┐      │
│              ▼                     ▼                     ▼      │
│    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│    │  PDF PROCESSOR   │  │ DOCUMENT ID GEN  │  │   DUPLICATE  ││
│    │ • Copy originals │  │ • Hash-based     │  │   CHECKER    ││
│    │ • Remove blanks  │  │ • Timestamp      │  │ • pHash      ││
│    │ • Split PDFs     │  │ • Composite      │  │ • Index      ││
│    └──────────────────┘  └──────────────────┘  └──────────────┘│
│              │                                         │         │
│              ▼                                         ▼         │
│    ┌──────────────────┐                    ┌──────────────────┐ │
│    │   OCR SERVICE    │                    │  LOCAL INDEX     │ │
│    │  (CloudConvert)  │                    │ (document_index. │ │
│    │ • PDF → Text     │                    │     json)        │ │
│    └──────────────────┘                    └──────────────────┘ │
│              │                                                   │
│              ▼                                                   │
│    ┌──────────────────┐                                         │
│    │  GPT ANALYZER    │                                         │
│    │ • Document type  │                                         │
│    │ • Supplier class │                                         │
│    │ • Anomaly detect │                                         │
│    │ • Error learning │                                         │
│    └──────────────────┘                                         │
│              │                                                   │
│       ┌──────┴──────┐                                           │
│       ▼             ▼                                           │
│ ┌──────────┐  ┌──────────┐                                     │
│ │  GOOGLE  │  │  MAKE.   │                                     │
│ │ SERVICES │  │   COM    │                                     │
│ │ • Sheets │  │ • Events │                                     │
│ │ • Drive  │  │ • Webhook│                                     │
│ └──────────┘  └──────────┘                                     │
│       │             │                                           │
└───────┼─────────────┼───────────────────────────────────────────┘
        ▼             ▼
   ┌─────────┐  ┌──────────┐
   │ Google  │  │  Make.com│
   │  Cloud  │  │ Scenarios│
   └─────────┘  └──────────┘
```

## Компоненты системы

### 1. Folder Monitor (folder_monitor.py)
**Назначение**: Мониторинг папки для новых документов

**Функции**:
- Отслеживание файловых событий (watchdog)
- Фильтрация по расширениям файлов
- Обработка существующих файлов при старте
- Предотвращение дублирования обработки

**Технологии**: `watchdog`

### 2. PDF Processor (pdf_processor.py)
**Назначение**: Обработка PDF документов

**Функции**:
- Копирование оригиналов
- Определение пустых страниц (по содержимому пикселей)
- Удаление пустых страниц
- Разделение PDF на страницы
- Извлечение метаданных

**Технологии**: `PyPDF2`, `pdf2image`, `Pillow`, `numpy`

### 3. Document ID Generator (document_id.py)
**Назначение**: Генерация уникальных идентификаторов

**Методы**:
- Hash-based (SHA256)
- UUID
- Timestamp
- Composite (timestamp + hash)

**Формат**: `DOC_YYYYMMDD_HHMMSS_hash12`

### 4. Duplicate Checker (duplicate_checker.py)
**Назначение**: Определение дубликатов документов

**Алгоритм**:
1. Вычисление perceptual hash (pHash) документа
2. Сравнение с индексом
3. Расчет similarity score
4. Порог: 95% (настраивается)

**Технологии**: `imagehash`

### 5. Google Services (google_services.py)
**Назначение**: Интеграция с Google Cloud

**Функции**:
- Аутентификация через Service Account
- Запись в Google Sheets
- Загрузка в Google Drive
- Управление индексом документов
- Логирование ошибок

**API**:
- Google Sheets API v4
- Google Drive API v3

### 6. OCR Service (ocr_service.py)
**Назначение**: Распознавание текста в документах

**Функции**:
- OCR для PDF
- OCR для изображений
- Мониторинг использования API

**Провайдер**: CloudConvert API

**Поддерживаемые языки**: eng, rus, и другие (настраивается)

### 7. GPT Analyzer (gpt_analyzer.py)
**Назначение**: AI-анализ документов

**Функции**:
- Анализ документов (тип, поставщик, ключевые данные)
- Классификация поставщиков (отрасль, надежность)
- Прогнозирование типов документов
- Обнаружение аномалий
- Обучение на ошибках
- Генерация insights

**Модель**: GPT-4 (настраивается)

### 8. Make Integration (make_integration.py)
**Назначение**: Интеграция с Make.com

**События**:
- `document_processed` - документ обработан
- `duplicate_found` - найден дубликат
- `anomaly_detected` - обнаружены аномалии
- `processing_error` - ошибка обработки

### 9. Logger (logger.py)
**Назначение**: Централизованное логирование

**Функции**:
- Цветной вывод в консоль
- Запись в файлы
- Уровни: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Технология**: `colorlog`

### 10. Config (config.py)
**Назначение**: Управление конфигурацией

**Источники**:
- Переменные окружения (.env)
- Значения по умолчанию
- Валидация при старте

## Поток данных

### Обработка одного документа

```
1. NEW FILE DETECTED
   ↓
2. GENERATE DOCUMENT ID
   ↓
3. COPY ORIGINAL
   ↓
4. CHECK DUPLICATES ─────→ [DUPLICATE?] ─→ NOTIFY
   ↓                              ↓ No
5. GET PDF INFO                   ↓
   ↓                              ↓
6. REMOVE BLANK PAGES             ↓
   ↓                              ↓
7. SPLIT PDF (optional)           ↓
   ↓                              ↓
8. PERFORM OCR                    ↓
   ↓                              ↓
9. GPT ANALYSIS ──────────────────┘
   • Document type
   • Supplier classification
   • Anomaly detection
   ↓
10. UPLOAD TO DRIVE
    ↓
11. ADD TO INDEX (local + Sheets)
    ↓
12. NOTIFY MAKE.COM
    ↓
13. DONE ✓
```

## Хранилище данных

### Локальное хранилище

```
data/
├── input/           # Входящие документы (temporary)
├── processed/       # Обработанные документы
│   ├── cleaned_*.pdf
│   ├── ocr_*.pdf
│   └── split_*/
├── originals/       # Копии оригиналов
└── index/
    └── document_index.json  # Локальный индекс
```

### Google Sheets

**Document Index** - главная таблица документов
**Error Log** - журнал ошибок

### Google Drive

Все документы загружаются в указанную папку для долговременного хранения.

## API интеграции

### CloudConvert API

```
POST /v2/jobs
{
  "tasks": {
    "import": { "operation": "import/upload" },
    "ocr": { "operation": "ocr", "language": "eng" },
    "export": { "operation": "export/url" }
  }
}
```

### OpenAI API

```
POST /v1/chat/completions
{
  "model": "gpt-4",
  "messages": [...],
  "response_format": { "type": "json_object" }
}
```

### Google Sheets API

```
POST /v4/spreadsheets/{sheetId}/values/{range}:append
{
  "values": [[...]]
}
```

### Google Drive API

```
POST /v3/files
{
  "name": "filename.pdf",
  "parents": ["folderId"]
}
```

## Паттерны проектирования

### 1. Factory Pattern
Создание компонентов системы через фабрику в main.py

### 2. Observer Pattern
Мониторинг папки и обработка событий

### 3. Strategy Pattern
Различные методы генерации ID документов

### 4. Chain of Responsibility
Последовательная обработка документа через модули

### 5. Singleton Pattern
Единственный экземпляр конфигурации

## Обработка ошибок

### Стратегия

```
TRY
  Process Document
CATCH Error
  ↓
  1. Log to file
  2. Log to Google Sheets
  3. Notify Make.com
  4. Learn from error (GPT)
  5. Continue with next document
```

### Типы ошибок

- **Configuration Error**: Неверная конфигурация (fatal)
- **File Error**: Проблемы с файлом (skip document)
- **API Error**: Ошибка внешнего API (retry/skip)
- **Processing Error**: Ошибка обработки (log + skip)

## Масштабируемость

### Текущая архитектура
- **Тип**: Single-node
- **Обработка**: Sequential (последовательная)
- **Подходит для**: < 100 документов/день

### Возможные улучшения

1. **Параллельная обработка**
   - Использование multiprocessing
   - Очередь задач (Celery + Redis)

2. **Распределенная обработка**
   - Kubernetes для оркестрации
   - RabbitMQ для очередей
   - Shared storage (S3/GCS)

3. **Микросервисы**
   - Отдельные сервисы для каждого модуля
   - REST API для взаимодействия
   - Container orchestration

## Безопасность

### Хранение секретов
- Environment variables (.env)
- Service Account JSON (не в git)
- API keys (не в коде)

### Доступы
- Google Service Account с минимальными правами
- Read-only для исходных документов
- Encryption at rest (Google Drive)

### Логирование
- Не логируем sensitive data
- Маскирование API keys в логах
- Ротация логов

## Мониторинг и метрики

### Key Performance Indicators (KPI)

- **Throughput**: документов/час
- **Success Rate**: % успешно обработанных
- **Duplicate Rate**: % дубликатов
- **Error Rate**: % ошибок
- **Processing Time**: среднее время обработки

### Логи

```
logs/ocr_factory.log
- INFO: нормальная работа
- WARNING: не критичные проблемы
- ERROR: ошибки обработки
- CRITICAL: фатальные ошибки
```

## Зависимости

### Внешние сервисы

- **Google Cloud** (Sheets, Drive)
- **CloudConvert** (OCR)
- **OpenAI** (GPT)
- **Make.com** (Automation) - опционально

### Python пакеты

См. `requirements.txt`

## Конфигурация

### Обязательные параметры
- `GOOGLE_SERVICE_ACCOUNT_FILE`
- `CLOUDCONVERT_API_KEY`
- `OPENAI_API_KEY`

### Опциональные параметры
- `MAKE_WEBHOOK_URL`
- `GOOGLE_SHEETS_ID`
- `GOOGLE_DRIVE_FOLDER_ID`

### Настройки обработки
- `MIN_PAGE_CONTENT_THRESHOLD`
- `DUPLICATE_SIMILARITY_THRESHOLD`
- `MAX_FILE_SIZE_MB`

## Развертывание

### Опции

1. **Локальное**
   ```bash
   python src/main.py
   ```

2. **Docker**
   ```bash
   docker-compose up -d
   ```

3. **Cloud (Google Cloud Run)**
   ```bash
   gcloud run deploy ocr-factory
   ```

4. **Kubernetes**
   ```bash
   kubectl apply -f k8s/
   ```

## Roadmap

### v1.0 (Текущая версия)
- ✅ Базовая обработка PDF
- ✅ OCR с CloudConvert
- ✅ GPT-анализ
- ✅ Google Services интеграция
- ✅ Make.com webhook

### v1.1 (Планируется)
- [ ] Поддержка больше форматов (DOC, DOCX)
- [ ] Batch processing (пакетная обработка)
- [ ] Web UI для мониторинга
- [ ] REST API
- [ ] Поддержка нескольких языков OCR

### v2.0 (Будущее)
- [ ] Микросервисная архитектура
- [ ] ML модели для классификации
- [ ] Real-time dashboard
- [ ] Multi-tenant support
- [ ] Advanced analytics
