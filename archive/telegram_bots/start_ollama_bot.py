#!/usr/bin/env python3
"""
Quick launcher for Ollama Chat Bot
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Проверяет зависимости"""
    print("🔍 Checking dependencies...")
    
    # Проверяем Python пакеты
    required_packages = ["httpx", "asyncio"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - install with: pip install {package}")
            return False
    
    return True

def check_services():
    """Проверяет доступность сервисов"""
    print("\n🔍 Checking services...")
    
    # Проверяем Ollama
    try:
        import httpx
        import asyncio
        
        async def check_ollama():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get("http://localhost:11434/api/tags")
                    if response.status_code == 200:
                        models = response.json().get("models", [])
                        print(f"✅ Ollama (found {len(models)} models)")
                        for model in models[:3]:  # Show first 3
                            print(f"   📦 {model['name']}")
                        return True
                    else:
                        print("❌ Ollama - server responded with error")
                        return False
            except Exception as e:
                print(f"❌ Ollama - not running: {e}")
                return False
        
        ollama_ok = asyncio.run(check_ollama())
    except Exception as e:
        print(f"❌ Ollama - check failed: {e}")
        ollama_ok = False
    
    # Проверяем API ключи
    grok_key = os.getenv("GROK_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    print(f"{'✅' if grok_key else '⚠️'} Grok API key {'set' if grok_key else 'not set'}")
    print(f"{'✅' if anthropic_key else '⚠️'} Anthropic API key {'set' if anthropic_key else 'not set'}")
    
    return ollama_ok

def main():
    """Главная функция"""
    print("🚀 LLMStruct Ollama Chat Bot Launcher")
    print("=" * 50)
    
    # Проверяем токен бота
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not set!")
        print("🔧 Set it with: export TELEGRAM_BOT_TOKEN='your_token'")
        print("📱 Get token from @BotFather on Telegram")
        return 1
    
    print(f"✅ Telegram bot token: ...{bot_token[-10:]}")
    
    # Проверяем зависимости
    if not check_dependencies():
        print("\n❌ Dependencies missing. Install with:")
        print("pip install httpx")
        return 1
    
    # Проверяем сервисы
    services_ok = check_services()
    
    if not services_ok:
        print("\n⚠️ Ollama not available, will use fallback models only")
        print("💡 To install Ollama: https://ollama.ai/")
        print("💡 To start Ollama: ollama serve")
    
    # Создаем необходимые директории
    print("\n📁 Creating directories...")
    Path("logs").mkdir(exist_ok=True)
    Path("data/ollama_chat").mkdir(parents=True, exist_ok=True)
    print("✅ Directories ready")
    
    # Запускаем бота
    print("\n🚀 Starting Ollama Chat Bot...")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Используем subprocess для запуска бота
        result = subprocess.run([
            sys.executable, "ollama_chat_bot.py"
        ], cwd=Path.cwd())
        return result.returncode
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 