# User Feedback #001 - Roadmap Audit

**Дата:** 25.06.2024  
**Автор:** kpblc  
**Тип:** Экспертный аудит roadmap  
**Статус:** 🟢 Принят к реализации

---

## 🧠 Аудит по фазам

### Phase 1: 🏗️ Core
**Оценка:** 👍 Отлично

**Единственное уточнение:**
- **UID Components:** при генерации желательно хранить не только `uid`, но и `uid_components` 
  - Пример: `["sboxmgr", "exporter", "SingboxExporter", "export"]`
  - **Цель:** облегчит работу в UI и в поиске

### Phase 2: 📈 Enhancement  
**Оценка:** Очень сильный блок

**Улучшения Summary генерации:**
- Лучше изначально строить не LLM-only, а с fallback:
  1. `docstring → truncate → summary`
  2. если пусто → `gen from LLM`
  3. кэшировать в `summary_generated`

**Test coverage расширение:**
- Сейчас: `tested: true` на уровне объекта
- **Добавить:** список тестов, его вызывающих
- Формат: `"tested_by": ["tests/test_exporter.py::test_export_config"]`

### Phase 3: 🌟 Innovation
**Оценка:** Амбициозно, но реалистично

**Предложения по Viewer:**

#### 🧩 Начать с режима Markdown Static Site
- mkdocs или vitepress с автогенерацией .md
- проще валидировать, можно делать PWA позже

#### 🔌 Планировать devtools-интеграции
- расширение для Cursor или Codeium-like интерфейс на основе index.json

#### Security tags расширение
- Не забыть о: `@input-validated`, `@public-entrypoint`, `@auth-required`

---

## 📎 Дополнения и предложения

### 1. 📊 Coverage Heatmap
- **JSON:** `coverage_map.json`
- **UI:** миникарта проекта с цветами по покрытию, CC, тестам

### 2. 🛠️ LLMStruct Linter
**CLI-команда:** `llmstruct lint`

**Проверки:**
- длинные функции
- цикломатическая сложность > threshold
- сильные связности  
- публичные функции без тестов
- потенциальные security gaps по tag'ам

### 3. 🧠 LLMStruct DevAssistant
**API-интерфейс:** `api/assistant.py`

**Возможности:**
- `explain(uid)`
- `list_untested()`
- `suggest_refactor(uid)`
- `llmstruct chat` (с prompt'ом внутри)

### 4. 🌍 LLMStruct Showcase Site
- Генерация `llmstruct.github.io` (или internal portal)
- Демо для портфолио, контрибьюторов, интеграторов

### 5. 🔄 Incremental Rebuild
**Добавить в Phase 2/3:**
- хранилище хэшей на уровне файлов
- генерация `struct-delta.json`
- пересборка только модулей с изменениями

---

## 📌 Экспертная оценка

> 📈 Этот план на уровне архитектуры LSP или pyright — зрелый, масштабируемый, с огромным потенциалом.

## 💡 Итоговые советы

| Что | Зачем |
|-----|-------|
| 🧭 Добавить assistant/linter API | Для CI/UX/LLM |
| 🧱 UID-components | Для UI и быстрых выборок |
| 🛠️ Внедрить tested_by и used_in | Повысит прозрачность |
| 🔁 Ввести incremental-режим | Повысит производительность |
| 🌐 Готовить showcase-режим | PR-боты, портфолио, gh-pages |
| 📚 Начать писать spec/schema как документацию | Чтобы в будущем иметь полноценный стандарт |

---

## 🚀 Стратегическая перспектива

**Уровень проекта:** OpenCodeAtlas-class framework  
**Направление:** open-source или SaaS  
**Потенциал:** Публичный фреймворк промышленного уровня

---

## 🔄 Предложения к реализации

**Варианты помощи:**
1. оформить `spec.md` как стандарт
2. сгенерировать schema + примеры  
3. разработать MVP `viewer/index.html + app.ts`

---

**Статус:** ✅ Feedback интегрирован в roadmap v2.1 