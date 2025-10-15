# Contributing to OCR Factory

Спасибо за интерес к проекту OCR Factory! 🎉

## Как внести вклад

### 1. Сообщить об ошибке (Bug Report)

Создайте issue с описанием:
- Шаги для воспроизведения
- Ожидаемое поведение
- Фактическое поведение
- Версия Python и ОС
- Логи (если есть)

### 2. Предложить улучшение (Feature Request)

Создайте issue с описанием:
- Проблема, которую решает функция
- Предлагаемое решение
- Альтернативные решения
- Примеры использования

### 3. Внести код (Pull Request)

#### Процесс

1. **Fork** репозитория
2. **Clone** вашего fork
   ```bash
   git clone https://github.com/your-username/Make_me_OCR.git
   ```
3. **Создайте ветку** для изменений
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Внесите изменения**
5. **Тестируйте** изменения
6. **Commit** с понятным сообщением
   ```bash
   git commit -m "Add feature: description"
   ```
7. **Push** в ваш fork
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Создайте Pull Request**

## Стандарты кода

### Python Code Style

Следуем **PEP 8** с некоторыми исключениями:
- Максимальная длина строки: 100 символов
- Используем 4 пробела для отступов
- Docstrings для всех функций и классов

### Пример docstring

```python
def process_document(file_path: Path, options: Dict) -> Dict:
    """
    Process a document through the OCR pipeline.
    
    Args:
        file_path: Path to the document file
        options: Processing options dictionary
    
    Returns:
        Dictionary with processing results
    
    Raises:
        FileNotFoundError: If file does not exist
        ProcessingError: If processing fails
    """
    pass
```

### Именование

- **Модули**: `lowercase_with_underscores.py`
- **Классы**: `CapitalizedWords`
- **Функции**: `lowercase_with_underscores()`
- **Константы**: `UPPERCASE_WITH_UNDERSCORES`
- **Переменные**: `lowercase_with_underscores`

### Type Hints

Используйте type hints где возможно:

```python
from typing import List, Dict, Optional
from pathlib import Path

def get_files(directory: Path, extensions: List[str]) -> List[Path]:
    """Get all files with specified extensions."""
    return [f for f in directory.iterdir() if f.suffix in extensions]
```

## Структура коммитов

### Формат сообщения

```
<type>: <subject>

<body>

<footer>
```

### Типы коммитов

- **feat**: Новая функция
- **fix**: Исправление ошибки
- **docs**: Изменения в документации
- **style**: Форматирование кода (без изменения логики)
- **refactor**: Рефакторинг кода
- **test**: Добавление тестов
- **chore**: Обновление зависимостей, конфигурации

### Примеры

```
feat: add support for DOCX files

Implement DOCX file processing using python-docx library.
Includes conversion to PDF before OCR.

Closes #42
```

```
fix: handle empty PDF files gracefully

Add check for empty PDFs before processing to prevent crashes.

Fixes #38
```

## Тестирование

### Запуск тестов

```bash
# Пока тестов нет, но планируются
python -m pytest tests/
```

### Написание тестов

Добавляйте тесты для новых функций в `tests/`:

```python
# tests/test_document_id.py
import pytest
from src.modules.document_id import DocumentIDGenerator

def test_generate_uuid():
    """Test UUID generation."""
    gen = DocumentIDGenerator()
    uuid1 = gen.generate_uuid()
    uuid2 = gen.generate_uuid()
    
    assert uuid1 != uuid2
    assert len(uuid1) == 36
```

## Области для вклада

### 🐛 Исправление ошибок (Beginner-friendly)

- Обработка edge cases
- Улучшение обработки ошибок
- Исправление опечаток в документации

### ✨ Новые функции (Intermediate)

- Поддержка новых форматов файлов (DOCX, RTF)
- Дополнительные OCR провайдеры (Tesseract, AWS Textract)
- Web UI для мониторинга
- REST API

### 🏗️ Архитектура (Advanced)

- Асинхронная обработка (asyncio)
- Пакетная обработка (batch processing)
- Микросервисная архитектура
- Кэширование результатов
- Оптимизация производительности

### 📚 Документация (All levels)

- Примеры использования
- Туториалы
- Перевод на другие языки
- Видео-демонстрации
- API reference

### 🧪 Тестирование (Intermediate)

- Unit tests
- Integration tests
- End-to-end tests
- Performance tests

## Приоритетные задачи

### High Priority
- [ ] Unit tests для всех модулей
- [ ] Web UI для мониторинга
- [ ] Поддержка Tesseract OCR
- [ ] Batch processing

### Medium Priority
- [ ] Асинхронная обработка
- [ ] REST API
- [ ] Docker optimization
- [ ] Performance profiling

### Low Priority
- [ ] Поддержка DOCX
- [ ] Локализация UI
- [ ] Advanced analytics
- [ ] ML-based classification

## Обзор кода (Code Review)

Все Pull Requests будут проверены на:

1. **Функциональность**: Работает ли код?
2. **Тесты**: Есть ли тесты? Проходят ли они?
3. **Документация**: Обновлена ли документация?
4. **Стиль**: Соответствует ли код стандартам?
5. **Производительность**: Нет ли узких мест?
6. **Безопасность**: Нет ли уязвимостей?

## Лицензия

Внося вклад, вы соглашаетесь, что ваш код будет лицензирован под MIT License.

## Вопросы?

- Создайте issue с меткой `question`
- Свяжитесь с maintainer

## Благодарности

Спасибо всем контрибьюторам! 🙏

## Полезные ресурсы

- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Git Best Practices](https://git-scm.com/book/en/v2)
- [Writing Good Commit Messages](https://chris.beams.io/posts/git-commit/)
