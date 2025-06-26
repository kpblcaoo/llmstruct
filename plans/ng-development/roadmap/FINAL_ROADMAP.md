# LLMStruct Next Generation - Final Roadmap

**Версия:** v2.0 (Next Generation)  
**Дата создания:** 25.06.2024  
**Статус:** 🟡 Планирование завершено, ожидает согласования

---

## 🎯 Стратегическая цель

Превратить LLMStruct из простого парсера кода в **мощную платформу для анализа архитектуры**, оптимизированную для LLM, с интерактивным просмотром и мультиязычной поддержкой.

---

## 📊 Анализ приоритетов

### 🔥 Критический уровень - Основа (v2.0 Core)
**Цель:** LLM-оптимизированная структура данных

1. **UID/FQNAME система** - стабильные ссылки
2. **Иерархическая структура JSON** - улучшенная навигация  
3. **Markdown-friendly anchors** - интеграция с AI инструментами
4. **Обратная совместимость** - не ломать существующие интеграции

### ⭐ Высокий уровень - Расширение (v2.1)
**Цель:** Богатый контекст и метрики

1. **Summary/Tags система** - автогенерация описаний
2. **Встроенные метрики** - complexity, test coverage, call depth
3. **DIFF-анализ** - сравнение между версиями
4. **Связка с тестами** - архитектурное покрытие

### 🚀 Средний уровень - Инновации (v2.2)
**Цель:** Интерактивность и многоязычность  

1. **LLMStruct Viewer** - автономный интерактивный просмотр
2. **Мультиязычная поддержка** - Python + Go + расширения
3. **TypeScript frontend** - современный UI
4. **Security теги** - threat modeling hooks

---

## 🗓️ Детальный план реализации

### Phase 1: 🏗️ Foundation (v2.0 Core) - 4-6 недель

#### Epic 1.1: UID/FQNAME System (1-2 недели)
- [ ] **Дизайн UID схемы** для разных языков
  - Python: `module.class.method`
  - Go: `package.Type.Method`  
  - Унифицированный формат для всех языков
- [ ] **Рефакторинг парсеров** - добавление UID генерации
- [ ] **Обновление struct.json** - интеграция UID
- [ ] **Backward compatibility** - сохранение старых полей

#### Epic 1.2: Hierarchical JSON Structure (1-2 недели)  
- [ ] **Новая схема struct.json**
  ```json
  {
    "modules": {
      "module.name": {
        "metadata": { "summary", "tags", "hash", "lines" },
        "classes": { "ClassName": { "methods": {...} } },
        "functions": {...},
        "calls": {...}
      }
    }
  }
  ```
- [ ] **Обновление .llmstruct_index/**
  - Синхронизация структуры с основным JSON
  - Добавление metadata блоков
- [ ] **Создание index.json** - манифест модулей

#### Epic 1.3: Markdown-friendly Output (1 неделя)
- [ ] **Anchor генератор** - для каждого объекта
- [ ] **CLI команда export-markdown** 
- [ ] **Шаблоны карточек** для функций/классов
- [ ] **Интеграция с существующими export'ами**

#### Epic 1.4: Schema & Validation (1 неделя)
- [ ] **JSON Schema v2.0** - формальное описание структуры
- [ ] **Валидатор** - проверка корректности генерируемых данных
- [ ] **Миграционные скрипты** - v1 → v2
- [ ] **Документация формата**

### Phase 2: 📈 Enhancement (v2.1) - 3-4 недели

#### Epic 2.1: Summary & Tags System (1-2 недели)
- [ ] **Базовые теги** - cli, core, export, security, etc.
- [ ] **Автогенерация summary** - с помощью LLM (опционально)
- [ ] **Кэширование** - сохранение generated content
- [ ] **Tag-based фильтрация** - в CLI и API

#### Epic 2.2: Metrics Integration (1-2 недели)
- [ ] **Cyclomatic complexity** 
  - Python: интеграция с `radon`
  - Go: интеграция с `gocyclo`
- [ ] **Test coverage mapping** - связь с coverage.py/go cover
- [ ] **Call depth analysis** - глубина вызовов
- [ ] **Dead code detection** - неиспользуемые функции

#### Epic 2.3: DIFF Analysis (1 неделя)
- [ ] **Структурный diff** - сравнение struct.json между версиями
- [ ] **Семантический анализ** - не только хэши, но и смысловые изменения
- [ ] **CLI команда diff** - удобный интерфейс
- [ ] **CI/CD интеграция** - автоматические отчеты

### Phase 3: 🌟 Innovation (v2.2) - 6-8 недель

#### Epic 3.1: LLMStruct Viewer (3-4 недели)
- [ ] **Архитектура viewer'а**
  ```
  viewer/
  ├── index.html          # Entry point
  ├── src/
  │   ├── app.ts         # Main application  
  │   ├── components/    # UI components
  │   └── utils/         # Utilities
  ├── public/            # Static assets
  └── data/              # Generated JSON files
  ```
- [ ] **TypeScript setup** - современный frontend стек
- [ ] **Core компоненты**:
  - Module tree navigator
  - Function inspector  
  - Callgraph visualizer
  - Search & filter interface
  - Metrics dashboard
- [ ] **Data integration** - загрузка и обработка JSON
- [ ] **Export generator** - Python скрипт создания viewer
- [ ] **Responsive design** - работа на разных устройствах

#### Epic 3.2: Multi-language Support (2-3 недели)  
- [ ] **Go parser enhancement** - полная поддержка на уровне Python
- [ ] **Language registry** - плагинная архитектура
- [ ] **UID normalization** - унификация между языками
- [ ] **Mixed projects support** - Python + Go в одном проекте
- [ ] **Future expansion planning** - подготовка для Rust/JS/etc

#### Epic 3.3: Advanced Features (1 неделя)
- [ ] **Security tags** - @security-sensitive, @public-api
- [ ] **External dependencies** - отслеживание внешних зависимостей  
- [ ] **Usage examples** - связь с тестами и примерами
- [ ] **Performance optimizations** - кэширование, инкрементальный анализ

---

## 🧱 Техническая архитектура v2.0

### Структура проекта
```
llmstruct/
├── core/                      # Ядро системы
│   ├── schema.py             # Модели данных v2.0
│   ├── generator.py          # Генерация struct.json
│   ├── merger.py             # Объединение из разных языков
│   ├── differ.py             # Анализ различий
│   └── exporter.py           # Export в разные форматы
├── parsers/                   # Языковые парсеры
│   ├── base.py               # Базовый интерфейс парсера
│   ├── python/               # Python AST анализ
│   ├── go/                   # Go AST анализ  
│   └── registry.py           # Регистрация парсеров
├── viewer/                    # Interactive viewer
│   ├── template/             # Шаблон viewer'а
│   ├── generator.py          # Генератор viewer'а
│   └── assets/               # Статические ресурсы
├── cli/                       # Command line interface
└── api/                       # REST API (из feature/API)
```

### Ключевые принципы
1. **Модульность** - четкое разделение компонентов
2. **Расширяемость** - простое добавление новых языков
3. **Обратная совместимость** - поддержка v1.x форматов
4. **Производительность** - инкрементальный анализ и кэширование
5. **LLM-first** - оптимизация под восприятие AI моделей

---

## 📏 Критерии успеха

### Phase 1 Success Metrics
- [ ] 100% обратная совместимость с v1.x
- [ ] UID генерируется для всех объектов
- [ ] Новый формат JSON читается LLM на 40%+ эффективнее
- [ ] Markdown export работает для существующих проектов

### Phase 2 Success Metrics  
- [ ] Summary генерируется автоматически (90%+ покрытие)
- [ ] Метрики интегрированы в основной workflow
- [ ] DIFF показывает осмысленные изменения архитектуры
- [ ] Test coverage mapping работает точно

### Phase 3 Success Metrics
- [ ] Viewer открывается и работает без backend'а
- [ ] Python + Go проекты анализируются корректно
- [ ] Интерактивная навигация по проекту интуитивна
- [ ] Экспорт viewer'а занимает <30 секунд

---

## ⚠️ Риски и митигация

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Производительность парсинга | Средняя | Высокое | Инкрементальный анализ, кэширование |
| Размер JSON вывода | Высокая | Среднее | Опциональные поля, сжатие |
| Сложность viewer'а | Средняя | Среднее | MVP подход, итеративная разработка |
| Совместимость парсеров | Низкая | Высокое | Тщательное тестирование, автотесты |

---

## 🔄 Plan Review & Updates

### Следующие шаги для согласования:
1. **Приоритизация** - подтверждение порядка фаз
2. **Ресурсы** - оценка времени и сложности  
3. **MVP scope** - что включать в первую версию viewer'а
4. **Technical decisions** - выбор конкретных технологий

### Частота ревью: еженедельно
### Владелец плана: kpblc
### Статус: 🟡 Ожидает утверждения

---

**Готово к обсуждению и уточнению приоритетов** 🚀 