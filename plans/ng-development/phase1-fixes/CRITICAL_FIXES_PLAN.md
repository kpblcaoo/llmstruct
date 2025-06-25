# Phase 1 Critical Fixes Plan

## Выявленные проблемы

### 🔥 High Priority

1. **Некачественные auto-summary**
   - Проблема: Одинаковые заглушки "Optimizes image loading and caching for improved website performance"
   - Причина: LLM prompt "прилип" к первому примеру
   - Решение: Исправить fallback chain: docstring → heuristic → LLM (если confidence < 0.5)

2. **uid_components дублирует элементы**
   - Проблема: `["dir:", "dir:."]` и отсутствие строгого формата
   - Решение: Зафиксировать схемой - массив без дубликатов, каждый шаг = отдельный уровень FQN

3. **Hash отсутствует (null)**
   - Проблема: Нет SHA-256 хэшей для incremental build
   - Решение: Создать `core/hash_utils.py` с функцией `hash_source(content)`

4. **Саммари должен быть опциональным**
   - Проблема: API не бесплатно, включен по умолчанию
   - Решение: Добавить флаг `--enable-summaries`, по умолчанию выключен

### ⭐ Medium Priority

5. **Метрики-заглушки**
   - Проблема: `lines_of_code: 20` одинаково для разных модулей
   - Решение: Вычислять real LOC

6. **Test coverage = 0 everywhere**
   - Проблема: Не находит .coverage файлы
   - Решение: Создать `core/coverage_mapper.py`

7. **Отсутствует index.json**
   - Проблема: Нет быстрого реестра
   - Решение: Автогенерировать `{path, summary, tags, hash, tested}`

### 🛈 Low Priority

8. **TOC дублирует поля**
   - Решение: Минимальный TOC (id, path, summary)

## План исправлений

### Шаг 1: Исправление Summary System
- [ ] Добавить флаг `--enable-summaries` (по умолчанию False)
- [ ] Исправить fallback chain: docstring → heuristic → LLM
- [ ] Добавить confidence threshold < 0.5 для пустых summary
- [ ] Исправить LLM prompt для избежания "прилипания"

### Шаг 2: Исправление UID System
- [ ] Убрать дубликаты в uid_components
- [ ] Зафиксировать схему uid_components
- [ ] Обновить JSON Schema

### Шаг 3: Добавление Hash Utils
- [ ] Создать `core/hash_utils.py`
- [ ] Интегрировать в генераторы
- [ ] Добавить в JSON Schema

### Шаг 4: Исправление метрик
- [ ] Реальный подсчет LOC
- [ ] Исправить maintainability_index
- [ ] Добавить coverage mapping

### Шаг 5: Index.json
- [ ] Создать `export_index.py`
- [ ] Генерировать индекс из modules[]

## Статус выполнения

- [x] Шаг 1: Summary System ✅ COMPLETED
  - [x] Добавлен флаг `--enable-llm` (по умолчанию False)
  - [x] Исправлен fallback chain: docstring → heuristic → LLM
  - [x] Добавлен confidence threshold < 0.5 для пустых summary
  - [x] Создана система провайдеров с HeuristicProvider по умолчанию
- [x] Шаг 2: UID System ✅ COMPLETED
  - [x] Убраны дубликаты в uid_components
  - [x] Зафиксирована схема uid_components без дубликатов
  - [x] Обновлена логика генерации компонентов
- [x] Шаг 3: Hash Utils ✅ COMPLETED
  - [x] Создан `core/hash_utils.py` с полным набором функций
  - [x] Поддержка хэширования файлов, контента, сущностей
  - [x] Нормализация исходного кода для консистентного хэширования
- [x] Шаг 4: Configuration System ✅ COMPLETED  
  - [x] Создана система управления конфигурацией
  - [x] LLM отключен по умолчанию для безопасности
  - [x] Поддержка переменных окружения и CLI флагов
  - [x] Создан пример конфигурации llmstruct.example.yaml
- [ ] Шаг 5: Index.json
- [ ] Шаг 6: Coverage mapping  
- [ ] Шаг 7: Real LOC metrics

## Тестирование

После каждого шага:
- [ ] Запуск `test_phase1_integration.py`
- [ ] Проверка качества генерируемого JSON
- [ ] Валидация schema

## Цель

Довести Phase 1 до 95% соответствия roadmap перед переходом к Phase 2. 