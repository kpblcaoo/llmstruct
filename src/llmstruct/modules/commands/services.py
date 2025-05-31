import os
import subprocess
import signal
import psutil
import requests
import time
from pathlib import Path


def add_api_bot_commands(subparsers):
    """Добавить команды для управления API и Bot сервисами"""
    # API Management команды
    api_parser = subparsers.add_parser('api', help='API server management')
    api_subparsers = api_parser.add_subparsers(dest='api_action', help='API actions')
    api_start = api_subparsers.add_parser('start', help='Start API server')
    api_start.add_argument('--port', type=int, default=8000, help='Port number')
    api_start.add_argument('--host', default='0.0.0.0', help='Host address')
    api_start.add_argument('--background', action='store_true', help='Run in background')
    api_status = api_subparsers.add_parser('status', help='Check API server status')
    api_stop = api_subparsers.add_parser('stop', help='Stop API server')
    bot_parser = subparsers.add_parser('bot', help='Telegram bot management')
    bot_subparsers = bot_parser.add_subparsers(dest='bot_action', help='Bot actions')
    bot_start = bot_subparsers.add_parser('start', help='Start Telegram bot')
    bot_start.add_argument('--token', help='Telegram bot token (or use TELEGRAM_BOT_TOKEN env)')
    bot_start.add_argument('--type', choices=['mp002', 'test', 'main'], default='mp002', help='Bot type')
    bot_start.add_argument('--background', action='store_true', help='Run in background')
    bot_status = bot_subparsers.add_parser('status', help='Check bot status')
    bot_stop = bot_subparsers.add_parser('stop', help='Stop Telegram bot')
    services_parser = subparsers.add_parser('services', help='Manage all services (API + Bots)')
    services_subparsers = services_parser.add_subparsers(dest='services_action', help='Services actions')
    services_start = services_subparsers.add_parser('start', help='Start all services')
    services_status = services_subparsers.add_parser('status', help='Check all services status')
    services_stop = services_subparsers.add_parser('stop', help='Stop all services')
    metrics_parser = subparsers.add_parser('metrics', help='Project metrics and analytics')
    metrics_subparsers = metrics_parser.add_subparsers(dest='metrics_action', help='Metrics actions')
    metrics_status = metrics_subparsers.add_parser('status', help='Show current session metrics')
    metrics_summary = metrics_subparsers.add_parser('summary', help='Show session summary')
    metrics_analytics = metrics_subparsers.add_parser('analytics', help='Generate analytics data for graphs')
    metrics_analytics.add_argument('--output', help='Output file for analytics data')
    metrics_analytics.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
    metrics_tokens = metrics_subparsers.add_parser('tokens', help='Show detailed token usage statistics')
    metrics_report = metrics_subparsers.add_parser('report', help='Generate comprehensive metrics report')
    metrics_report.add_argument('--sessions', type=int, default=10, help='Number of recent sessions to include')
    metrics_report.add_argument('--output', help='Output file for report')
    metrics_track = metrics_subparsers.add_parser('track', help='Manually track workflow event')
    metrics_track.add_argument('event_type', help='Type of event to track')
    metrics_track.add_argument('--details', help='Additional details about the event')

async def cmd_api_management(args):
    """Управление API сервером"""
    venv_path = Path('venv/bin/activate')
    if args.api_action == 'start':
        if not venv_path.exists():
            print("❌ Virtual environment not found. Run: python -m venv venv")
            return
        print(f"🚀 Starting API server on {args.host}:{args.port}")
        try:
            response = requests.get(f"http://{args.host}:{args.port}/api/v1/system/health", timeout=1)
            print(f"⚠️ Port {args.port} already in use. Use 'llmstruct api stop' first")
            return
        except:
            pass
        cmd = f"source venv/bin/activate && python test_api.py"
        if args.background:
            cmd += " &"
        process = subprocess.Popen(cmd, shell=True, cwd='.')
        if args.background:
            print(f"✅ API server started in background (PID: {process.pid})")
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
        try:
            response = requests.post("http://localhost:8000/api/v1/system/shutdown", timeout=2)
            print("✅ API server shutdown requested")
        except:
            pass
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
    if args.bot_action == 'start':
        token = args.token or os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            print("❌ Telegram bot token required!")
            print("Set with: export TELEGRAM_BOT_TOKEN='your_token'")
            print("Or use: --token 'your_token'")
            return
        bot_scripts = {
            'mp002': 'integrations/telegram_bot/mp002_progress_bot.py',
            'test': 'integrations/telegram_bot/test_bot.py',
            'main': 'integrations/telegram_bot/test_bot.py'
        }
        bot_script = bot_scripts.get(args.type, bot_scripts['mp002'])
        if not Path(bot_script).exists():
            print(f"❌ Bot script not found: {bot_script}")
            return
        print(f"🤖 Starting {args.type} Telegram bot...")
        env = os.environ.copy()
        env['TELEGRAM_BOT_TOKEN'] = token
        cmd = f"source venv/bin/activate && python {bot_script}"
        if args.background:
            cmd += " &"
        process = subprocess.Popen(cmd, shell=True, cwd='.', env=env)
        if args.background:
            print(f"✅ {args.type} bot started in background (PID: {process.pid})")
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
        bot_types = ['mp002', 'test', 'main']
        active_bots = []
        for bot_type in bot_types:
            pid_file = Path(f'.bot_{bot_type}_pid')
            if pid_file.exists():
                try:
                    with open(pid_file, 'r') as f:
                        pid = int(f.read().strip())
                    process = psutil.Process(pid)
                    if process.is_running():
                        active_bots.append((bot_type, pid))
                    else:
                        pid_file.unlink()
                except (ValueError, psutil.NoSuchProcess, FileNotFoundError):
                    pid_file.unlink()
        if active_bots:
            print("✅ Active Telegram Bots:")
            for bot_type, pid in active_bots:
                print(f"   🤖 {bot_type} bot (PID: {pid})")
        else:
            print("❌ No active Telegram bots found")
    elif args.bot_action == 'stop':
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
            api_args = type('Args', (), {
                'api_action': 'start',
                'port': 8000,
                'host': '0.0.0.0',
                'background': True
            })()
            await cmd_api_management(api_args)
            time.sleep(2)
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
            bot_args = type('Args', (), {'bot_action': 'stop'})()
            await cmd_bot_management(bot_args)
            api_args = type('Args', (), {'api_action': 'stop'})()
            await cmd_api_management(api_args)
            print("✅ All services stopped")
        elif args.services_action == 'status':
            print("📊 Services Status Report:")
            print("=" * 30)
            api_args = type('Args', (), {'api_action': 'status'})()
            await cmd_api_management(api_args)
            print()
            bot_args = type('Args', (), {'bot_action': 'status'})()
            await cmd_bot_management(bot_args) 