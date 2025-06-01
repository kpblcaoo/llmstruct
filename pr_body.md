epic(epic_ai_workflow_rules_2024): финализация — структура правил, ссылки, retrospective, логи

Эпик завершён: внедрена и стандартизирована архитектура AI workflow/rules.

**Что реализовано:**
- Заполнена и согласована структура .cursor/rules/ (cli-commands, logging-and-retrospective, ai-capabilities)
- Все ссылки и структура согласованы с ai_workflow.json и документацией
- Внедрён стандарт завершения эпика: финальный коммит, PR через gh, возврат в develop, шаблон описания PR
- Lessons learned и retrospective зафиксированы в insights.json

**Ключевые файлы:**
- .cursor/rules/cli-commands.mdc
- .cursor/rules/logging-and-retrospective.mdc
- .cursor/rules/ai-capabilities.mdc
- data/ai_workflow.json
- data/insights.json (INS-2024-06-11-001, INS-2024-06-11-002, INS-2024-06-11-003)
- data/epic_logs/epic_ai_workflow_rules_2024/event_log.jsonl

**Lessons learned:**
- Формализация структуры и ссылок минимизирует дублирование и ускоряет онбординг
- Lessons learned и best practices должны фиксироваться сразу
- Все детали вынесены по ссылкам, базовые правила — в настройках AI
- Стандарт завершения эпика (финальный коммит, PR, возврат в develop) ускоряет интеграцию и снижает ошибки

**Рекомендации:**
- Поддерживать структуру и ссылки в актуальном состоянии
- Регулярно проводить ретроспективу и обновлять best practices

---

_После мержа:_
- Вернуться в develop:  
  ```bash
  git checkout develop
  git pull
  ```
- (Опционально) Архивировать логи эпика 