#!/usr/bin/env python3
"""
Session Management CLI
Automates session tracking, worklog updates, and session switching for llmstruct.
Part of the comprehensive session management system.
"""

import json
import os
import subprocess
import sys
from datetime import datetime

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def get_current_branch():
    """Get current git branch."""
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def load_json_file(file_path):
    """Load JSON file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"{Colors.RED}❌ Error loading {file_path}: {e}{Colors.ENDC}")
        return None

def save_json_file(file_path, data):
    """Save JSON file with error handling."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Error saving {file_path}: {e}{Colors.ENDC}")
        return False

def get_current_timestamp():
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat() + "Z"

def log_event(event_message, author="@kpblcaoo"):
    """Log an event to worklog.json."""
    worklog_path = "data/sessions/worklog.json"
    
    # Load current worklog
    worklog = load_json_file(worklog_path)
    if not worklog:
        # Create new worklog if it doesn't exist
        current_session = load_json_file("data/sessions/current_session.json")
        if not current_session:
            print(f"{Colors.RED}❌ No current session found{Colors.ENDC}")
            return False
            
        worklog = {
            "version": "0.1.0",
            "session_id": current_session.get("session_id", "unknown"),
            "branch": current_session.get("branch", get_current_branch() or "unknown"),
            "log": []
        }
    
    # Add new event
    worklog["log"].append({
        "timestamp": get_current_timestamp(),
        "author": author,
        "event": event_message
    })
    
    # Save updated worklog
    if save_json_file(worklog_path, worklog):
        print(f"{Colors.GREEN}✅ Event logged: {event_message}{Colors.ENDC}")
        return True
    return False

def switch_session(session_id=None):
    """Switch to a different session or create new one."""
    sessions_data = load_json_file("data/sessions/ai_sessions.json")
    if not sessions_data:
        print(f"{Colors.RED}❌ Could not load sessions data{Colors.ENDC}")
        return False
    
    current_branch = get_current_branch()
    
    if session_id:
        # Find specified session
        session = None
        for s in sessions_data["sessions"]:
            if s["id"] == session_id:
                session = s
                break
        
        if not session:
            print(f"{Colors.RED}❌ Session {session_id} not found{Colors.ENDC}")
            return False
    else:
        # Auto-detect session by branch
        session = None
        for s in sessions_data["sessions"]:
            if s["branch"] == current_branch:
                session = s
                break
        
        if not session:
            print(f"{Colors.YELLOW}⚠️  No session found for branch {current_branch}{Colors.ENDC}")
            print("Available sessions:")
            for s in sessions_data["sessions"]:
                print(f"  - {s['id']}: {s['title']} ({s['branch']})")
            return False
    
    # Update current_session.json
    current_session = {
        "version": "0.1.0",
        "session_id": session["id"],
        "branch": session["branch"],
        "status": session["status"],
        "started_at": get_current_timestamp(),
        "author": session["author"],
        "notes": f"Switched to session: {session['title']}"
    }
    
    if save_json_file("data/sessions/current_session.json", current_session):
        print(f"{Colors.GREEN}✅ Switched to session: {session['id']} - {session['title']}{Colors.ENDC}")
        log_event(f"Switched to session {session['id']}: {session['title']}")
        return True
    
    return False

def list_sessions():
    """List all available sessions."""
    sessions_data = load_json_file("data/sessions/ai_sessions.json")
    if not sessions_data:
        return False
    
    print(f"{Colors.BOLD}{Colors.BLUE}📋 Available Sessions{Colors.ENDC}")
    print()
    
    current_session = load_json_file("data/sessions/current_session.json")
    current_id = current_session.get("session_id") if current_session else None
    
    for session in sessions_data["sessions"]:
        status_color = Colors.GREEN if session["status"] == "active" else Colors.YELLOW
        current_marker = " ← CURRENT" if session["id"] == current_id else ""
        
        print(f"{Colors.BOLD}{session['id']}{Colors.ENDC}: {session['title']}")
        print(f"  Branch: {session['branch']}")
        print(f"  Status: {status_color}{session['status']}{Colors.ENDC}{current_marker}")
        print(f"  Author: {session['author']}")
        print(f"  Created: {session['created_at']}")
        print()
    
    return True

def show_current_session():
    """Show current session details."""
    current_session = load_json_file("data/sessions/current_session.json")
    if not current_session:
        print(f"{Colors.RED}❌ No current session active{Colors.ENDC}")
        return False
    
    print(f"{Colors.BOLD}{Colors.BLUE}📌 Current Session{Colors.ENDC}")
    print(f"ID: {current_session['session_id']}")
    print(f"Branch: {current_session['branch']}")
    print(f"Status: {current_session['status']}")
    print(f"Started: {current_session['started_at']}")
    print(f"Author: {current_session['author']}")
    print(f"Notes: {current_session.get('notes', 'No notes')}")
    
    return True

def show_worklog(limit=10):
    """Show recent worklog entries."""
    worklog = load_json_file("data/sessions/worklog.json")
    if not worklog:
        print(f"{Colors.RED}❌ No worklog found{Colors.ENDC}")
        return False
    
    print(f"{Colors.BOLD}{Colors.BLUE}📝 Recent Worklog (Session: {worklog['session_id']}){Colors.ENDC}")
    print()
    
    recent_entries = worklog["log"][-limit:] if len(worklog["log"]) > limit else worklog["log"]
    
    for entry in reversed(recent_entries):
        timestamp = entry["timestamp"][:19]  # Remove Z and microseconds
        print(f"{Colors.YELLOW}{timestamp}{Colors.ENDC} | {entry['author']}")
        print(f"  {entry['event']}")
        print()
    
    return True

def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print(f"{Colors.BOLD}{Colors.BLUE}🔄 Session Management CLI{Colors.ENDC}")
        print()
        print("Usage:")
        print("  python3 session_cli.py list                    # List all sessions")
        print("  python3 session_cli.py current                 # Show current session")
        print("  python3 session_cli.py switch [session_id]     # Switch to session (auto-detect by branch if no ID)")
        print("  python3 session_cli.py log <message>           # Log an event")
        print("  python3 session_cli.py worklog [limit]         # Show recent worklog entries")
        print()
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "list":
        return 0 if list_sessions() else 1
    
    elif command == "current":
        return 0 if show_current_session() else 1
    
    elif command == "switch":
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        return 0 if switch_session(session_id) else 1
    
    elif command == "log":
        if len(sys.argv) < 3:
            print(f"{Colors.RED}❌ Please provide a log message{Colors.ENDC}")
            return 1
        message = " ".join(sys.argv[2:])
        return 0 if log_event(message) else 1
    
    elif command == "worklog":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 10
        return 0 if show_worklog(limit) else 1
    
    else:
        print(f"{Colors.RED}❌ Unknown command: {command}{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
