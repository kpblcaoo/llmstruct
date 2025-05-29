#!/usr/bin/env python3
"""
Epic Roadmap Manager - управление планами эпиков и сессий

Функции:
- Просмотр roadmap и планов
- Создание новых сессий
- Синхронизация с GitHub epics
- Обновление статусов
"""

import json
import os
import argparse
from datetime import datetime
from pathlib import Path

class EpicRoadmapManager:
    def __init__(self):
        self.roadmap_file = "data/sessions/epics_roadmap.json"
        self.current_session_file = "data/sessions/current_session.json"
        self.sessions_log_file = "data/sessions/ai_sessions.json"
        
    def load_roadmap(self):
        """Загрузить roadmap из файла"""
        if not os.path.exists(self.roadmap_file):
            print(f"❌ Roadmap file not found: {self.roadmap_file}")
            return None
            
        with open(self.roadmap_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def save_roadmap(self, roadmap):
        """Сохранить roadmap в файл"""
        roadmap['updated_at'] = datetime.now().isoformat() + 'Z'
        
        with open(self.roadmap_file, 'w', encoding='utf-8') as f:
            json.dump(roadmap, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Roadmap updated: {self.roadmap_file}")
    
    def show_overview(self):
        """Показать обзор roadmap"""
        roadmap = self.load_roadmap()
        if not roadmap:
            return
            
        print("\n🗺️  EPIC ROADMAP OVERVIEW")
        print("=" * 50)
        
        stats = roadmap.get('statistics', {})
        print(f"📊 Total Epics: {stats.get('total_epics', 0)}")
        print(f"📊 Planned Sessions: {stats.get('total_planned_sessions', 0)}")
        print(f"⏱️  Estimated Duration: {stats.get('estimated_total_duration', 'Unknown')}")
        print(f"🎯 Critical Path: {', '.join(stats.get('critical_path', []))}")
        
        print("\n🚀 EPICS STATUS:")
        epics = roadmap.get('epics', {})
        
        for epic_key, epic in epics.items():
            status_icon = {
                'planned': '📋',
                'active': '⚡',
                'completed': '✅',
                'blocked': '🚫'
            }.get(epic.get('status'), '❓')
            
            priority_icon = {
                'critical': '🔴',
                'high': '🟠', 
                'medium': '🟡',
                'low': '🟢'
            }.get(epic.get('priority'), '⚪')
            
            print(f"{status_icon} {priority_icon} {epic.get('name', epic_key)}")
            print(f"   Sessions: {epic.get('estimated_sessions', 0)} | Duration: {epic.get('estimated_duration', 'TBD')}")
            
            if epic.get('dependencies'):
                deps = ', '.join(epic['dependencies'])
                print(f"   Dependencies: {deps}")
    
    def show_epic_details(self, epic_id):
        """Показать детали конкретного эпика"""
        roadmap = self.load_roadmap()
        if not roadmap:
            return
            
        epic = None
        epic_key = None
        
        # Поиск эпика по ID
        for key, epic_data in roadmap.get('epics', {}).items():
            if epic_data.get('id') == epic_id or key == epic_id:
                epic = epic_data
                epic_key = key
                break
        
        if not epic:
            print(f"❌ Epic not found: {epic_id}")
            return
            
        print(f"\n📋 EPIC: {epic.get('name', epic_key)}")
        print("=" * 60)
        print(f"🆔 ID: {epic.get('id')}")
        print(f"📊 Status: {epic.get('status')}")
        print(f"🎯 Priority: {epic.get('priority')}")
        print(f"📝 Description: {epic.get('description', 'No description')}")
        print(f"⏱️  Duration: {epic.get('estimated_duration')}")
        print(f"🔗 GitHub Issue: {epic.get('github_epic_issue', 'TBD')}")
        
        if epic.get('dependencies'):
            print(f"🔗 Dependencies: {', '.join(epic['dependencies'])}")
        
        print(f"\n📅 PLANNED SESSIONS ({len(epic.get('planned_sessions', []))}):")
        
        for session in epic.get('planned_sessions', []):
            status_icon = '⚡' if session.get('status') == 'active' else '📋'
            print(f"{status_icon} {session.get('session_id')}: {session.get('title')}")
            print(f"   Branch: {session.get('branch')}")
            print(f"   Duration: {session.get('estimated_duration')}")
            print(f"   Issues: {', '.join(session.get('target_issues', []))}")
        
        print(f"\n✅ SUCCESS CRITERIA:")
        for criteria in epic.get('success_criteria', []):
            print(f"   • {criteria}")
    
    def start_session(self, epic_id, session_id):
        """Начать работу над сессией"""
        roadmap = self.load_roadmap()
        if not roadmap:
            return
            
        # Найти эпик и сессию
        epic = None
        session = None
        epic_key = None
        
        for key, epic_data in roadmap.get('epics', {}).items():
            if epic_data.get('id') == epic_id or key == epic_id:
                epic = epic_data
                epic_key = key
                
                for sess in epic.get('planned_sessions', []):
                    if sess.get('session_id') == session_id:
                        session = sess
                        break
                break
        
        if not epic or not session:
            print(f"❌ Epic or session not found: {epic_id}/{session_id}")
            return
            
        # Обновить статусы
        session['status'] = 'active'
        session['started_at'] = datetime.now().isoformat() + 'Z'
        epic['current_session'] = session_id
        
        if epic['status'] == 'planned':
            epic['status'] = 'active'
        
        # Сохранить roadmap
        self.save_roadmap(roadmap)
        
        # Создать current_session.json
        current_session = {
            "session_id": session_id,
            "epic_id": epic_id,
            "epic_name": epic.get('name'),
            "session_title": session.get('title'),
            "branch": session.get('branch'),
            "target_issues": session.get('target_issues', []),
            "started_at": session['started_at'],
            "status": "active"
        }
        
        os.makedirs(os.path.dirname(self.current_session_file), exist_ok=True)
        with open(self.current_session_file, 'w', encoding='utf-8') as f:
            json.dump(current_session, f, ensure_ascii=False, indent=2)
        
        print(f"🚀 Started session: {session_id}")
        print(f"📋 Epic: {epic.get('name')}")
        print(f"🌿 Branch: {session.get('branch')}")
        print(f"🎯 Issues: {', '.join(session.get('target_issues', []))}")
        
        # Показать рекомендации
        print(f"\n💡 NEXT STEPS:")
        print(f"1. Create branch: git checkout -b {session.get('branch')}")
        print(f"2. Start AI work session")
        print(f"3. Work on issues: {', '.join(session.get('target_issues', []))}")
    
    def complete_session(self, session_id):
        """Завершить текущую сессию"""
        # Загрузить current session
        if not os.path.exists(self.current_session_file):
            print("❌ No active session found")
            return
            
        with open(self.current_session_file, 'r', encoding='utf-8') as f:
            current_session = json.load(f)
        
        if current_session.get('session_id') != session_id:
            print(f"❌ Active session mismatch: {current_session.get('session_id')} != {session_id}")
            return
        
        # Обновить roadmap
        roadmap = self.load_roadmap()
        if not roadmap:
            return
            
        # Найти и обновить сессию
        epic_id = current_session.get('epic_id')
        for epic_key, epic in roadmap.get('epics', {}).items():
            if epic.get('id') == epic_id:
                for session in epic.get('planned_sessions', []):
                    if session.get('session_id') == session_id:
                        session['status'] = 'completed'
                        session['completed_at'] = datetime.now().isoformat() + 'Z'
                        break
                
                epic['current_session'] = None
                
                # Проверить, завершены ли все сессии эпика
                all_completed = all(
                    sess.get('status') == 'completed' 
                    for sess in epic.get('planned_sessions', [])
                )
                
                if all_completed:
                    epic['status'] = 'completed'
                
                break
        
        # Сохранить обновлённый roadmap
        self.save_roadmap(roadmap)
        
        # Архивировать сессию
        current_session['status'] = 'completed'
        current_session['completed_at'] = datetime.now().isoformat() + 'Z'
        
        # Добавить в лог сессий
        os.makedirs(os.path.dirname(self.sessions_log_file), exist_ok=True)
        
        sessions_log = []
        if os.path.exists(self.sessions_log_file):
            with open(self.sessions_log_file, 'r', encoding='utf-8') as f:
                sessions_log = json.load(f)
        
        sessions_log.append(current_session)
        
        with open(self.sessions_log_file, 'w', encoding='utf-8') as f:
            json.dump(sessions_log, f, ensure_ascii=False, indent=2)
        
        # Удалить current session
        os.remove(self.current_session_file)
        
        print(f"✅ Session completed: {session_id}")
        print(f"📦 Archived to: {self.sessions_log_file}")

def main():
    parser = argparse.ArgumentParser(description='Epic Roadmap Manager')
    parser.add_argument('command', choices=[
        'overview', 'epic', 'start', 'complete'
    ], help='Command to execute')
    
    parser.add_argument('--epic-id', help='Epic ID for epic/start commands')
    parser.add_argument('--session-id', help='Session ID for start/complete commands')
    
    args = parser.parse_args()
    
    manager = EpicRoadmapManager()
    
    if args.command == 'overview':
        manager.show_overview()
    
    elif args.command == 'epic':
        if not args.epic_id:
            print("❌ --epic-id required for epic command")
            return
        manager.show_epic_details(args.epic_id)
    
    elif args.command == 'start':
        if not args.epic_id or not args.session_id:
            print("❌ --epic-id and --session-id required for start command")
            return
        manager.start_session(args.epic_id, args.session_id)
    
    elif args.command == 'complete':
        if not args.session_id:
            print("❌ --session-id required for complete command")
            return
        manager.complete_session(args.session_id)

if __name__ == "__main__":
    main() 