# Best Practices: llmstruct Project Data & LLM-Orchestration

## 1. Архивирование project data
- **Перед любыми изменениями** project data (tasks, ideas, insights, prs) обязательно создавайте архивную копию в `data/archived_jsons/`.
- Если архив отсутствует, восстановите из git: 
  ```bash
  git show HEAD:data/tasks.json > data/archived_jsons/tasks.archived.json
  ```

## 2. Использование меток (tags)
- Все сущности снабжайте массивом `tags` для фильтрации, автоматизации и LLM-оркестрации.
- Описание ключевых меток и best practices — в [`data/tags_reference.json`](../data/tags_reference.json).

## 3. Связывание сущностей
- Для задач, идей, инсайтов и PR используйте поля:
  - `epic` — принадлежность к эпику
  - `tags` — для фильтрации и автоматизации
  - `related_tasks`, `related_ideas`, `related_insights`, `related_prs` — для сквозной навигации

## 4. Lessons learned и инсайты
- После любого нештатного события или улучшения workflow фиксируйте инсайт в [`data/insights.json`](../data/insights.json) с тегами `lessons_learned`, `workflow`.

## 5. Генерация CLI-команд для пользователя
- После любого изменения project data предлагайте CLI-команды для проверки, фильтрации или автоматизации.
- Примеры команд:
  ```bash
  python scripts/epic_roadmap_manager.py epic --epic-id meta_workflow_management
  python scripts/epic_roadmap_manager.py show-links --epic-id meta_workflow_management
  ```

## 6. Использование коллекции промтов
- Для LLM-оркестрации и автоматизации используйте [`data/prompts_collection.json`](../data/prompts_collection.json).
- Промты охватывают типовые сценарии: архивирование, lessons learned, связывание сущностей, генерация CLI-команд, документирование best practices.

## 7. Документирование и поддержка
- При внедрении новых практик или меток обязательно обновляйте `tags_reference.json` и/или этот файл.
- Все изменения и ошибки логируйте в meta-log или insights.json для ретроспективы и улучшения процессов.

## Best practice
- Всегда дожидайтесь merge PR и git pull develop перед архивированием или проверкой актуальности файлов. Это защищает от потери данных и гарантирует, что все изменения попадут в основную ветку.

---

**Система поддерживает масштабирование, интеграцию с Kanban/API/CLI и прозрачную работу с LLM. Следуйте этим практикам для эффективной автоматизации и командной работы!** 