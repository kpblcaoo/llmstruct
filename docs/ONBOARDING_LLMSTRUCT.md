# Onboarding: llmstruct Workflow, Project Data & LLM-Orchestration

---

## Быстрый старт: промт для запуска AI/LLM-сессии

Скопируйте и вставьте нижеследующий промт при запуске новой сессии или чата с AI — это обеспечит корректный старт работы по всем правилам проекта.

```
Restore the working context for the llmstruct project. Use user rules, .cursor/rules/, data/ai_workflow.json, project_manifest.json, and prompts_collection.json as your main references. Follow the branch policy: do not make any changes outside of tasks, epics, or ideas unless you are in an active session (a new branch for a task or epic). Log all key actions and warn about risks if working
```

- Этот промт предназначен передачи AI/LLM в начале работы.
- Prompts for AI/LLM: English only
- User-facing text: Russian (or user-selected language)

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

## Важно!
- После завершения эпика и перед архивированием или проверкой файлов обязательно дождитесь merge PR и выполните git pull develop. Это предотвратит потерю данных и обеспечит актуальность всех файлов.

**Вопросы, предложения и обратная связь приветствуются! Следуйте этим практикам для эффективной командной работы и автоматизации с LLM.** 

Все project data JSON-файлы (ideas, tasks, insights, prs и др.) должны храниться в папке `data/`.

---

## 10. Сессионный контроль и тотальное логирование
- Для всех рабочих ситуаций (эпики, планирование, обсуждение, debug, тесты и др.) используйте сессионный контроль: отдельные event_log, tech_log, meta-log для каждой сессии.
- Именование: data/sessions/<session_type>_<date>_<custom>.json
- При смене типа работы — создавайте новые логи.
- Логируйте каждое взаимодействие: действия пользователя, AI, системные события.
- AI обязан подмечать и фиксировать возможности улучшения workflow (insights.json или отдельный лог).
- Регулярно анализируйте логи для выявления паттернов и улучшений. 

## Language Policy for Prompts and Communication

- All prompts intended for AI/LLM (prompts_collection.json, workflow, automation) must be written in English for maximum compatibility and reproducibility.
- All communication, advice, and discussion for the user can be in Russian (or any language the user prefers).
- This ensures LLM compatibility and user comfort.

### Example: Start Prompt for New Session

```
Восстанови рабочий контекст по проекту llmstruct. Ориентируйся на user rules, .cursor/rules/, data/ai_workflow.json, project_manifest.json, prompts_collection.json. Соблюдай branch policy: не изменяй ничего вне сессии/ветки, логируй все действия, предупреждай о рисках вне сессии. Давай советы объективно, не подстраиваясь под мои ожидания. Общайся со мной на русском, но промты для AI используй на английском.
```

- Prompts for AI/LLM: English only
- User-facing text: Russian (or user-selected language) 