# Prompts for AI: Architecture and Workflow

## 1. Prompts Collection Structure
- Все промты для AI хранятся в prompts_collection.json (англоязычный формат).
- Структура промта:
  ```json
  {
    "id": "epic_full_setup_standard",
    "title": "Epic full setup (standard)",
    "template": "1. Create branch epic/<epic_id>-to-develop from develop\n2. Initialize event_log and tech_log for the epic\n3. Add initiating idea to ideas.json\n4. Add task to tasks.json\n5. Log all actions",
    "usage": "Used by AI and CLI to standardize epic setup."
  }
  ```
- В prompts_collection.json могут быть секции: workflow, code, debug, retrospective, etc.

## 2. How AI Uses Prompts
- AI ищет нужный промт по id или по сценарию (например, "epic_finish_standard").
- Если промт не найден — AI сообщает пользователю и предлагает добавить новый.
- AI может комбинировать промты (например, для сложных workflow).
- Промты используются для генерации чеклистов, шаблонов, CLI-команд, summary и т.д.

## 3. Attention Markers & Reminders
- В каждом project data-файле могут быть поля:
  - `llm_context`: краткое описание текущего фокуса/контекста для AI.
  - `attention_marker`: явная метка, на что AI должен обратить внимание (например, "focus_on_epic_links_cli_test").
- AI при старте сессии/эпика читает эти поля и использует их для выбора промтов и генерации действий.
- Если attention_marker устарел — AI предлагает обновить его.

## 4. Workflow Integration
- В ai_workflow.json и project_manifest.json хранятся ссылки на актуальные промты (по id).
- При старте нового workflow-этапа AI ищет промт по id, применяет шаблон, логирует действия.
- Пользователь может расширять prompts_collection.json — AI автоматически подхватит новые промты.

## 5. Ollama/LLM Integration
- Ollama/LLM вызывается с промтом из prompts_collection.json (template + context).
- AI может автоматически подставлять переменные (epic_id, branch, etc.) в шаблон промта.
- Ответ LLM анализируется и логируется, при необходимости — уточняется промт или attention_marker.

## 6. Best Practices
- Все промты — на английском, для совместимости с LLM.
- Для каждого нового workflow-этапа — отдельный промт.
- Все изменения prompts_collection.json логируются.
- Пользователь может просматривать, редактировать и добавлять промты через CLI или редактор.

---

## Пример схемы (диаграмма):

```
[User/AI] --(start workflow)--> [AI reads ai_workflow.json/project_manifest.json]
   |                                             |
   v                                             v
[AI finds prompt id] <---(links)--- [prompts_collection.json]
   |                                             |
   v                                             v
[AI applies template, fills variables]         [attention_marker/llm_context]
   |                                             |
   v                                             v
[AI sends prompt to Ollama/LLM]  <---(context)--|
   |
   v
[LLM response] --(actions/summary/cli)--> [Logs, User, Next step]
``` 