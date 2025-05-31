# cli.py
# Copyright (C) 2025 Mikhail Stepanov
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""LLMStruct CLI - Main entry point for the command-line interface."""

import argparse
import asyncio
import json
import logging
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import List, Optional

import toml
from llmstruct import LLMClient
from llmstruct.cache import JSONCache
from llmstruct.generators.json_generator import generate_json, get_folder_structure
from llmstruct.self_run import attach_to_llm_request

# Import modular CLI components
try:
    from .cli_main_commands import (
        parse, query, interactive, context, dogfood, review, 
        copilot, audit, analyze_duplicates
    )
    from .cli_argument_parser import create_full_argument_parser
    MODULAR_CLI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Modular CLI components not available: {e}")
    MODULAR_CLI_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_gitignore(root_dir: str) -> List[str]:
    """Load and normalize patterns from .gitignore."""
    gitignore_path = Path(root_dir) / ".gitignore"
    patterns = []
    if gitignore_path.exists():
        try:
            with gitignore_path.open("r", encoding="utf-8") as f:
                patterns = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
        except Exception as e:
            logging.error(f"Failed to read .gitignore: {e}")
    return patterns


def load_config(root_dir: str) -> dict:
    """Load settings from llmstruct.toml or return empty dict."""
    config_path = Path(root_dir) / "llmstruct.toml"
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as f:
                return toml.load(f)
        except Exception as e:
            logging.error(f"Failed to read llmstruct.toml: {e}")
    return {}


def read_file_content(file_path: str) -> Optional[str]:
    """Read content of a file if it exists and is a text file."""
    path = Path(file_path)
    if path.is_file():
        try:
            with path.open("r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logging.error(f"Failed to read file {file_path}: {e}")
    return None


def write_to_file(content: str, filename: str, base_dir: str = "./tmp") -> str:
    """Write content to a file in base_dir (default ./tmp) and return the path."""
    # Ensure base_dir exists
    base_path = Path(base_dir)
    base_path.mkdir(exist_ok=True, parents=True)
    # Sanitize filename: allow only safe filenames
    safe_filename = re.sub(r"[^\w\-.]", "_", filename)
    if not safe_filename or safe_filename in {"file", "a", "to", "the", "output"}:
        logging.error(f"Refusing to write to suspicious filename: {filename}")
        return ""
    file_path = base_path / safe_filename
    if file_path.exists():
        logging.warning(f"File {file_path} already exists, overwriting")
    try:
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"Wrote content to {file_path}")
        return str(file_path)
    except Exception as e:
        logging.error(f"Failed to write to {file_path}: {e}")
        return ""


def parse_files_from_response(response: str) -> List[tuple[str, str]]:
    """Extract filenames and content from LLM response (e.g., ```filename\ncontent```)."""
    files = []
    pattern = r"```(\S+?)\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    for filename, content in matches:
        files.append((filename.strip(), content.strip()))
    return files


# ===== API/Bot Management and Metrics Functions =====

def add_api_bot_commands(subparsers):
    """Добавить команды для управления API и Bot сервисами"""
    
    # API Management команды
    api_parser = subparsers.add_parser('api', help='API server management')
    api_subparsers = api_parser.add_subparsers(dest='api_action', help='API actions')
    
    # API start
    api_start = api_subparsers.add_parser('start', help='Start API server')
    api_start.add_argument('--port', type=int, default=8000, help='Port number')
    api_start.add_argument('--host', default='0.0.0.0', help='Host address') 
    api_start.add_argument('--background', action='store_true', help='Run in background')
    
    # API status
    api_status = api_subparsers.add_parser('status', help='Check API server status')
    
    # API stop
    api_stop = api_subparsers.add_parser('stop', help='Stop API server')
    
    # Bot Management команды  
    bot_parser = subparsers.add_parser('bot', help='Telegram bot management')
    bot_subparsers = bot_parser.add_subparsers(dest='bot_action', help='Bot actions')
    
    # Bot start
    bot_start = bot_subparsers.add_parser('start', help='Start Telegram bot')
    bot_start.add_argument('--token', help='Telegram bot token (or use TELEGRAM_BOT_TOKEN env)')
    bot_start.add_argument('--type', choices=['mp002', 'test', 'main'], default='mp002', help='Bot type')
    bot_start.add_argument('--background', action='store_true', help='Run in background')
    
    # Bot status  
    bot_status = bot_subparsers.add_parser('status', help='Check bot status')
    
    # Bot stop
    bot_stop = bot_subparsers.add_parser('stop', help='Stop Telegram bot')
    
    # Services - управление всеми сервисами
    services_parser = subparsers.add_parser('services', help='Manage all services (API + Bots)')
    services_subparsers = services_parser.add_subparsers(dest='services_action', help='Services actions')
    
    # Services start
    services_start = services_subparsers.add_parser('start', help='Start all services')
    
    # Services status
    services_status = services_subparsers.add_parser('status', help='Check all services status')
    
    # Services stop
    services_stop = services_subparsers.add_parser('stop', help='Stop all services')

    # Metrics Management команды
    metrics_parser = subparsers.add_parser('metrics', help='Project metrics and analytics')
    metrics_subparsers = metrics_parser.add_subparsers(dest='metrics_action', help='Metrics actions')
    
    # Metrics status
    metrics_status = metrics_subparsers.add_parser('status', help='Show current session metrics')
    
    # Metrics summary
    metrics_summary = metrics_subparsers.add_parser('summary', help='Show session summary') 
    
    # Metrics analytics
    metrics_analytics = metrics_subparsers.add_parser('analytics', help='Generate analytics data for graphs')
    metrics_analytics.add_argument('--output', help='Output file for analytics data')
    metrics_analytics.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
    
    # Metrics tokens
    metrics_tokens = metrics_subparsers.add_parser('tokens', help='Show detailed token usage statistics')
    
    # Metrics report
    metrics_report = metrics_subparsers.add_parser('report', help='Generate comprehensive metrics report')
    metrics_report.add_argument('--sessions', type=int, default=10, help='Number of recent sessions to include')
    metrics_report.add_argument('--output', help='Output file for report')
    
    # Metrics track (manual event tracking)
    metrics_track = metrics_subparsers.add_parser('track', help='Manually track workflow event')
    metrics_track.add_argument('event_type', help='Type of event to track')
    metrics_track.add_argument('--details', help='Additional details about the event')


async def cmd_api_management(args):
    """Управление API сервером"""
    import subprocess
    import signal
    import psutil
    import requests
    from pathlib import Path
    
    if args.api_action == 'start':
        # Проверяем что venv активирован
        venv_path = Path('venv/bin/activate')
        if not venv_path.exists():
            print("❌ Virtual environment not found. Run: python -m venv venv")
            return
            
        print(f"🚀 Starting API server on {args.host}:{args.port}")
        
        # Проверяем что порт свободен
        try:
            response = requests.get(f"http://{args.host}:{args.port}/api/v1/system/health", timeout=1)
            print(f"⚠️ Port {args.port} already in use. Use 'llmstruct api stop' first")
            return
        except:
            pass  # Порт свободен
            
        # Запускаем API
        cmd = f"source venv/bin/activate && python test_api.py"
        if args.background:
            cmd += " &"
            
        process = subprocess.Popen(cmd, shell=True, cwd='.')
        
        if args.background:
            print(f"✅ API server started in background (PID: {process.pid})")
            # Сохраняем PID для последующего управления
            with open('.api_pid', 'w') as f:
                f.write(str(process.pid))
        else:
            print("✅ API server started. Press Ctrl+C to stop")
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping API server...")
                process.terminate()
                
    elif args.api_action == 'status':
        try:
            response = requests.get(f"http://localhost:8000/api/v1/system/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print("✅ API Server Status: RUNNING")
                print(f"🔍 Health: {data.get('status', 'unknown')}")
                print(f"📄 Docs: http://localhost:8000/docs")
            else:
                print(f"⚠️ API Server responding with status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ API Server Status: STOPPED")
        except Exception as e:
            print(f"❌ Error checking API status: {e}")
            
    elif args.api_action == 'stop':
        # Попытка graceful shutdown через API
        try:
            response = requests.post("http://localhost:8000/api/v1/system/shutdown", timeout=2)
            print("✅ API server shutdown requested")
        except:
            pass
            
        # Принудительное завершение через PID файл
        pid_file = Path('.api_pid')
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                process = psutil.Process(pid)
                process.terminate()
                print(f"🛑 API server stopped (PID: {pid})")
                pid_file.unlink()
            except (ValueError, psutil.NoSuchProcess, FileNotFoundError):
                print("⚠️ PID file found but process not running")
                pid_file.unlink()
        else:
            print("⚠️ No PID file found. API may not be running or was started manually")


async def cmd_bot_management(args):
    """Управление Telegram ботами"""
    import subprocess
    import os
    from pathlib import Path
    
    if args.bot_action == 'start':
        # Проверяем токен
        token = args.token or os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            print("❌ Telegram bot token required!")
            print("Set with: export TELEGRAM_BOT_TOKEN='your_token'")
            print("Or use: --token 'your_token'")
            return
            
        # Определяем какой бот запускать
        bot_scripts = {
            'mp002': 'integrations/telegram_bot/mp002_progress_bot.py',
            'test': 'integrations/telegram_bot/test_bot.py',
            'main': 'integrations/telegram_bot/test_bot.py'  # fallback
        }
        
        bot_script = bot_scripts.get(args.type, bot_scripts['mp002'])
        if not Path(bot_script).exists():
            print(f"❌ Bot script not found: {bot_script}")
            return
            
        print(f"🤖 Starting {args.type} Telegram bot...")
        
        # Экспортируем токен и запускаем бота
        env = os.environ.copy()
        env['TELEGRAM_BOT_TOKEN'] = token
        
        cmd = f"source venv/bin/activate && python {bot_script}"
        if args.background:
            cmd += " &"
            
        process = subprocess.Popen(cmd, shell=True, cwd='.', env=env)
        
        if args.background:
            print(f"✅ {args.type} bot started in background (PID: {process.pid})")
            # Сохраняем PID
            with open(f'.bot_{args.type}_pid', 'w') as f:
                f.write(str(process.pid))
        else:
            print("✅ Bot started. Press Ctrl+C to stop")
            try:
                process.wait()
            except KeyboardInterrupt:
                print(f"\n🛑 Stopping {args.type} bot...")
                process.terminate()
                
    elif args.bot_action == 'status':
        # Проверяем PID файлы активных ботов
        bot_types = ['mp002', 'test', 'main']
        active_bots = []
        
        for bot_type in bot_types:
            pid_file = Path(f'.bot_{bot_type}_pid')
            if pid_file.exists():
                try:
                    with open(pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    import psutil
                    process = psutil.Process(pid)
                    if process.is_running():
                        active_bots.append((bot_type, pid))
                    else:
                        pid_file.unlink()  # Удаляем устаревший PID
                except (ValueError, psutil.NoSuchProcess, FileNotFoundError):
                    pid_file.unlink()
                    
        if active_bots:
            print("✅ Active Telegram Bots:")
            for bot_type, pid in active_bots:
                print(f"   🤖 {bot_type} bot (PID: {pid})")
        else:
            print("❌ No active Telegram bots found")
            
    elif args.bot_action == 'stop':
        # Останавливаем все активные боты
        import psutil
        bot_types = ['mp002', 'test', 'main']
        stopped_count = 0
        
        for bot_type in bot_types:
            pid_file = Path(f'.bot_{bot_type}_pid')
            if pid_file.exists():
                try:
                    with open(pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    process = psutil.Process(pid)
                    process.terminate()
                    print(f"🛑 Stopped {bot_type} bot (PID: {pid})")
                    pid_file.unlink()
                    stopped_count += 1
                except (ValueError, psutil.NoSuchProcess, FileNotFoundError):
                    pid_file.unlink()
                    
        if stopped_count == 0:
            print("⚠️ No active bots to stop")
        else:
            print(f"✅ Stopped {stopped_count} bot(s)")


async def cmd_services(args):
    """Управление всеми сервисами (API + Bots)"""
    if args.command == 'api':
        await cmd_api_management(args)
    elif args.command == 'bot':
        await cmd_bot_management(args)  
    elif args.command == 'services':
        if args.services_action == 'start':
            print("🚀 Starting all services...")
            
            # Запускаем API
            api_args = type('Args', (), {
                'api_action': 'start', 
                'port': 8000, 
                'host': '0.0.0.0', 
                'background': True
            })()
            await cmd_api_management(api_args)
            
            # Ждем запуска API
            import time
            time.sleep(2)
            
            # Запускаем MP002 бота
            bot_args = type('Args', (), {
                'bot_action': 'start',
                'token': None,
                'type': 'mp002', 
                'background': True
            })()
            await cmd_bot_management(bot_args)
            
            print("✅ All services started successfully!")
            print("📄 API Docs: http://localhost:8000/docs")
            print("🤖 Use Telegram bot for MP-002 progress control")
            
        elif args.services_action == 'stop':
            print("🛑 Stopping all services...")
            
            # Останавливаем боты
            bot_args = type('Args', (), {'bot_action': 'stop'})()
            await cmd_bot_management(bot_args)
            
            # Останавливаем API
            api_args = type('Args', (), {'api_action': 'stop'})()
            await cmd_api_management(api_args)
            
            print("✅ All services stopped")
            
        elif args.services_action == 'status':
            print("📊 Services Status Report:")
            print("=" * 30)
            
            # Статус API
            api_args = type('Args', (), {'api_action': 'status'})()
            await cmd_api_management(api_args)
            
            print()
            
            # Статус ботов
            bot_args = type('Args', (), {'bot_action': 'status'})()
            await cmd_bot_management(bot_args)


async def cmd_metrics(args):
    """Управление метриками проекта"""
    try:
        if args.metrics_action == 'status':
            metrics_status()
        elif args.metrics_action == 'summary':
            metrics_summary()
        elif args.metrics_action == 'analytics':
            metrics_analytics(args.output, args.format)
        elif args.metrics_action == 'tokens':
            metrics_tokens()
        elif args.metrics_action == 'report':
            metrics_report(args.sessions, args.output)
        elif args.metrics_action == 'track':
            metrics_track(args.event_type, args.details)
        else:
            print("❌ Unknown metrics action")
            
    except Exception as e:
        print(f"❌ Metrics command failed: {e}")


def metrics_status():
    """Показать текущий статус метрик"""
    try:
        from .metrics_tracker import get_metrics_tracker
        
        tracker = get_metrics_tracker()
        summary = tracker.get_session_summary()
        
        print("📊 CURRENT SESSION METRICS")
        print("=" * 40)
        print(f"Session ID: {summary['session_id']}")
        print(f"Duration: {summary['duration']:.0f}s ({summary['duration']/60:.1f}m)")
        print(f"Efficiency Score: {summary['efficiency_score']:.2f}")
        print(f"Total Tokens: {summary['total_tokens']:,}")
        print(f"Estimated Cost: ${summary['estimated_cost']:.4f}")
        print(f"Tasks: {summary['tasks_completed']}/{summary['tasks_total']}")
        print(f"False Paths: {summary['false_paths']}")
        print(f"Rollbacks: {summary['rollbacks']}")
        print(f"Retries: {summary['retries']}")
        print(f"Avoidable Errors: {summary['avoidable_errors']}")
        
    except Exception as e:
        print(f"❌ Error getting metrics status: {e}")


def metrics_summary():
    """Показать детальную сводку метрик"""
    try:
        from .metrics_tracker import get_metrics_tracker
        
        tracker = get_metrics_tracker()
        summary = tracker.get_session_summary()
        metadata = tracker.session_data['metadata']
        workflow = tracker.session_data['workflow_metrics']
        
        print("📊 DETAILED SESSION SUMMARY")
        print("=" * 50)
        print(f"Session: {summary['session_id']}")
        print(f"Branch: {metadata['branch']}")
        print(f"Commit: {metadata['commit_hash']}")
        print(f"Struct.json Hash: {metadata['struct_json_hash']}")
        print()
        
        print("🎯 PERFORMANCE:")
        print(f"  Efficiency Score: {summary['efficiency_score']:.2f}/1.0")
        if summary['efficiency_score'] < 0.7:
            print("  ⚠️ Low efficiency detected!")
        
        print(f"  Duration: {summary['duration']:.0f}s")
        print(f"  Tasks per minute: {summary['tasks_total'] / max(summary['duration']/60, 1):.1f}")
        print()
        
        print("💰 RESOURCE USAGE:")
        print(f"  Total Tokens: {summary['total_tokens']:,}")
        print(f"  Average per task: {summary['total_tokens'] / max(summary['tasks_total'], 1):.0f}")
        print(f"  Estimated Cost: ${summary['estimated_cost']:.4f}")
        print()
        
        print("🔄 WORKFLOW EVENTS:")
        print(f"  Struct.json usage: {workflow['struct_json_usage']}")
        print(f"  Context switches: {workflow['context_switches']}")
        print(f"  CLI commands: {workflow['cli_commands_executed']}")
        print(f"  File operations: {workflow['file_operations']}")
        print()
        
        if summary['false_paths'] > 0 or summary['rollbacks'] > 0:
            print("⚠️ INEFFICIENCIES DETECTED:")
            if summary['false_paths'] > 0:
                print(f"  False paths: {summary['false_paths']}")
            if summary['rollbacks'] > 0:
                print(f"  Rollbacks: {summary['rollbacks']}")
            if summary['avoidable_errors'] > 0:
                print(f"  Avoidable errors: {summary['avoidable_errors']}")
            print("  💡 Consider reviewing workflow patterns")
            print()
            
    except Exception as e:
        print(f"❌ Error getting metrics summary: {e}")


def metrics_analytics(output_file=None, format='json'):
    """Сгенерировать аналитические данные"""
    try:
        from .metrics_tracker import get_metrics_tracker
        import json
        import time
        
        tracker = get_metrics_tracker()
        analytics = tracker.get_analytics_data()
        
        if 'error' in analytics:
            print(f"❌ {analytics['error']}")
            return
        
        output_data = {
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "analytics": analytics,
            "current_session": tracker.get_session_summary()
        }
        
        if output_file:
            if format == 'csv':
                # Конвертация в CSV для графиков
                import csv
                with open(output_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Token usage over time
                    writer.writerow(["session", "tokens", "efficiency", "cost", "completion_rate"])
                    for i, session in enumerate(analytics['token_usage_over_time']):
                        efficiency = analytics['efficiency_trends'][i]['efficiency']
                        cost = analytics['cost_analysis'][i]['cost']
                        completion = analytics['task_completion_rates'][i]['completion_rate']
                        writer.writerow([session['session'], session['tokens'], efficiency, cost, completion])
                    
                    print(f"📈 Analytics data exported to {output_file} (CSV)")
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                print(f"📈 Analytics data exported to {output_file} (JSON)")
        else:
            print("📈 ANALYTICS DATA PREVIEW:")
            print(json.dumps(analytics, indent=2)[:1000] + "...")
            
    except Exception as e:
        print(f"❌ Error generating analytics: {e}")


def metrics_report(sessions=10, output_file=None):
    """Создать всесторонний отчет"""
    try:
        from .metrics_tracker import get_metrics_tracker
        import time
        
        tracker = get_metrics_tracker()
        analytics = tracker.get_analytics_data()
        
        if 'error' in analytics:
            print(f"❌ {analytics['error']}")
            return
        
        recent_sessions = analytics.get('token_usage_over_time', [])[-sessions:]
        
        report = f"""📊 LLMSTRUCT PROJECT METRICS REPORT
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}
Report Period: Last {len(recent_sessions)} sessions

🎯 SUMMARY:
- Total Sessions Analyzed: {len(recent_sessions)}
- Average Tokens per Session: {sum(s['tokens'] for s in recent_sessions) / len(recent_sessions) if recent_sessions else 0:.0f}
- Total Token Usage: {sum(s['tokens'] for s in recent_sessions):,}

📈 TRENDS:
- Efficiency Trend: {"📈 Improving" if len(analytics['efficiency_trends']) > 1 and analytics['efficiency_trends'][-1]['efficiency'] > analytics['efficiency_trends'][0]['efficiency'] else "📉 Declining"}
- Token Usage Trend: {"📈 Increasing" if len(recent_sessions) > 1 and recent_sessions[-1]['tokens'] > recent_sessions[0]['tokens'] else "📉 Decreasing"}

🎯 RECOMMENDATIONS:
"""
        
        # Анализ паттернов и рекомендации
        if recent_sessions:
            avg_efficiency = sum(s['efficiency'] for s in analytics['efficiency_trends'][-sessions:]) / min(sessions, len(analytics['efficiency_trends']))
            if avg_efficiency < 0.7:
                report += "- ⚠️ Low efficiency detected. Review workflow patterns.\n"
            if sum(s['tokens'] for s in recent_sessions) > 100000:
                report += "- 💰 High token usage. Consider context optimization.\n"
            
            error_sessions = [s for s in analytics['error_patterns'][-sessions:] if s['false_paths'] > 0 or s['rollbacks'] > 0]
            if error_sessions:
                report += f"- 🔧 {len(error_sessions)} sessions with inefficiencies. Review error patterns.\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📋 Report saved to {output_file}")
        else:
            print(report)
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")


def metrics_track(event_type, details=None):
    """Ручное отслеживание событий"""
    try:
        from .metrics_tracker import track_workflow_event
        
        track_workflow_event(event_type, details)
        print(f"📊 Tracked event: {event_type}")
        if details:
            print(f"    Details: {details}")
            
    except Exception as e:
        print(f"❌ Error tracking event: {e}")


def metrics_tokens():
    """Показать детальную статистику токенов"""
    try:
        from .metrics_tracker import get_token_summary, get_metrics_tracker
        
        print("📊 **Token Usage Summary**")
        print("=" * 50)
        
        summary = get_token_summary()
        if not summary:
            print("❌ No token data available")
            return
            
        print(f"📱 **Telegram Interactions:**")
        print(f"   • Total tokens: {summary.get('telegram_tokens', 0):,}")
        print(f"   • Interactions: {summary.get('telegram_interactions_count', 0)}")
        
        print(f"\n🔌 **API Interactions:**")
        print(f"   • Total tokens: {summary.get('api_tokens', 0):,}")
        print(f"   • Interactions: {summary.get('api_interactions_count', 0)}")
        
        print(f"\n💰 **Overall:**")
        print(f"   • Total tokens: {summary.get('total_tokens', 0):,}")
        print(f"   • Estimated cost: ${summary.get('estimated_cost_usd', 0):.6f}")
        
        # Детальная информация
        tracker = get_metrics_tracker()
        
        telegram_interactions = tracker.session_data.get('telegram_interactions', [])
        if telegram_interactions:
            print(f"\n📱 **Recent Telegram Interactions:**")
            for i, interaction in enumerate(telegram_interactions[-5:], 1):  # Последние 5
                print(f"   {i}. {interaction.get('total_tokens_estimate', 0)} tokens "
                      f"(user: {interaction.get('user_tokens_estimate', 0)}, "
                      f"bot: {interaction.get('bot_tokens_estimate', 0)}, "
                      f"context: {interaction.get('context_tokens', 0)})")
        
        api_interactions = tracker.session_data.get('api_interactions', [])
        if api_interactions:
            print(f"\n🔌 **Recent API Interactions:**")
            for i, interaction in enumerate(api_interactions[-5:], 1):  # Последние 5
                print(f"   {i}. {interaction.get('endpoint', 'unknown')} - "
                      f"{interaction.get('total_tokens', 0)} tokens "
                      f"(req: {interaction.get('request_tokens', 0)}, "
                      f"resp: {interaction.get('response_tokens', 0)}, "
                      f"ctx: {interaction.get('context_tokens', 0)})")
                      
    except Exception as e:
        print(f"❌ Error getting token summary: {e}")


def main():
    """Command-line interface for LLMstruct."""
    # Use modular argument parser if available, otherwise fallback to basic parser
    if MODULAR_CLI_AVAILABLE:
        parser = create_full_argument_parser()
    else:
        # Fallback basic parser
        parser = argparse.ArgumentParser(
            description="Generate structured JSON for codebases and query LLMs"
        )
        subparsers = parser.add_subparsers(
            dest="command", required=True, help="Available commands"
        )

        parse_parser = subparsers.add_parser(
            "parse", help="Parse codebase and generate struct.json"
        )
        parse_parser.add_argument("root_dir", help="Root directory of the project")
        parse_parser.add_argument(
            "-o", "--output", default="struct.json", help="Output JSON file"
        )
        parse_parser.add_argument("--goals", nargs="*", help="Custom project goals")
        parse_parser.add_argument(
            "--use-cache", action="store_true", help="Cache generated JSON"
        )

        query_parser = subparsers.add_parser(
            "query", help="Query LLMs with prompt and context"
        )
        query_parser.add_argument("--prompt", required=True, help="Prompt for LLM")
        query_parser.add_argument(
            "--context", default="struct.json", help="Context JSON file"
        )
        # Add API and Bot management commands if available
        if not MODULAR_CLI_AVAILABLE:
            try:
                add_api_bot_commands(subparsers)
            except NameError:
                # API/Bot commands not available in legacy mode
                pass

    args = parser.parse_args()

    # Execute commands using modular handlers
    if args.command == "parse":
        parse(args)
    elif args.command == "query":
        asyncio.run(query(args))
    elif args.command == "interactive":
        asyncio.run(interactive(args))
    elif args.command == "context":
        context(args)
    elif args.command == "dogfood":
        dogfood(args)
    elif args.command == "review":
        review(args)
    elif args.command == "copilot":
        copilot(args)
    elif args.command == "audit":
        audit(args)
    elif args.command == "analyze-duplicates":
        analyze_duplicates(args)
    elif args.command in ["api", "bot", "services"]:
        try:
            asyncio.run(cmd_services(args))
        except NameError:
            print(f"Command '{args.command}' not available in current configuration")
    elif args.command == "metrics":
        try:
            asyncio.run(cmd_metrics(args))
        except NameError:
            print("Metrics command not available in current configuration")
    else:
        print(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
