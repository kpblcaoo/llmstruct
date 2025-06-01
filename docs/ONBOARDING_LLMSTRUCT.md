# Onboarding: llmstruct Workflow, Project Data & LLM-Orchestration

Добро пожаловать в обновлённую экосистему llmstruct! Этот гайд поможет быстро освоить новые подходы к работе с задачами, идеями, инсайтами, PR и автоматизацией с помощью LLM.

---

## 1. Основные файлы и их назначение
- **`data/tasks.json`** — задачи (issues, workflow, automation)
- **`data/ideas.json`** — идеи (feature requests, улучшения, концепты)
- **`data/insights.json`** — инсайты, lessons learned, ретроспектива
- **`data/prs.json`** — pull requests, история изменений
- **`data/tags_reference.json`** — справочник по меткам (tags) и best practices
- **`data/prompts_collection.json`** — коллекция промтов для LLM-оркестрации и автоматизации
- **`docs/BEST_PRACTICES_LLMSTRUCT.md`** — best practices по workflow, автоматизации, LLM

---

## 2. Архивирование project data
- **Перед любыми изменениями** project data создавайте архивную копию в `data/archived_jsons/`.
- Если архив отсутствует, восстановите из git:
  ```bash
  git show HEAD:data/tasks.json > data/archived_jsons/tasks.archived.json
  ```

---

## 3. Метки (tags) и справочник
- Все сущности снабжайте массивом `tags` для фильтрации, автоматизации и LLM-оркестрации.
- Описание ключевых меток и best practices — в [`data/tags_reference.json`](../data/tags_reference.json).

---

## 4. Связи между сущностями
- Используйте поля:
  - `epic` — принадлежность к эпику
  - `tags` — для фильтрации и автоматизации
  - `related_tasks`, `related_ideas`, `related_insights`, `related_prs` — для сквозной навигации

---

## 5. Lessons learned и инсайты
- После любого нештатного события или улучшения workflow фиксируйте инсайт в [`data/insights.json`](../data/insights.json) с тегами `lessons_learned`, `workflow`.

---

## 6. Коллекция промтов для LLM
- Используйте [`data/prompts_collection.json`](../data/prompts_collection.json) для типовых сценариев автоматизации и LLM-оркестрации.
- Примеры промтов: архивирование, фиксация инсайтов, связывание сущностей, генерация CLI-команд, документирование best practices.

---

## 7. CLI-команды для пользователя
- Примеры команд для поиска, фильтрации, отображения связей:
  ```bash
  python scripts/epic_roadmap_manager.py epic --epic-id meta_workflow_management
  python scripts/epic_roadmap_manager.py show-links --epic-id meta_workflow_management
  python scripts/epic_roadmap_manager.py tasks --filter-tag workflow
  python scripts/epic_roadmap_manager.py ideas --filter-tag prompts
  python scripts/epic_roadmap_manager.py insights --filter-tag lessons_learned
  python scripts/epic_roadmap_manager.py prs --filter-status open
  ```
- Для просмотра справочника по меткам и коллекции промтов:
  ```bash
  cat data/tags_reference.json | jq
  cat data/prompts_collection.json | jq
  ```

---

## 8. Best practices и поддержка
- Следуйте рекомендациям из [`docs/BEST_PRACTICES_LLMSTRUCT.md`](../docs/BEST_PRACTICES_LLMSTRUCT.md).
- При внедрении новых практик или меток обновляйте справочник и этот гайд.
- Все изменения и ошибки логируйте в meta-log или insights.json для ретроспективы и улучшения процессов.

---

## 9. Советы для эффективной работы
- Используйте связи и метки для быстрой навигации и автоматизации.
- Фиксируйте инсайты и lessons learned сразу — это ускоряет развитие проекта.
- Не бойтесь расширять коллекцию промтов и best practices — это облегчает онбординг новых участников.
- Всегда предлагайте CLI-команды для проверки и автоматизации после изменений.

---

## Примеры CLI для анализа логов (logging_transparency_audit)

Для просмотра event_log по текущему эпику:
```bash
python scripts/log_viewer.py --epic logging_transparency_audit --format table
```

Фильтрация по типу события (например, только действия AI):
```bash
python scripts/log_viewer.py --epic logging_transparency_audit --event-type ai_action --format table
```

Вывод в формате JSON:
```bash
python scripts/log_viewer.py --epic logging_transparency_audit --format json
```

Поиск по request_id:
```bash
python scripts/log_viewer.py --epic logging_transparency_audit --request-id REQ-004 --format json
```

> Все действия по логированию, тестированию и анализу фиксируются в event_log и tech_log. Для ретроспективы и улучшения процессов используйте фильтрацию и анализ логов.

---

## Стандартизированный процесс ведения и завершения эпика

### 1. Оформление эпика
- Создайте отдельную ветку от develop: `epic/<epic_id>-to-develop`
- Оформите event_log и tech_log для эпика в `data/epic_logs/<epic_id>/`
- Добавьте инициирующую идею в `ideas.json` и задачу в `tasks.json`
- Все действия фиксируйте в логах

### 2. Ведение эпика
- Все ключевые действия и reasoning фиксируются в event_log и tech_log
- Для новых функций используйте анализ целесообразности: если нет явного запроса — фиксируйте идею, не реализуйте без согласования
- Вся работа по эпику ведётся только в своей ветке

### 3. Завершение эпика
- Финальный коммит всех изменений
- Summary: что реализовано, ключевые файлы, lessons learned, рекомендации
- Анализ процесса: что сработало, что улучшить
- Оформление PR по шаблону (см. ниже)
- Архивация логов эпика (перемещение/zip)
- Все действия фиксируются в event_log и tech_log

### 4. Автоматизация ретроспективы
- По завершении эпика AI формирует summary, lessons learned, рекомендации и добавляет их в `insights.json`

### 5. Шаблон PR по эпику
```
epic(<epic_id>): summary изменений
- Что реализовано
- Ключевые файлы
- Lessons learned
- Рекомендации
- (Опционально) ссылки на инсайты, идеи, задачи
```

### 6. Best practices
- Не реализовывать опциональные функции без явной необходимости — фиксируйте идеи и согласовывайте
- Все новые функции проходят анализ целесообразности
- Регулярно проводите ретроспективу и обновляйте стандарты
- Архивируйте логи эпика после завершения

---

**Вопросы, предложения и обратная связь приветствуются! Следуйте этим практикам для эффективной командной работы и автоматизации с LLM.** 