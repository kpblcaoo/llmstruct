# Внутренняя настройка llmstruct

Руководство по настройке для команды `llmstruct` (@kpblcaoo, @momai, @ivan-ib). Фокус: локальная разработка, Qwen, VPS.

## Локальная настройка
1. **Клонировать репо**:
   ```bash
   git clone https://github.com/kpblcaoo/llmstruct.git
   cd llmstruct
   ```
2. **Установить**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Запустить Qwen-1.5B** (3060Ti, TSK-016):
   ```bash
   python src/llmstruct/cli.py --model qwen-1.5b --spec struct.json
   ```
   - Оптимизация VRAM: Использовать квантование (LoRA, TSK-016).
4. **Тестировать парсер**:
   ```bash
   python src/llmstruct/parser.py --input src/ --output struct.json
   pytest src/tests/test_parser.py
   ```

## Настройка VPS (TSK-018)
- **Деплой**: Использовать Nginx (@momai, TSK-014).
- **Запустить Qwen-7B** (v0.3.0):
   ```bash
   docker run -v ./struct.json:/app/struct.json llmstruct:qwen-7b
   ```
- **Мониторинг**: Grafana для метрик (TSK-015, @momai).

## Заметки
- Проверять лимиты API (Anthropic, Grok, TSK-014).
- Использовать `internal/roadmap.md` для приоритетов.
- Пинг @kpblcaoo для онбординг-колла 1–2ч (TSK-019).