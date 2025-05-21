# Внутренняя настройка llmstruct

**Статус**: Черновик  
**Версия**: 0.1.0  
**Последнее обновление**: 2025-05-18T23:00:27.888546Z  
**Автор**: Mikhail Stepanov ([kpblcaoo](https://github.com/kpblcaoo), kpblcaoo@gmail.com)

## 1. Локальная настройка

1. **Клонировать репо**:
   ```bash
   git clone https://github.com/kpblcaoo/llmstruct.git
   cd llmstruct
   ```
2. **Установить**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Запустить Qwen-1.5B** (TSK-016):
   ```bash
   python src/llmstruct/cli.py --model qwen-1.5b --spec struct.json
   ```

## 2. Настройка VPS (TSK-018)

- **Деплой**: Использовать Nginx (TSK-014).
- **Запустить Qwen-7B** (v0.3.0):
   ```bash
   docker run -v ./struct.json:/app/struct.json llmstruct:qwen-7b
   ```
- **Мониторинг**: Grafana для метрик (TSK-015).

## 3. Заметки

- Проверить лимиты API (TSK-014).
- Использовать `internal/roadmap.md` для приоритетов.
- Пинг @kpblcaoo для онбординга (TSK-019).
