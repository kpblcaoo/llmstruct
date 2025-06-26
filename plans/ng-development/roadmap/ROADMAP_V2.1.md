# LLMStruct Next Generation - Roadmap v2.1 (Updated)

**Версия:** v2.1 (с интеграцией user feedback)  
**Дата обновления:** 25.06.2024  
**Базовая версия:** FINAL_ROADMAP.md  
**Статус:** 🟢 Готов к реализации

---

## 🎯 Стратегическая цель (обновлена)

Создать промышленный фреймворк уровня LSP/pyright для анализа архитектуры кода, оптимизированный для LLM, с интерактивным просмотром, мультиязычной поддержкой и встроенными DevTools. Все новые компоненты должны работать с модульной структурой struct/ (директория, не flat JSON) и поддерживать работу с несколькими проектами (multi-tenant, struct_path/project_id).

---

## 🔄 Интеграция пользовательского feedback

### ✅ Принятые улучшения:
- **UID Components** - для удобства UI и поиска
- **Smart Summary fallback** - docstring → LLM → cache
- **tested_by arrays** - список тестов для каждой функции
- **Markdown Static Site** - первый этап viewer
- **5 новых модулей** - Linter, DevAssistant, Heatmap, Showcase, Incremental

---

## 🗓️ Обновленный план реализации

### Phase 1: 🏗️ Foundation (v2.0 Core) - 4-6 недель

#### Epic 1.1: Advanced UID System (1-2 недели) ⭐ ОБНОВЛЕНО
- [ ] **UID + Components генерация**
  ```json
  {
    "uid": "sboxmgr.exporter.SingboxExporter.export",
    "uid_components": ["sboxmgr", "exporter", "SingboxExporter", "export"]
  }
  ```
- [ ] **Поиск по компонентам** - быстрые выборки в UI
- [ ] **Рефакторинг парсеров** - добавление UID+components генерации
- [ ] **Backward compatibility** - сохранение старых полей

#### Epic 1.2: Enhanced JSON Structure (1-2 недели) ⭐ ОБНОВЛЕНО
- [ ] **Обновленная схема struct.json**
  ```json
  {
    "modules": {
      "module.name": {
        "metadata": { 
          "summary": "...",
          "summary_source": "docstring|llm|generated",
          "tags": [...],
          "hash": "...",
          "lines": [...] 
        },
        "classes": {
          "ClassName": {
            "uid": "...",
            "uid_components": [...],
            "tested_by": ["tests/test_file.py::test_method"],
            "methods": {...}
          }
        }
      }
    }
  }
  ```
- [ ] **tested_by integration** - отслеживание связей с тестами
- [ ] **File hash tracking** - для incremental rebuild

#### Epic 1.3: Smart Summary System (1 неделя) 🆕
- [ ] **Fallback стратегия:**
  1. Extract from docstring → truncate
  2. If empty → generate with LLM  
  3. Cache in `summary_generated`
- [ ] **Summary quality scoring** - оценка качества описаний
- [ ] **Batch LLM processing** - эффективная генерация

#### Epic 1.4: Schema & Validation (1 неделя)
- [ ] **JSON Schema v2.1** - с учетом uid_components и tested_by
- [ ] **Spec documentation** - формальное описание стандарта
- [ ] **Migration tools** - v1 → v2.1
- [ ] **Validation API** - программная проверка

### Phase 2: 📈 Enhancement Plus (v2.1) - 4-5 недель

#### Epic 2.1: Coverage Heatmap (1 неделя) 🆕
- [ ] **coverage_map.json генерация**
- [ ] **Визуальная миникарта** проекта с цветовым кодированием:
  - 🟢 Хорошо покрыто тестами
  - 🟡 Частично покрыто
  - 🔴 Не покрыто / высокая сложность
- [ ] **CLI export** - `llmstruct export-heatmap`

#### Epic 2.2: LLMStruct Linter (1-2 недели) 🆕
- [ ] **CLI команда** `llmstruct lint`
- [ ] **Правила проверки:**
  - Длинные функции (> N строк)
  - Цикломатическая сложность > threshold
  - Сильные связности между модулями
  - Публичные функции без тестов
  - Security gaps по tag'ам
- [ ] **Конфигурируемые правила** - `.llmstruct-lint.yaml`
- [ ] **CI/CD интеграция** - exit codes для pipeline

#### Epic 2.3: Enhanced Metrics (1 неделя)
- [ ] **Расширенные метрики:**
  - Call depth analysis
  - Dead code detection
  - External dependencies tracking
- [ ] **Performance metrics** - время парсинга, размер вывода
- [ ] **Quality scoring** - общая оценка архитектуры

#### Epic 2.4: Incremental Rebuild (1 неделя) 🆝
- [ ] **File hash storage** - отслеживание изменений
- [ ] **struct-delta.json** - инкрементальные обновления
- [ ] **Smart rebuild** - пересборка только измененных модулей
- [ ] **Performance benchmarks** - замеры ускорения

### Phase 3: 🌟 Innovation Plus (v2.2) - 8-10 недель

#### Epic 3.1: Markdown Static Site Generator (2-3 недели) 🆕
- [ ] **mkdocs/vitepress интеграция**
- [ ] **Автогенерация .md файлов** из struct.json
- [ ] **Static site themes:**
  - Documentation theme
  - Portfolio theme  
  - Code review theme
- [ ] **GitHub Pages ready** - one-click deploy

#### Epic 3.2: LLMStruct DevAssistant API (2-3 недели) 🆕
- [ ] **REST API endpoints:**
  - `POST /explain` - объяснение функции по UID
  - `GET /untested` - список непокрытых функций
  - `POST /suggest-refactor` - предложения рефакторинга
  - `POST /chat` - интерактивный чат с контекстом проекта
- [ ] **LLM provider integration** - OpenAI, Anthropic, local models
- [ ] **Context management** - подача struct.json в промпты

#### Epic 3.3: Interactive TypeScript Viewer (2-3 недели)
- [ ] **Modern frontend stack** - Vite + TypeScript + React/Vue
- [ ] **Core компоненты:**
  - Module tree с uid_components поиском
  - Function inspector с tested_by показом
  - Callgraph visualizer (d3.js/vis.js)
  - Coverage heatmap интеграция
  - Metrics dashboard
- [ ] **PWA capabilities** - offline работа

#### Epic 3.4: Showcase & Integration (1-2 недели) 🆕
- [ ] **LLMStruct Showcase Site** - llmstruct.github.io
- [ ] **Demo projects** - анализ популярных open-source проектов
- [ ] **Cursor/VSCode extensions** - devtools интеграция
- [ ] **PR-bots integration** - автоматические code review комментарии

---

## 🧱 Обновленная техническая архитектура

```
llmstruct/
├── core/                          # Ядро системы
│   ├── schema.py                 # Модели данных v2.1
│   ├── uid_generator.py          # UID + components генерация
│   ├── summary_generator.py      # Smart summary с fallback
│   ├── generator.py              # Главный генератор
│   ├── merger.py                 # Мультиязычное объединение
│   ├── differ.py                 # Incremental & diff анализ
│   └── exporter.py               # Export в разные форматы
├── parsers/                       # Языковые парсеры
│   ├── base.py                   # Базовый интерфейс
│   ├── python/                   # Python AST + coverage
│   ├── go/                       # Go AST анализ
│   └── registry.py               # Парсер регистрация
├── linter/                        # 🆕 Встроенный линтер
│   ├── rules.py                  # Правила проверки
│   ├── config.py                 # Конфигурация
│   └── cli.py                    # CLI интерфейс
├── assistant/                     # 🆕 DevAssistant API
│   ├── api.py                    # REST endpoints
│   ├── llm_provider.py           # LLM интеграция
│   └── context.py                # Context management
├── viewer/                        # Интерактивный просмотр
│   ├── static-site/              # 🆕 Markdown генератор
│   ├── webapp/                   # TypeScript SPA
│   └── showcase/                 # 🆕 Showcase сайт
├── exports/                       # 🆕 Specialized exports
│   ├── heatmap.py                # Coverage heatmap
│   ├── metrics.py                # Metrics dashboard
│   └── github_pages.py           # GH Pages готовый экспорт
├── cli/                           # Enhanced CLI
└── api/                           # REST API
```

---

## 📏 Обновленные критерии успеха

### Phase 1 Success Metrics
- [ ] 100% обратная совместимость с v1.x
- [ ] UID + uid_components генерируется для всех объектов
- [ ] Smart summary работает с 95%+ покрытием
- [ ] tested_by отслеживается точно

### Phase 2 Success Metrics
- [ ] Linter находит 90%+ реальных проблем
- [ ] Coverage heatmap визуально понятна
- [ ] Incremental rebuild ускоряет сборку в 3-5x
- [ ] Метрики помогают принимать решения по рефакторингу

### Phase 3 Success Metrics
- [ ] Static site генерируется за <60 секунд
- [ ] DevAssistant API дает полезные ответы в 80%+ случаев
- [ ] Interactive viewer интуитивен для новых пользователей
- [ ] Showcase привлекает контрибьюторов и пользователей

---

## 🚀 Стратегическое позиционирование

### Конкуренты и позиционирование
- **vs Language Server Protocol:** более специализированно на архитектуру
- **vs Sourcegraph:** локальное решение с LLM интеграцией
- **vs GitHub Copilot:** фокус на анализ, а не генерацию

### Target аудитория
1. **Индивидуальные разработчики** - для понимания legacy кода
2. **Tech leads** - для архитектурных решений
3. **DevOps/QA** - для CI/CD интеграции
4. **Open source maintainers** - для onboarding новых контрибьюторов

---

## 🔄 План запуска

### Open Source стратегия
1. **Phase 1** - internal development
2. **Phase 2** - alpha release для early adopters
3. **Phase 3** - public beta + showcase + community

### Возможные монетизации
- **SaaS версия** с облачными LLM
- **Enterprise features** - advanced security, team collaboration
- **Professional services** - консультации по архитектуре

---

## 💡 Immediate Next Steps

Я готов помочь с любым из вариантов:

### 1. 📋 Создать spec.md как стандарт
- Формальное описание LLMStruct v2.1 format
- JSON Schema с примерами
- API спецификация

### 2. 🧪 Разработать MVP viewer
- Базовый `index.html + app.ts`
- Работа с реальными данными
- Демонстрационная версия

### 3. 🛠️ Начать с конкретного эпика
- Выбрать приоритетный блок
- Детальная техническая спецификация
- Прототип реализации

**Какой путь выбираем для старта?** 🚀

---

**Готов к реализации уровня LSP/pyright!** 📈 

## 🧩 Multi-Container Architecture (v2.1+)

- Один контейнер: **Node.js/TypeScript middleware** (proxy/router, расширяемый, multi-tenant)
    - Принимает запросы от клиентов (CLI, Cursor, LLM, API)
    - Маршрутизирует по project_id/struct_path
    - Управляет безопасностью (project registry, white-list, enum)
    - Легко расширяется для новых MCP-тулзов и интеграций
- Второй контейнер: **llmstruct** (CLI, MCP, core)
    - Обрабатывает запросы к struct/ (по project_id/struct_path)
    - Генерирует, валидирует, анализирует struct/
- **struct/** для всех проектов хранится в общем Docker volume, монтируется в оба контейнера
- Такая архитектура обеспечивает масштабируемость, безопасность, расширяемость и удобную интеграцию с внешними инструментами

## 🗓️ Обновленный план реализации

- [ ] Реализовать multi-container архитектуру: Node.js/TS middleware + llmstruct core/MCP
- [ ] Все новые фичи и интеграции должны работать через middleware (proxy)
- [ ] struct/ для проектов хранится в общем volume, доступен обоим контейнерам
- [ ] Middleware обеспечивает маршрутизацию, безопасность, расширяемость MCP-инструментов

## 🧩 Multi-tenant Proxy & Security

- [ ] FastAPI proxy/router для Cursor и внешних клиентов
- [ ] Proxy получает project_token/project_id, подставляет struct_path для backend MCP
- [ ] Project registry и white-list реализованы в proxy
- [ ] Enum для выбора проекта в tool schema (нет raw path)
- [ ] Все новые фичи должны работать с несколькими struct/ (разные проекты)

- [ ] MCP/CLI/Proxy: поддержка выбора проекта (struct_path/project_id) во всех командах и endpoint'ах
- [ ] Все новые фичи (heatmap, linter, metrics, diff, viewer, DevAssistant API) — только на struct/ и с поддержкой нескольких проектов
- [ ] Безопасность: project registry, enum для выбора проекта, white-list, запрет raw path
- [ ] Proxy/multi-tenant слой для Cursor и внешних клиентов 