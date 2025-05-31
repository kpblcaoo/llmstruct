#!/usr/bin/env python3
"""
Лаунчер для Ollama API Bot с проверками зависимостей и API
"""

import os
import sys
import asyncio
import aiohttp
import subprocess
from pathlib import Path

def check_environment():
    """Проверка переменных окружения"""
    print("🔍 Проверка окружения...")
    
    # Проверка токена
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не установлен!")
        print("   Установите: export TELEGRAM_BOT_TOKEN='ваш_токен'")
        return False
    
    print(f"✅ Telegram токен найден: {token[:10]}...")
    
    # Проверка API URL
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    print(f"📡 API URL: {api_url}")
    
    return True

async def check_api_server(api_url="http://localhost:8000"):
    """Проверка доступности FastAPI сервера"""
    print(f"🔗 Проверка API сервера: {api_url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{api_url}/api/v1/system/health", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API сервер работает: {data['status']}")
                    print(f"   Версия: {data['api_version']}")
                    print(f"   Метрики: {'включены' if data['metrics_enabled'] else 'отключены'}")
                    return True
                else:
                    print(f"❌ API сервер ошибка: {response.status}")
                    return False
    except asyncio.TimeoutError:
        print("❌ API сервер не отвечает (timeout)")
        return False
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {e}")
        return False

async def check_ollama():
    """Проверка доступности Ollama"""
    print("🦙 Проверка Ollama...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model['name'] for model in data.get('models', [])]
                    print(f"✅ Ollama работает, моделей: {len(models)}")
                    if models:
                        print(f"   Доступные модели: {', '.join(models[:3])}")
                        if len(models) > 3:
                            print(f"   ... и ещё {len(models)-3}")
                    return True
                else:
                    print(f"❌ Ollama ошибка: {response.status}")
                    return False
    except Exception as e:
        print(f"⚠️ Ollama недоступна: {e}")
        print("   Бот будет работать только через FastAPI fallback")
        return False

def check_dependencies():
    """Проверка Python зависимостей"""
    print("📦 Проверка зависимостей...")
    
    required = ['aiohttp', 'asyncio']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✅ {pkg}")
        except ImportError:
            missing.append(pkg)
            print(f"❌ {pkg}")
    
    if missing:
        print(f"❌ Отсутствующие зависимости: {', '.join(missing)}")
        print("   Установите: pip install aiohttp")
        return False
    
    return True

def start_api_server():
    """Попытка запуска API сервера"""
    print("🚀 Попытка запуска API сервера...")
    
    try:
        # Проверяем есть ли файл
        if not Path("test_api_simple.py").exists():
            print("❌ Файл test_api_simple.py не найден")
            return False
        
        # Запускаем в фоне
        process = subprocess.Popen([
            sys.executable, "test_api_simple.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ API сервер запущен (PID: {process.pid})")
        print("   Ждём 3 секунды для инициализации...")
        import time
        time.sleep(3)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка запуска API сервера: {e}")
        return False

async def main():
    """Главная функция"""
    print("🤖 Ollama API Bot Launcher")
    print("=" * 50)
    
    # 1. Проверка окружения
    if not check_environment():
        return 1
    
    # 2. Проверка зависимостей
    if not check_dependencies():
        return 1
    
    # 3. Проверка API
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    api_ok = await check_api_server(api_url)
    
    if not api_ok:
        print("\n💡 Пытаемся запустить API сервер...")
        if start_api_server():
            # Повторная проверка
            await asyncio.sleep(2)
            api_ok = await check_api_server(api_url)
        
        if not api_ok:
            print("\n❌ API сервер недоступен!")
            print("   Запустите вручную: python test_api_simple.py")
            return 1
    
    # 4. Проверка Ollama (опционально)
    await check_ollama()
    
    # 5. Создание директорий
    print("\n📁 Создание директорий...")
    Path("logs").mkdir(exist_ok=True)
    Path("data/ollama_api_chat").mkdir(parents=True, exist_ok=True)
    print("✅ Директории созданы")
    
    # 6. Запуск бота
    print("\n🚀 Запуск Ollama API Bot...")
    print("=" * 50)
    
    try:
        # Импорт и запуск
        from ollama_api_bot import main as bot_main
        return await bot_main()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта бота: {e}")
        print("   Проверьте наличие файла ollama_api_bot.py")
        return 1
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен пользователем")
        return 0
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        return 1

if __name__ == "__main__":
    # Проверка Python версии
    if sys.version_info < (3, 7):
        print("❌ Требуется Python 3.7 или выше")
        sys.exit(1)
    
    # Запуск
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 