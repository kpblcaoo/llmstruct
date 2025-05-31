# 🚀 PHOENIX: ШПАРГАЛКА ДЛЯ БЫСТРОГО ВЫПОЛНЕНИЯ

## 📌 СТАРТ (копировать и выполнить)

```bash
cd /home/sma/projects/llmstruct/llmstruct
source venv/bin/activate
git checkout -b phoenix-final
mkdir -p .PHOENIX/{schemas,docs,archive,consolidated}
```

---

## 🔄 ФАЗА 0: АНАЛИЗ ДУБЛИКАТОВ

### Команда 1: Генерация отчета
```bash
llmstruct analyze-duplicates --save-report .PHOENIX/duplicates_report.json --format json
```

### Команда 2: Стратегия консолидации
```bash
curl -s -X POST http://localhost:8000/api/v1/files/read?path=.PHOENIX/duplicates_report.json | \
jq -r '.content' | \
curl -s -X POST http://localhost:8000/api/v1/chat/ollama \
  -H "Content-Type: application/json" \
  -d @- << EOF | jq -r '.response' > .PHOENIX/consolidation_strategy.md
{
  "message": "Analyze this duplication report: $(cat -). Create consolidation strategy: 1) Group all 8 bot implementations 2) List duplicate init/main functions 3) Suggest merge strategy. Be specific.",
  "model": "wizardlm2:7b"
}
EOF
```

### Команда 3: Схема текущего состояния
```bash
curl -s -X POST http://localhost:8000/api/v1/chat/ollama \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create Mermaid diagram of llmstruct current state. Show: FastAPI server, CLI tools, 8 telegram bot versions, workflow system, metrics, cache. Mark duplication areas. Keep high-level but clear.",
    "model": "qwen2.5:7b"
  }' | jq -r '.response' > .PHOENIX/schemas/current_state.mmd
```

---

## 🏗️ ФАЗА 1: КОНСОЛИДАЦИЯ

### Команда 4: Найти все боты
```bash
find . -name "*bot*.py" -type f | grep -E "(telegram|chat)" | sort > .PHOENIX/all_bots.txt
cat .PHOENIX/all_bots.txt
```

### Команда 5: Анализ ботов
```bash
# Для каждого бота создаем краткое описание
for bot in $(cat .PHOENIX/all_bots.txt); do
  echo "=== $bot ===" >> .PHOENIX/bot_analysis.md
  curl -s "http://localhost:8000/api/v1/files/read?path=$bot" | \
  jq -r '.content' | head -100 | \
  curl -s -X POST http://localhost:8000/api/v1/chat/ollama \
    -H "Content-Type: application/json" \
    -d @- << EOF | jq -r '.response' >> .PHOENIX/bot_analysis.md
{
  "message": "List key features of this bot: $(cat -). Output: 1) Commands supported 2) API integrations 3) Unique features",
  "model": "deepseek-coder:6.7b"
}
EOF
done
```

### Команда 6: Выбор лучшего бота
```bash
curl -s -X POST http://localhost:8000/api/v1/chat/ollama \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Based on analysis in .PHOENIX/bot_analysis.md, which bot should be the main one? User prefers integrations/telegram_bot. Create comparison table.\",
    \"model\": \"deepseek-coder:6.7b\",
    \"context\": \"$(cat .PHOENIX/bot_analysis.md | head -1000)\"
  }" > .PHOENIX/bot_winner.md
```

---

## 🎨 ФАЗА 2: СХЕМЫ

### Команда 7: Workflow схема
```bash
curl -s -X POST http://localhost:8000/api/v1/chat/ollama \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create detailed Mermaid flowchart for LLMStruct workflow. Show: User->Bot->LLM->Cache->Response flow. Include FastAPI, CLI, metrics. Optimize for LLM readability with clear labels.",
    "model": "wizardlm2:7b"
  }' | jq -r '.response' > .PHOENIX/schemas/workflow.mmd
```

### Команда 8: Компонентные схемы (пакетная генерация)
```bash
for comp in "FastAPI_Server" "Telegram_Bot" "LLM_Manager" "Cache_System"; do
  curl -s -X POST http://localhost:8000/api/v1/chat/ollama \
    -H "Content-Type: application/json" \
    -d "{
      \"message\": \"Create Mermaid class diagram for $comp. Show main classes, methods, relationships. Add comments for LLM understanding.\",
      \"model\": \"starcoder2:7b\"
    }" | jq -r '.response' > .PHOENIX/schemas/${comp}.mmd
  echo "✅ Generated $comp schema"
  sleep 2
done
```

---

## 🔧 ФАЗА 3: РЕФАКТОРИНГ

### Команда 9: Новая структура
```bash
cat > .PHOENIX/new_structure.md << 'EOF'
src/llmstruct/
├── core/           # Base classes, utilities
├── providers/      # LLM providers (grok, anthropic, ollama)
├── interfaces/     # User interfaces
│   ├── api/       # FastAPI
│   ├── cli/       # CLI tools
│   └── bot/       # Telegram bot
├── workflow/       # Session management, state
├── metrics/        # Tracking and analytics
└── cache/          # Caching system
EOF
```

### Команда 10: Пример рефакторинга
```bash
# Тестовый рефакторинг одного модуля
MODULE="src/llmstruct/cache_manager.py"
curl -s "http://localhost:8000/api/v1/files/read?path=$MODULE" | \
jq -r '.content' | \
curl -s -X POST http://localhost:8000/api/v1/chat/ollama \
  -H "Content-Type: application/json" \
  -d @- << EOF | jq -r '.response' > .PHOENIX/refactored_example.py
{
  "message": "Refactor this code for LLM-first design: $(cat -). Add: 1) Comprehensive docstrings 2) Type hints 3) Clear method purposes 4) Context comments. Keep all functionality.",
  "model": "deepseek-coder:6.7b"
}
EOF
```

---

## 📚 ФАЗА 4: ДОКУМЕНТАЦИЯ

### Команда 11: README
```bash
curl -s -X POST http://localhost:8000/api/v1/chat/ollama \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create professional README for LLMStruct after restructuring. Include: badges, features (multi-LLM support, caching, metrics), quick start, architecture overview. Emphasize LLM-first design.",
    "model": "qwen2.5:7b"
  }' | jq -r '.response' > .PHOENIX/README_new.md
```

### Команда 12: LLM Guide
```bash
curl -s -X POST http://localhost:8000/api/v1/chat/ollama \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create LLM_DEVELOPER_GUIDE.md explaining how AI agents should work with this codebase. Include: entry points, context management, self-modification guidelines, API usage patterns.",
    "model": "wizardlm2:7b"
  }' | jq -r '.response' > .PHOENIX/docs/LLM_DEVELOPER_GUIDE.md
```

---

## ✅ ФАЗА 5: ВАЛИДАЦИЯ

### Команда 13: Проверка целостности
```bash
# Создаем чеклист
cat > .PHOENIX/validation_checklist.md << 'EOF'
- [ ] All 8 bots consolidated into one
- [ ] Duplicates removed (check with llmstruct analyze-duplicates)
- [ ] integrations/telegram_bot preserved
- [ ] All APIs working (Grok, Anthropic, Ollama)
- [ ] Documentation complete
- [ ] Schemas created for all components
- [ ] Tests passing
EOF

# Автоматическая проверка
llmstruct analyze-duplicates | grep "Total duplicate" > .PHOENIX/final_duplicates.txt
```

### Команда 14: Финальный отчет
```bash
curl -s -X POST http://localhost:8000/api/v1/chat/ollama \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"Create final restructuring report. Compare: Before (272 modules, 20.5% duplicates, 8 bots) vs After (check .PHOENIX folder). List achievements, improvements, next steps.\",
    \"model\": \"qwen2.5:7b\",
    \"context\": \"$(ls -la .PHOENIX/)\"
  }" > .PHOENIX/FINAL_REPORT.md
```

---

## 🔄 CHECKPOINTS (для переключения LLM)

### При затруднениях Ollama:
```bash
# Переключение на Grok/Claude для сложных архитектурных вопросов
echo "Текущий вопрос: [описание проблемы]" > .PHOENIX/checkpoint_N.md
echo "Нужна помощь с: [архитектура/рефакторинг/документация]" >> .PHOENIX/checkpoint_N.md
# Затем обратиться к Claude/GPT с этим контекстом
```

### Быстрая проверка прогресса:
```bash
echo "=== PHOENIX Progress ===" 
echo "Duplicates removed: $(llmstruct analyze-duplicates | grep 'Total duplicate')"
echo "Bots consolidated: $(ls .PHOENIX/archive/bots/ 2>/dev/null | wc -l) archived"
echo "Schemas created: $(ls .PHOENIX/schemas/*.mmd 2>/dev/null | wc -l)"
echo "Docs generated: $(ls .PHOENIX/docs/*.md 2>/dev/null | wc -l)"
```

---

## 💡 СОВЕТЫ

1. **Используй `| jq -r '.response'`** для чистого вывода из Ollama
2. **Сохраняй промежуточные результаты** в .PHOENIX/
3. **При больших файлах** используй `head -n 1000` перед отправкой в LLM
4. **Делай git commit** после каждой успешной фазы
5. **Если Ollama медленная** - уменьши контекст или переключись на mistral

---

**🔥 Готово к выполнению! Просто копируй команды и выполняй по порядку.** 