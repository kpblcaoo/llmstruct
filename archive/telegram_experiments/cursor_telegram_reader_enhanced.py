#!/usr/bin/env python3
"""
Enhanced Cursor Telegram Reader
Читает cursor команды с улучшенной поддержкой reply context
"""

import os
import time
import json
from typing import List, Dict, Optional
from datetime import datetime

class EnhancedCursorTelegramReader:
    """Enhanced reader для cursor команд из Telegram логов"""
    
    def __init__(self):
        self.cursor_log_file = "logs/telegram/cursor_commands.log"
        self.user_log_file = "logs/telegram/user_messages.log"
        self.processed_commands = set()
        self.last_check = 0
    
    def read_cursor_commands(self) -> List[Dict]:
        """Читает новые cursor команды"""
        if not os.path.exists(self.cursor_log_file):
            return []
        
        commands = []
        try:
            with open(self.cursor_log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse command entries
            entries = content.split("=== CURSOR COMMAND")
            for entry in entries[1:]:  # Skip empty first part
                if entry.strip():
                    command_data = self._parse_cursor_command(entry)
                    if command_data and command_data['id'] not in self.processed_commands:
                        commands.append(command_data)
                        self.processed_commands.add(command_data['id'])
        
        except Exception as e:
            print(f"Error reading cursor commands: {e}")
        
        return commands
    
    def _parse_cursor_command(self, entry: str) -> Optional[Dict]:
        """Parse single cursor command entry"""
        try:
            lines = entry.strip().split('\n')
            if len(lines) < 3:
                return None
            
            # Extract timestamp
            timestamp_line = lines[0].strip()
            if " ===" in timestamp_line:
                timestamp_str = timestamp_line.split(" ===")[0].strip()
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            else:
                timestamp = datetime.now()
            
            command_data = {
                'id': f"cursor_{int(timestamp.timestamp())}",
                'timestamp': timestamp.isoformat(),
                'from_user': 'Unknown',
                'command': '',
                'context': '',
                'raw_entry': entry
            }
            
            # Parse fields
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("👤 FROM:"):
                    command_data['from_user'] = line[8:].strip()
                elif line.startswith("🎯 COMMAND:"):
                    command_data['command'] = line[11:].strip()
                elif line.startswith("📝 CONTEXT:"):
                    command_data['context'] = line[11:].strip()
            
            return command_data
            
        except Exception as e:
            print(f"Error parsing cursor command: {e}")
            return None
    
    def get_recent_user_messages(self, limit: int = 5) -> List[Dict]:
        """Получает последние сообщения пользователя для контекста"""
        if not os.path.exists(self.user_log_file):
            return []
        
        messages = []
        try:
            with open(self.user_log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            entries = content.split("=== 2025-")
            for entry in entries[-limit:]:  # Last N entries
                if entry.strip():
                    # Add back the date prefix
                    entry = "=== 2025-" + entry
                    msg_data = self._parse_user_message(entry)
                    if msg_data:
                        messages.append(msg_data)
        
        except Exception as e:
            print(f"Error reading user messages: {e}")
        
        return messages[-limit:]  # Return last N messages
    
    def _parse_user_message(self, entry: str) -> Optional[Dict]:
        """Parse user message entry"""
        try:
            lines = entry.strip().split('\n')
            if len(lines) < 3:
                return None
            
            # Extract timestamp from first line
            timestamp_line = lines[0].strip()
            if "===" in timestamp_line:
                timestamp_str = timestamp_line.replace("===", "").strip()
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            msg_data = {
                'timestamp': timestamp.isoformat(),
                'user': 'Unknown',
                'type': 'text',
                'message': '',
                'chat_id': None,
                'reply_to': None
            }
            
            # Parse fields
            for line in lines[1:]:
                line = line.strip()
                if line.startswith("👤 USER:"):
                    msg_data['user'] = line[8:].strip()
                elif line.startswith("📱 TYPE:"):
                    msg_data['type'] = line[8:].strip()
                elif line.startswith("💬 MESSAGE:"):
                    msg_data['message'] = line[11:].strip()
                elif line.startswith("🆔 CHAT_ID:"):
                    try:
                        msg_data['chat_id'] = int(line[11:].strip())
                    except:
                        pass
                elif line.startswith("↩️ REPLY_TO:"):
                    msg_data['reply_to'] = line[12:].strip()
            
            return msg_data
            
        except Exception as e:
            print(f"Error parsing user message: {e}")
            return None
    
    def poll_for_commands(self, callback_func, poll_interval: int = 2):
        """Polling для новых команд"""
        print(f"🔍 Polling for cursor commands every {poll_interval}s...")
        print(f"📁 Watching: {self.cursor_log_file}")
        
        while True:
            try:
                commands = self.read_cursor_commands()
                for command in commands:
                    print(f"\n🎯 New cursor command: {command['command'][:50]}...")
                    callback_func(command)
                
                time.sleep(poll_interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Polling stopped")
                break
            except Exception as e:
                print(f"❌ Polling error: {e}")
                time.sleep(poll_interval)

def handle_cursor_command(command_data: Dict):
    """Example handler for cursor commands"""
    print(f"\n" + "="*60)
    print(f"📅 Timestamp: {command_data['timestamp']}")
    print(f"👤 From: {command_data['from_user']}")
    print(f"🎯 Command: {command_data['command']}")
    if command_data['context']:
        print(f"📝 Context: {command_data['context']}")
    print("="*60)
    
    # Here you could:
    # 1. Process the command
    # 2. Send to LLM/API
    # 3. Execute actions
    # 4. Send response back to Telegram
    
    # Example processing
    if "статус" in command_data['command'].lower():
        print("🔍 Processing status request...")
    elif "помощь" in command_data['command'].lower():
        print("📚 Processing help request...")
    else:
        print(f"⚙️ Processing general command: {command_data['command'][:30]}...")

def main():
    """Main entry point"""
    reader = EnhancedCursorTelegramReader()
    
    print("🚀 Enhanced Cursor Telegram Reader")
    print("Monitors cursor commands from Telegram bot")
    print("Press Ctrl+C to stop\n")
    
    # Show recent context
    recent_messages = reader.get_recent_user_messages(3)
    if recent_messages:
        print("📝 Recent user messages context:")
        for msg in recent_messages:
            print(f"  {msg['timestamp'][:19]} | {msg['user']}: {msg['message'][:50]}...")
        print()
    
    # Start polling
    reader.poll_for_commands(handle_cursor_command)

if __name__ == "__main__":
    main() 