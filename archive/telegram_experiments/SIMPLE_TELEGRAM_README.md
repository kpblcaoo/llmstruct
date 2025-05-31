# 🤖 Simple Telegram Bot для Cursor ↔ Telegram

## ✅ БАЗОВОЕ РЕШЕНИЕ ГОТОВО К ИСПОЛЬЗОВАНИЮ

Простое, надежное решение для двусторонней связи между Cursor AI и Telegram без сложностей.

---

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Подготовка

```bash
# Убедитесь что у вас есть токен бота
export TELEGRAM_BOT_TOKEN="your_bot_token_here"

# Установите зависимости (если нужно)
pip install requests
```

### 2. Запуск бота

```bash
# Простой запуск
python simple_telegram_bot.py

# Или через менеджер
python start_simple_telegram.py start
```

### 3. Использование из Cursor

```bash
# Отправить сообщение в Telegram
python cursor_simple_integration.py send "Привет из Cursor!"

# Проверить статус
python cursor_simple_integration.py status

# Показать последние сообщения
python cursor_simple_integration.py messages

# Мониторинг новых сообщений
python cursor_simple_integration.py monitor
```

---

## 📋 ЧТО РАБОТАЕТ

### ✅ Telegram Bot
- **Получение сообщений** от пользователя
- **Отправка ответов** в Telegram  
- **Базовые команды**: /start, /status, /help
- **Надежная работа** без asyncio конфликтов
- **Automatic restart** при ошибках

### ✅ Cursor Integration
- **Простые Python функции** для отправки сообщений
- **Мониторинг** новых сообщений пользователя
- **Файловый обмен** через JSON (надежно!)
- **Status checking** в реальном времени

### ✅ Двусторонняя связь
```
👤 Пользователь в Telegram → 📱 Bot → 📁 JSON файлы → 🎯 Cursor AI
🎯 Cursor AI → 📁 JSON файлы → 📱 Bot → 👤 Пользователь в Telegram
```

---

## 🔧 СТРУКТУРА ФАЙЛОВ

```
simple_telegram_bot.py         # Основной бот
cursor_simple_integration.py   # Функции для Cursor
start_simple_telegram.py       # Менеджер запуска
data/telegram/                 # Данные для обмена
├── user_messages.json         # Сообщения пользователя
├── cursor_commands.json       # Команды от Cursor
└── bot_responses.json         # Ответы бота
```

---

## 📖 ИСПОЛЬЗОВАНИЕ

### В Cursor/Python коде:

```python
from cursor_simple_integration import *

# Отправить сообщение
send_to_telegram("👋 Привет из Cursor!")

# Быстрые функции
quick_reply("Готово!")
quick_status()
quick_notification("Важное уведомление")

# Получить сообщения
messages = get_user_messages(limit=5)
last_msg = get_last_message()

# Проверить статус
status = show_conversation_status()
```

### В Telegram:

```
/start   - Запуск бота
/status  - Статус системы  
/help    - Справка

# Просто пишите сообщения - они передаются в Cursor!
```

---

## 🧪 ТЕСТИРОВАНИЕ

### Проверка системы:
```bash
python start_simple_telegram.py test
```

### Полный тест:
1. Запустите бот: `python simple_telegram_bot.py`
2. Отправьте сообщение из Cursor: `python cursor_simple_integration.py send "Тест"`
3. Напишите сообщение в Telegram боту
4. Проверьте статус: `python cursor_simple_integration.py status`

---

## ⚙️ НАСТРОЙКИ

### Переменные окружения:
```bash
export TELEGRAM_BOT_TOKEN="your_token"           # Обязательно!
export TELEGRAM_CHAT_ID="-1234567890"           # Опционально (авто-определение)
```

### Файлы конфигурации:
- `data/telegram/` - автоматически создается
- `simple_bot.log` - логи бота
- JSON файлы для обмена данными

---

## 🔍 МОНИТОРИНГ

### Логи:
```bash
tail -f simple_bot.log
```

### Статус в реальном времени:
```bash
watch -n 2 "python cursor_simple_integration.py status | jq ."
```

### Мониторинг сообщений:
```bash
python cursor_simple_integration.py monitor
```

---

## 🚨 TROUBLESHOOTING

### Проблема: Bot не отвечает
```bash
# Проверьте токен
echo $TELEGRAM_BOT_TOKEN

# Проверьте процесс
ps aux | grep simple_telegram_bot.py

# Проверьте логи
tail simple_bot.log
```

### Проблема: Сообщения не передаются
```bash
# Проверьте файлы данных
ls -la data/telegram/
python cursor_simple_integration.py status
```

### Проблема: Multiple bot instances
```bash
# Остановите все экземпляры
pkill -f "python.*bot"
```

---

## 📈 ПРЕИМУЩЕСТВА БАЗОВОГО РЕШЕНИЯ

### ✅ Простота
- **Без async сложностей** - обычный Python код
- **Минимум зависимостей** - только `requests`
- **Понятная архитектура** - файловый обмен

### ✅ Надежность  
- **Без event loop конфликтов**
- **Автоматический retry** для HTTP запросов
- **Graceful error handling**

### ✅ Готовность
- **Работает из коробки** - запустил и пользуйся
- **Протестировано** на реальных данных
- **Документировано** для быстрого старта

---

## 🛣️ ДАЛЬНЕЙШЕЕ РАЗВИТИЕ

Базовое решение готово к использованию **прямо сейчас**!

Для перехода к продакшн-версии см. **`PRODUCTION_ROADMAP.md`**

### Следующие возможные улучшения:
- Database storage вместо JSON файлов
- Web dashboard для мониторинга  
- Advanced LLM integration
- Multi-user support
- Enterprise features

---

## 💡 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### Scenario 1: Уведомления о прогрессе
```python
# В Cursor во время длительной задачи
quick_notification("Начинаю анализ кода...")
# ... код выполнения ...
quick_notification("Анализ завершен! Найдено 15 улучшений")
```

### Scenario 2: Вопрос-ответ
```python
# Получить последнее сообщение пользователя
msg = get_last_message()
if msg and "статус" in msg['text'].lower():
    quick_reply("✅ Система работает нормально")
```

### Scenario 3: Мониторинг задач
```python
# Запускать в background для отслеживания
def handle_new_message(msg):
    text = msg.get('text', '').lower()
    if 'помощь' in text:
        quick_reply("Чем могу помочь?")

start_conversation_monitor(handle_new_message)
```

---

## 📞 ПОДДЕРЖКА

**Система работает и готова к использованию!** 🎉

При возникновении вопросов:
1. Проверьте логи: `simple_bot.log`
2. Запустите тест: `python start_simple_telegram.py test`
3. Проверьте статус: `python cursor_simple_integration.py status`

**Happy coding with Telegram integration!** 🚀 