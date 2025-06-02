# LLMStruct Prompt & Workflow Integration Architecture

## 1. Общая схема
- Все workflow-этапы, чеклисты и автоматизации строятся на промтах из prompts_collection.json.
- AI использует ai_workflow.json/project_manifest.json для поиска нужных промтов (по id).
- attention_marker и llm_context в файлах сессий/эпиков задают фокус для AI и LLM.
- Ollama/LLM вызывается с промтом и контекстом, возвращает результат для логирования и дальнейших действий.

## 2. Взаимодействие компонентов

```
[User/AI] --(start/continue workflow)--> [AI reads ai_workflow.json/project_manifest.json]
   |                                             |
   v                                             v
[AI finds prompt id] <---(links)--- [prompts_collection.json]
   |                                             |
   v                                             v
[AI applies template, fills variables]         [attention_marker/llm_context]
   |                                             |
   v                                             v
[AI sends prompt+context to Ollama/LLM]  <---(context)--|
   |
   v
[LLM response] --(actions/summary/cli)--> [Logs, User, Next step]
```

## 3. Пример сценария
1. Пользователь инициирует новый эпик.
2. AI читает ai_workflow.json, находит id промта для старта эпика.
3. AI берёт шаблон из prompts_collection.json, подставляет переменные (epic_id, branch и т.д.).
4. Если в сессии есть attention_marker/llm_context — AI учитывает их при формировании промта.
5. AI отправляет промт и контекст в Ollama/LLM.
6. LLM возвращает чеклист/шаблон/summary — AI логирует результат, предлагает действия пользователю.

## 4. Логирование и обратная связь
- Все действия AI и LLM логируются (event_log, tech_log, meta-log).
- Если промт/attention_marker устарел — AI предлагает обновить.
- Пользователь может вручную корректировать промты, attention_marker, llm_context.

## 5. Best Practices
- Промты — на английском, для совместимости с LLM.
- attention_marker/llm_context — кратко и по делу, только для текущего фокуса.
- Все изменения логируются и доступны для аудита.

---

## Диаграмма (workflow):

```
[User/AI] -> [AI: read workflow/manifest] -> [Find prompt id] -> [prompts_collection.json]
      |                                             |
      v                                             v
[Fill template vars] <--- [attention_marker/llm_context]
      |
      v
[Send to Ollama/LLM]
      |
      v
[LLM response] -> [Log/Action/Next step]
``` 