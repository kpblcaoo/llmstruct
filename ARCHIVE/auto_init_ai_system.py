#!/usr/bin/env python3
"""
🚀 Автоматическая инициализация AI системы при открытии проекта в Cursor
Этот файл автоматически инициализирует систему самоанализа AI возможностей
ENHANCED: Интеграция с workflow системой, сессиями и context tags
"""

import os
import sys
import json
import logging
from pathlib import Path
import time

# Setup logging (Grok suggestion)
logging.basicConfig(
    filename='ai_system.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные переменные для доступа к AI системе
AI_CAPABILITIES = None
AI_STATUS = {"initialized": False, "error": None}

def auto_initialize_ai_system():
    """Автоматическая инициализация AI системы при открытии проекта"""
    
    global AI_CAPABILITIES, AI_STATUS
    
    if AI_STATUS["initialized"]:
        return AI_CAPABILITIES
    
    try:
        # Определяем корень проекта
        project_root = Path(__file__).parent
        
        # Добавляем путь к модулям
        src_path = project_root / 'src'
        if src_path.exists():
            sys.path.insert(0, str(src_path))
        
        # Проверяем наличие ключевых файлов
        required_files = [
            project_root / 'struct.json',
            project_root / 'src' / 'llmstruct' / 'ai_self_awareness.py'
        ]
        
        missing_files = [f for f in required_files if not f.exists()]
        if missing_files:
            AI_STATUS["error"] = f"Missing required files: {[str(f) for f in missing_files]}"
            logger.error(AI_STATUS["error"])
            print(f"⚠️  AI System: {AI_STATUS['error']}")
            return None
        
        # Инициализируем систему самоанализа
        from llmstruct.ai_self_awareness import SystemCapabilityDiscovery
        
        AI_CAPABILITIES = SystemCapabilityDiscovery(str(project_root))
        
        # Быстрая проверка возможностей (без полного анализа)
        capabilities = AI_CAPABILITIES.discover_all_capabilities()
        
        # Статус инициализации
        AI_STATUS["initialized"] = True
        tools_count = len(capabilities.tools)
        active_tools = len([t for t in capabilities.tools.values() if t.status.value == 'available'])
        
        # Получаем workflow контекст
        workflow_context = get_current_workflow_context()
        
        print("🧠 AI System AUTO-INITIALIZED!")
        print(f"   ✅ Tools: {active_tools}/{tools_count} active")
        print(f"   ✅ VS Code integration: {'ON' if capabilities.vscode.copilot_integration else 'OFF'}")
        print(f"   ✅ Context modes: {len(capabilities.context.available_modes)}")
        print(f"   ✅ Project modules: 272 | Functions: 1857 | Classes: 183")
        print(f"   🎭 Current mode: {workflow_context['mode']}")
        print(f"   📅 Active session: {workflow_context['session']}")
        print(f"   🌿 Current branch: {workflow_context['branch']}")
        print("   🎯 Use: get_ai_status(), search_ai_capabilities(query), get_workflow_status()")
        
        logger.info(f"AI System initialized successfully. Workflow: {workflow_context}")
        return AI_CAPABILITIES
        
    except Exception as e:
        AI_STATUS["error"] = str(e)
        logger.error(f"AI System initialization failed: {e}")
        print(f"❌ AI System initialization failed: {e}")
        print("   💡 Try: python start_development.py")
        return None

def get_current_workflow_context():
    """Получить контекст текущей workflow сессии и workspace mode"""
    try:
        project_root = Path(__file__).parent
        context = {"session": "none", "mode": "[discuss]", "branch": "main", "epic": None}
        
        # Текущая сессия
        session_file = project_root / 'data' / 'sessions' / 'current_session.json'
        if session_file.exists():
            with open(session_file, 'r') as f:
                session = json.load(f)
                context["session"] = session.get('session_id', 'SES-001')
                context["branch"] = session.get('branch', 'main')
        
        # Workspace mode
        workspace_file = project_root / 'data' / 'workspace' / 'workspace_state.json'
        if workspace_file.exists():
            with open(workspace_file, 'r') as f:
                workspace = json.load(f)
                context["mode"] = workspace.get('current_mode', '[discuss]')
        
        # Epic информация
        roadmap_file = project_root / 'data' / 'sessions' / 'epics_roadmap.json'
        if roadmap_file.exists():
            with open(roadmap_file, 'r') as f:
                roadmap = json.load(f)
                for epic_key, epic_data in roadmap.get('epics', {}).items():
                    if epic_data.get('current_session') == context["session"]:
                        context["epic"] = epic_data.get('name', epic_key)
                        break
        
        logger.info(f"Workflow context loaded: {context}")
        return context
        
    except Exception as e:
        logger.warning(f"Failed to load workflow context: {e}")
        return {"session": "none", "mode": "[discuss]", "branch": "main", "epic": None}

def get_workflow_status():
    """Получить статус workflow с интеграцией метрик"""
    try:
        # Импорт метрик системы
        from src.llmstruct.metrics_tracker import get_metrics_tracker, track_workflow_event
        from src.llmstruct.workspace import WorkspaceStateManager
        
        # Отслеживаем событие запроса статуса
        track_workflow_event("workflow_status_check")
        
        workspace_manager = WorkspaceStateManager()
        current_mode = workspace_manager.get_current_mode()
        session_info = workspace_manager.get_session_info()
        
        # Получение метрик текущей сессии
        metrics_tracker = get_metrics_tracker()
        session_summary = metrics_tracker.get_session_summary()
        
        # Проверка актуальности struct.json
        struct_file = Path("struct.json")
        struct_status = "missing"
        if struct_file.exists():
            import os
            mod_time = os.path.getmtime(struct_file)
            import time
            age_hours = (time.time() - mod_time) / 3600
            
            if age_hours < 1:
                struct_status = "fresh"
                track_workflow_event("struct_json_used")
            elif age_hours < 6:
                struct_status = "recent"
            else:
                struct_status = "outdated"
                track_workflow_event("avoidable_error", "Using outdated struct.json")
        
        # Статус эпиков
        epic_status = "No active epics"
        roadmap_file = project_root / 'data' / 'sessions' / 'epics_roadmap.json'
        if roadmap_file.exists():
            with open(roadmap_file, 'r') as f:
                roadmap = json.load(f)
                total_epics = len(roadmap.get('epics', {}))
                active_epics = len([e for e in roadmap.get('epics', {}).values() if e.get('status') == 'active'])
                epic_status = f"{active_epics}/{total_epics} epics active"
        
        # Workspace capabilities
        workspace_status = "Basic mode"
        try:
            sys.path.insert(0, str(project_root / 'src'))
            from llmstruct.workspace import WorkspaceStateManager
            ws = WorkspaceStateManager()
            workspace_status = f"Advanced: {ws.current_state.current_mode}"
        except:
            pass
        
        return f"""🎭 WORKFLOW STATUS REPORT (Session: {session_summary['session_id']})
=============================================

📅 Session: {session_info.get('session_id', 'SES-001')}
🎯 Epic: {session_info.get('epic', 'None')}
🎭 Mode: {current_mode}
🌿 Branch: {workspace_manager._get_git_branch()}
📊 Epic Status: {len(workspace_manager.get_epic_summaries())}/4 epics active
⚙️  Workspace: {workspace_manager.get_mode_description(current_mode)}

📊 SESSION METRICS:
- Duration: {session_summary['duration']:.0f}s
- Efficiency Score: {session_summary['efficiency_score']:.2f}
- Total Tokens: {session_summary['total_tokens']}
- Tasks: {session_summary['tasks_completed']}/{session_summary['tasks_total']}
- False Paths: {session_summary['false_paths']}

📁 STRUCT.JSON STATUS: {struct_status.upper()}
- Hash: {metrics_tracker.session_data['metadata']['struct_json_hash']}
- Usage Count: {metrics_tracker.session_data['workflow_metrics']['struct_json_usage']}

🔧 Available Commands:
- python scripts/epic_roadmap_manager.py overview
- /workspace mode [code][debug] (if in CLI)
- python -c "from auto_init_ai_system import switch_workspace_mode; switch_workspace_mode('[code]')"
- python -c "from src.llmstruct.metrics_tracker import get_metrics_tracker; print(get_metrics_tracker().get_session_summary())"
"""
    except Exception as e:
        return f"❌ Workflow status error: {e}"

def switch_workspace_mode(mode_string: str):
    """Переключить workspace mode (для CLI integration)"""
    try:
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root / 'src'))
        from llmstruct.workspace import WorkspaceStateManager
        
        ws = WorkspaceStateManager()
        result = ws.set_mode(mode_string)
        
        context = get_current_workflow_context()
        logger.info(f"Workspace mode switched to: {mode_string}")
        return f"✅ Mode switched to: {result['current_mode']}\n🎭 Combination: {result['mode_combination']}\n📊 Context: {context}"
        
    except Exception as e:
        logger.error(f"Failed to switch workspace mode: {e}")
        return f"❌ Failed to switch mode: {e}"

def get_ai_status():
    """Получить статус AI системы"""
    if not AI_STATUS["initialized"]:
        auto_initialize_ai_system()
    
    if AI_CAPABILITIES:
        basic_status = AI_CAPABILITIES.get_enhanced_capabilities_summary()
        workflow_status = get_workflow_status()
        return f"{basic_status}\n\n{workflow_status}"
    else:
        return f"❌ AI System not available: {AI_STATUS.get('error', 'Unknown error')}"

def search_ai_capabilities(query):
    """Поиск возможностей AI с интеграцией актуального struct.json и метрик"""
    try:
        # Трекинг метрик
        from src.llmstruct.metrics_tracker import track_workflow_event, track_task_start, track_task_complete
        
        task_id = f"search_capabilities_{int(time.time())}"
        track_task_start(task_id, "capability_search")
        track_workflow_event("struct_json_used")
        
        # Проверка актуальности struct.json
        struct_file = Path("struct.json")
        if not struct_file.exists():
            track_workflow_event("avoidable_error", "struct.json missing during capability search")
            track_task_complete(task_id, "failed", "struct.json not found")
            return "❌ struct.json not found. Run: python -m llmstruct.cli parse . -o struct.json"
        
        # Загрузка struct.json для поиска
        with open(struct_file, 'r', encoding='utf-8') as f:
            struct_data = json.load(f)
        
        results = []
        query_lower = query.lower()
        
        # Поиск в функциях
        for file_info in struct_data.get('files', []):
            for func in file_info.get('functions', []):
                if (query_lower in func.get('name', '').lower() or 
                    query_lower in func.get('docstring', '').lower()):
                    results.append({
                        'type': 'function',
                        'name': func['name'],
                        'file': file_info['path'],
                        'docstring': func.get('docstring', 'No description')[:100]
                    })
        
        # Поиск в классах
        for file_info in struct_data.get('files', []):
            for cls in file_info.get('classes', []):
                if (query_lower in cls.get('name', '').lower() or 
                    query_lower in cls.get('docstring', '').lower()):
                    results.append({
                        'type': 'class',
                        'name': cls['name'],
                        'file': file_info['path'],
                        'docstring': cls.get('docstring', 'No description')[:100]
                    })
        
        track_task_complete(task_id, "success")
        
        if results:
            output = f"🔍 Found {len(results)} capabilities matching '{query}':\n\n"
            for i, result in enumerate(results[:10], 1):  # Limit to 10 results
                output += f"{i}. **{result['name']}** ({result['type']})\n"
                output += f"   📁 {result['file']}\n"
                output += f"   📝 {result['docstring']}\n\n"
            
            if len(results) > 10:
                output += f"... and {len(results) - 10} more results\n"
            
            return output
        else:
            track_workflow_event("avoidable_error", f"No results for query: {query}")
            return f"❌ No capabilities found matching '{query}'. Try broader terms."
            
    except Exception as e:
        track_task_complete(task_id, "failed", str(e))
        return f"❌ Search error: {e}"

def get_ai_context(mode: str = "focused"):
    """Получить контекст для AI в указанном режиме"""
    if not AI_STATUS["initialized"]:
        auto_initialize_ai_system()
    
    if not AI_CAPABILITIES:
        return "❌ AI System not available"
    
    try:
        # Получаем возможности в указанном режиме
        capabilities = AI_CAPABILITIES.discover_all_capabilities()
        workflow_context = get_current_workflow_context()
        
        context = {
            "mode": mode,
            "tools_active": len([t for t in capabilities.tools.values() if t.status.value == 'available']),
            "vs_code_integration": capabilities.vscode.copilot_integration,
            "available_modes": capabilities.context.available_modes,
            "token_budget": capabilities.context.token_budgets.get(mode, "Unknown"),
            "project_stats": {
                "modules": 272,
                "functions": 1857,
                "classes": 183
            },
            "workflow": workflow_context
        }
        
        return json.dumps(context, indent=2, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Context error for mode '{mode}': {e}")
        return f"❌ Ошибка получения контекста: {e}"

def get_epic_sessions_status():
    """Получить статус всех эпик-сессий"""
    try:
        project_root = Path(__file__).parent
        
        # Загрузить roadmap эпиков
        roadmap_file = project_root / 'data' / 'sessions' / 'epics_roadmap.json'
        if not roadmap_file.exists():
            return "❌ Epic roadmap not found"
        
        with open(roadmap_file, 'r') as f:
            roadmap = json.load(f)
        
        # Загрузить текущие сессии
        sessions_file = project_root / 'data' / 'sessions' / 'ai_sessions.json'
        sessions_data = {}
        if sessions_file.exists():
            with open(sessions_file, 'r') as f:
                sessions_data = json.load(f)
        
        status_lines = ["🎯 EPIC SESSIONS STATUS", "=" * 40, ""]
        
        for epic_key, epic_data in roadmap.get('epics', {}).items():
            epic_name = epic_data.get('name', epic_key)
            epic_status = epic_data.get('status', 'unknown')
            current_session = epic_data.get('current_session')
            
            status_icon = "🟢" if epic_status == "active" else "🟡" if epic_status == "planned" else "⚪"
            status_lines.append(f"{status_icon} {epic_name}")
            
            planned_sessions = epic_data.get('planned_sessions', [])
            if planned_sessions:
                for session in planned_sessions:
                    session_id = session.get('session_id')
                    session_title = session.get('title', 'No title')
                    session_status = session.get('status', 'planned')
                    is_current = "← ACTIVE" if session_id == current_session else ""
                    
                    session_icon = "▶️" if session_status == "active" else "⏸️" if session_status == "planned" else "✅"
                    status_lines.append(f"  {session_icon} {session_id}: {session_title} {is_current}")
            else:
                status_lines.append("  📝 No planned sessions")
            
            status_lines.append("")
        
        return "\n".join(status_lines)
        
    except Exception as e:
        logger.error(f"Failed to get epic sessions status: {e}")
        return f"❌ Error getting epic sessions: {e}"

def create_epic_session(epic_id: str, session_id: str = None):
    """Создать новую сессию для эпика"""
    try:
        project_root = Path(__file__).parent
        
        # Автогенерация session_id если не указан
        if not session_id:
            import datetime
            session_id = f"SES-{epic_id.split('_')[-1].upper()}-{datetime.datetime.now().strftime('%m%d%H%M')}"
        
        # Использовать epic_roadmap_manager для создания сессии
        result = os.system(f"cd {project_root} && python scripts/epic_roadmap_manager.py start --epic-id {epic_id} --session-id {session_id}")
        
        if result == 0:
            logger.info(f"Created epic session: {session_id} for epic {epic_id}")
            return f"✅ Created session {session_id} for epic {epic_id}"
        else:
            return f"❌ Failed to create session for epic {epic_id}"
            
    except Exception as e:
        logger.error(f"Failed to create epic session: {e}")
        return f"❌ Error creating epic session: {e}"

def switch_to_session(session_id: str):
    """Переключиться на другую сессию"""
    try:
        project_root = Path(__file__).parent
        
        # Использовать session_cli для переключения
        result = os.system(f"cd {project_root} && python scripts/session_cli.py switch {session_id}")
        
        if result == 0:
            # Обновить workflow контекст
            context = get_current_workflow_context()
            logger.info(f"Switched to session: {session_id}")
            return f"✅ Switched to session: {session_id}\n📊 Context: {context}"
        else:
            return f"❌ Failed to switch to session {session_id}"
            
    except Exception as e:
        logger.error(f"Failed to switch session: {e}")
        return f"❌ Error switching session: {e}"

def get_available_sessions():
    """Получить список доступных сессий"""
    try:
        project_root = Path(__file__).parent
        
        # Загрузить ai_sessions.json
        sessions_file = project_root / 'data' / 'sessions' / 'ai_sessions.json'
        if not sessions_file.exists():
            return "❌ No sessions file found"
        
        with open(sessions_file, 'r') as f:
            sessions_data = json.load(f)
        
        # Загрузить current_session.json для определения активной сессии
        current_session_file = project_root / 'data' / 'sessions' / 'current_session.json'
        current_session_id = None
        if current_session_file.exists():
            with open(current_session_file, 'r') as f:
                current_data = json.load(f)
                current_session_id = current_data.get('session_id')
        
        sessions_list = ["📋 AVAILABLE SESSIONS", "=" * 30, ""]
        
        for session in sessions_data.get('sessions', []):
            session_id = session.get('id')
            title = session.get('title', 'No title')
            status = session.get('status', 'unknown')
            branch = session.get('branch', 'unknown')
            is_current = " ← CURRENT" if session_id == current_session_id else ""
            
            status_icon = "🟢" if status == "active" else "🟡" if status == "planned" else "⚪"
            sessions_list.append(f"{status_icon} {session_id}: {title}")
            sessions_list.append(f"   Branch: {branch} | Status: {status}{is_current}")
            sessions_list.append("")
        
        # Добавить эпик-сессии из roadmap
        roadmap_file = project_root / 'data' / 'sessions' / 'epics_roadmap.json'
        if roadmap_file.exists():
            with open(roadmap_file, 'r') as f:
                roadmap = json.load(f)
            
            sessions_list.append("🎯 EPIC SESSIONS:")
            sessions_list.append("")
            
            for epic_key, epic_data in roadmap.get('epics', {}).items():
                planned_sessions = epic_data.get('planned_sessions', [])
                for session in planned_sessions:
                    session_id = session.get('session_id')
                    title = session.get('title', 'No title')
                    status = session.get('status', 'planned')
                    is_current = " ← ACTIVE" if session_id == epic_data.get('current_session') else ""
                    
                    status_icon = "▶️" if status == "active" else "⏸️" 
                    sessions_list.append(f"{status_icon} {session_id}: {title}{is_current}")
                    sessions_list.append(f"   Epic: {epic_data.get('name')} | Branch: {session.get('branch')}")
                    sessions_list.append("")
        
        return "\n".join(sessions_list)
        
    except Exception as e:
        logger.error(f"Failed to get available sessions: {e}")
        return f"❌ Error getting sessions: {e}"

def session_management_commands():
    """Получить список команд для управления сессиями"""
    return """🔄 SESSION MANAGEMENT COMMANDS
=================================

📋 Просмотр сессий:
python -c "from auto_init_ai_system import get_available_sessions; print(get_available_sessions())"
python -c "from auto_init_ai_system import get_epic_sessions_status; print(get_epic_sessions_status())"

🔄 Переключение сессий:
python -c "from auto_init_ai_system import switch_to_session; print(switch_to_session('SES-001'))"
python scripts/session_cli.py switch [session_id]

🚀 Создание epic сессий:
python -c "from auto_init_ai_system import create_epic_session; print(create_epic_session('epic_1_ai_branch_safety'))"
python scripts/epic_roadmap_manager.py start --epic-id epic_1 --session-id SES-E1-001

📊 Статус и контекст:
python scripts/session_cli.py current
python scripts/session_cli.py worklog
python -c "from auto_init_ai_system import get_workflow_status; print(get_workflow_status())"

📝 Логирование событий:
python scripts/session_cli.py log "Started working on feature X"

🎭 Workspace интеграция:
python -c "from auto_init_ai_system import switch_workspace_mode; print(switch_workspace_mode('[code]'))" """

# Автозапуск при импорте модуля
if __name__ != "__main__":
    auto_initialize_ai_system()

# Если запуск как скрипт - показать статус
if __name__ == "__main__":
    print("🚀 MANUAL AI SYSTEM INITIALIZATION")
    print("=" * 40)
    auto_initialize_ai_system()
    print("\n" + get_ai_status()) 