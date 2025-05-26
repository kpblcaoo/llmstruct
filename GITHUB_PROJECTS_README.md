# GitHub Projects Export - Quick Start

## Что реализовано

✅ **Полная система экспорта GitHub Projects (gh-view-v1)**

### Основные файлы:
- `src/llmstruct/gh_view.py` - основной модуль экспорта
- `scripts/export_to_github_projects.py` - CLI скрипт экспорта  
- `scripts/gh_export.sh` - bash обертка для удобства
- `docs/gh_view.md` - полная документация
- `data/gh_mapping.json` - сопоставление ID (создается автоматически)

### Быстрый тест:

1. **Проверка данных:**
   ```bash
   cd /home/kpblc/projects/github/llmstruct
   python test_export.py
   ```

2. **Dry-run экспорт:**
   ```bash
   python scripts/export_to_github_projects.py 1 --dry-run
   ```

3. **Реальный экспорт в GitHub Project #1:**
   ```bash
   python scripts/export_to_github_projects.py 1 --execute
   ```

### Основные функции:

- ✅ Загрузка официальных данных из `data/tasks.json` и `data/ideas.json`
- ✅ Форматирование для GitHub Project cards
- ✅ Сопоставление статусов (proposed → Todo, completed → Done, etc.)
- ✅ Фильтрация по статусу и приоритету
- ✅ Dry-run режим для безопасного тестирования
- ✅ ID mapping для предотвращения дублей
- ✅ GitHub CLI интеграция
- ✅ Полная документация

### Примеры использования:

```bash
# Только задачи
python scripts/export_to_github_projects.py 1 --execute --tasks-only

# Только высокоприоритетные идеи  
python scripts/export_to_github_projects.py 1 --execute --ideas-only --priority high

# Активные задачи для конкретного репозитория
python scripts/export_to_github_projects.py 1 --execute --owner kpblcaoo --repo llmstruct --status proposed in_progress

# Удобная bash обертка
./scripts/gh_export.sh 1 --dry-run
./scripts/gh_export.sh 1 --execute --tasks-only
```

## Статус задачи TSK-143

✅ **COMPLETED** - Задача TSK-143 "Implement GitHub visualization/graph (gh-view-v1)" выполнена полностью:

- Создан модуль `gh_view.py` с классом `GitHubProjectsExporter`
- Реализован CLI скрипт с полной поддержкой параметров
- Добавлена конфигурация в `llmstruct.toml`
- Создана исчерпывающая документация `docs/gh_view.md`
- Обновлены cross-references в `docs.json` и `tasks.json`
- Система готова к использованию

## Следующие шаги

1. Создать GitHub Project в вашем репозитории
2. Запустить dry-run для тестирования
3. Выполнить реальный экспорт
4. При необходимости настроить фильтры

Полную документацию см. в `docs/gh_view.md`
