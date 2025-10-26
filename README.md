# Make_me_OCR - OCR Factory

Автоматизированная система обработки документов с использованием OCR, GPT-анализа и интеграции с Google Services и Make.com.

## 🚀 Возможности

- **Мониторинг папок**: Автоматическое отслеживание новых документов в указанной папке
- **Обработка PDF**: 
  - Копирование оригиналов
  - Удаление белых/пустых страниц
  - Разделение PDF на отдельные страницы
- **OCR**: Распознавание текста с помощью CloudConvert API
- **GPT-анализ документов**:
  - Классификация типов документов
  - Определение поставщиков
  - Извлечение ключевой информации
  - Обнаружение аномалий
  - Обучение на ошибках
- **Управление дубликатами**: Определение дубликатов на основе перцептивного хеширования
- **Генерация ID**: Уникальные идентификаторы для каждого документа
- **Индексирование**: Хранение метаданных в Google Sheets
- **Интеграция с Google Drive**: Загрузка документов в облако
- **Make.com webhook**: Отправка событий в Make.com для автоматизации workflow
- **Полное логирование**: Цветные логи в консоли и файлы

## 📋 Требования

- Python 3.8+
- Google Service Account с доступом к Sheets и Drive API
- CloudConvert API ключ
- OpenAI API ключ (для GPT-4)
- Make.com webhook URL (опционально)

## 🛠️ Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/troublestarter-dot/Make_me_OCR.git
cd Make_me_OCR
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

4. Настройте переменные окружения в `.env`:
```env
# Google Service Account
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account.json
GOOGLE_SHEETS_ID=your-spreadsheet-id
GOOGLE_DRIVE_FOLDER_ID=your-drive-folder-id

# CloudConvert API
CLOUDCONVERT_API_KEY=your-cloudconvert-api-key

# OpenAI GPT
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4

# Make.com webhook (optional)
MAKE_WEBHOOK_URL=https://hook.make.com/your-webhook-url
```

## 🔑 Настройка Google Service Account

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google Sheets API и Google Drive API
4. Создайте Service Account:
   - IAM & Admin → Service Accounts → Create Service Account
   - Скачайте JSON-ключ
5. Предоставьте доступ Service Account к вашей Google таблице и папке Drive

## 📊 Структура проекта

```
Make_me_OCR/
├── src/
│   ├── config/
│   │   └── config.py          # Конфигурация приложения
│   ├── modules/
│   │   ├── logger.py          # Система логирования
│   │   ├── folder_monitor.py  # Мониторинг папок
│   │   ├── pdf_processor.py   # Обработка PDF
│   │   ├── document_id.py     # Генерация ID
│   │   ├── duplicate_checker.py # Проверка дубликатов
│   │   ├── google_services.py  # Google Sheets/Drive
│   │   ├── ocr_service.py     # CloudConvert OCR
│   │   ├── gpt_analyzer.py    # GPT-анализ
│   │   └── make_integration.py # Make.com webhook
│   └── main.py                # Главный оркестратор
├── data/
│   ├── input/                 # Входящие документы
│   ├── processed/             # Обработанные документы
│   ├── originals/             # Копии оригиналов
│   └── index/                 # Локальный индекс
├── logs/                      # Файлы логов
├── requirements.txt           # Зависимости Python
├── .env.example              # Пример конфигурации
└── README.md                 # Документация

```

## 🎯 Использование

### Запуск системы

```bash
python src/main.py
```

Система начнет мониторить папку `data/input/` и автоматически обрабатывать новые документы.

### Обработка существующих файлов

При запуске система автоматически обработает все существующие файлы в папке `input`, а затем начнет отслеживать новые.

### Поддерживаемые форматы

- PDF (`.pdf`)
- Изображения (`.jpg`, `.jpeg`, `.png`, `.tiff`)

## 🔄 Процесс обработки документа

1. **Обнаружение**: Файл появляется в папке `input`
2. **Генерация ID**: Создается уникальный идентификатор
3. **Копирование**: Оригинал сохраняется в `originals`
4. **Проверка дубликатов**: Поиск похожих документов
5. **Очистка**: Удаление пустых страниц
6. **Разделение**: PDF разбивается на отдельные страницы (опционально)
7. **OCR**: Распознавание текста
8. **GPT-анализ**: 
   - Определение типа документа
   - Классификация поставщика
   - Извлечение данных
   - Обнаружение аномалий
9. **Загрузка**: Файл загружается в Google Drive
10. **Индексирование**: Данные записываются в Google Sheets
11. **Уведомление**: Отправка webhook в Make.com

## 📈 Google Sheets структура

### Document Index
| Document ID | File Name | Timestamp | Page Count | File Size | OCR Status | Supplier | Document Type | Duplicate | Drive Link | Notes |
|-------------|-----------|-----------|------------|-----------|------------|----------|---------------|-----------|------------|-------|

### Error Log
| Timestamp | Document ID | Error Type | Error Message | Processing Stage | Resolution |
|-----------|-------------|------------|---------------|------------------|------------|

## 🔔 Make.com События

Система отправляет следующие события в Make.com webhook:

- `document_processed`: Документ успешно обработан
- `processing_error`: Ошибка при обработке
- `duplicate_found`: Обнаружен дубликат
- `anomaly_detected`: Обнаружены аномалии

## 🧠 GPT-функции

### Анализ документов
- Автоматическое определение типа документа
- Извлечение ключевой информации (даты, суммы, названия)
- Оценка уверенности в результатах

### Классификация поставщиков
- Определение отрасли
- Оценка надежности
- Выявление типичных документов от поставщика

### Прогнозирование типов
- Предсказание типа документа до полной обработки
- Определение приоритета обработки

### Обнаружение аномалий
- Выявление необычных паттернов
- Обнаружение несоответствий
- Предупреждение о подозрительном контенте

### Обучение на ошибках
- Сбор истории ошибок
- Анализ паттернов ошибок
- Рекомендации по предотвращению

## 🐛 Отладка

Логи сохраняются в:
- Консоль (с цветами)
- Файл `logs/ocr_factory.log`

Уровень логирования можно настроить в `.env`:
```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 📝 Лицензия

MIT License

## 👥 Авторы

troublestarter-dot

## 🤝 Вклад

Приветствуются pull requests. Для крупных изменений сначала откройте issue для обсуждения.

## 📧 Поддержка

Если у вас возникли вопросы или проблемы, создайте issue в репозитории.