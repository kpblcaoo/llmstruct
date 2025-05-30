#!/usr/bin/env python3
"""
Memory Manager for LLMStruct Telegram Bot
Управляет памятью, контекстом и персистентным хранением
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Сообщение в разговоре"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: str
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    token_count: Optional[int] = None

@dataclass
class ConversationSession:
    """Сессия разговора"""
    session_id: str
    chat_id: int
    user_id: int
    user_name: str
    started_at: str
    last_activity: str
    messages: List[ConversationMessage]
    context_summary: str = ""
    topic_tags: List[str] = None
    message_count: int = 0

class TelegramMemoryManager:
    """Управляет памятью и контекстом для Telegram бота"""
    
    def __init__(self, storage_dir: str = "memory_storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Файлы хранения
        self.sessions_file = self.storage_dir / "telegram_sessions.json"
        self.global_memory_file = self.storage_dir / "global_memory.json"
        self.user_profiles_file = self.storage_dir / "user_profiles.json"
        
        # Кеш в памяти
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.global_memory: Dict[str, Any] = {}
        self.user_profiles: Dict[int, Dict[str, Any]] = {}
        
        # Настройки
        self.max_messages_per_session = 200
        self.max_context_tokens = 8000
        self.session_timeout_hours = 48
        
        # Загружаем данные
        self._load_data()
    
    def _load_data(self):
        """Загружает данные из файлов"""
        try:
            # Загружаем сессии
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_data in data.values():
                        session = ConversationSession(
                            session_id=session_data["session_id"],
                            chat_id=session_data["chat_id"],
                            user_id=session_data["user_id"],
                            user_name=session_data["user_name"],
                            started_at=session_data["started_at"],
                            last_activity=session_data["last_activity"],
                            messages=[
                                ConversationMessage(**msg) for msg in session_data["messages"]
                            ],
                            context_summary=session_data.get("context_summary", ""),
                            topic_tags=session_data.get("topic_tags", []),
                            message_count=session_data.get("message_count", 0)
                        )
                        self.active_sessions[session.session_id] = session
            
            # Загружаем глобальную память
            if self.global_memory_file.exists():
                with open(self.global_memory_file, 'r', encoding='utf-8') as f:
                    self.global_memory = json.load(f)
            
            # Загружаем профили пользователей
            if self.user_profiles_file.exists():
                with open(self.user_profiles_file, 'r', encoding='utf-8') as f:
                    self.user_profiles = {int(k): v for k, v in json.load(f).items()}
                    
            logger.info(f"Loaded {len(self.active_sessions)} sessions, {len(self.user_profiles)} user profiles")
            
        except Exception as e:
            logger.error(f"Failed to load memory data: {e}")
    
    def _save_data(self):
        """Сохраняет данные в файлы"""
        try:
            # Сохраняем сессии
            sessions_data = {}
            for session_id, session in self.active_sessions.items():
                sessions_data[session_id] = {
                    "session_id": session.session_id,
                    "chat_id": session.chat_id,
                    "user_id": session.user_id,
                    "user_name": session.user_name,
                    "started_at": session.started_at,
                    "last_activity": session.last_activity,
                    "messages": [asdict(msg) for msg in session.messages],
                    "context_summary": session.context_summary,
                    "topic_tags": session.topic_tags or [],
                    "message_count": session.message_count
                }
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
            
            # Сохраняем глобальную память
            with open(self.global_memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.global_memory, f, indent=2, ensure_ascii=False)
            
            # Сохраняем профили пользователей
            with open(self.user_profiles_file, 'w', encoding='utf-8') as f:
                json.dump({str(k): v for k, v in self.user_profiles.items()}, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to save memory data: {e}")
    
    def get_or_create_session(self, chat_id: int, user_id: int, user_name: str) -> ConversationSession:
        """Получает или создает сессию разговора"""
        session_id = f"tg_{chat_id}_{user_id}"
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            # Проверяем таймаут
            last_activity = datetime.fromisoformat(session.last_activity)
            if datetime.now() - last_activity > timedelta(hours=self.session_timeout_hours):
                # Архивируем старую сессию и создаем новую
                self._archive_session(session_id)
                session = self._create_new_session(chat_id, user_id, user_name)
        else:
            session = self._create_new_session(chat_id, user_id, user_name)
        
        self.active_sessions[session_id] = session
        return session
    
    def _create_new_session(self, chat_id: int, user_id: int, user_name: str) -> ConversationSession:
        """Создает новую сессию"""
        session_id = f"tg_{chat_id}_{user_id}"
        now = datetime.now().isoformat()
        
        return ConversationSession(
            session_id=session_id,
            chat_id=chat_id,
            user_id=user_id,
            user_name=user_name,
            started_at=now,
            last_activity=now,
            messages=[],
            topic_tags=[]
        )
    
    def add_message(self, session: ConversationSession, role: str, content: str, user_name: str = None):
        """Добавляет сообщение в сессию"""
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            user_id=session.user_id if role == "user" else None,
            user_name=user_name or session.user_name if role == "user" else "Assistant"
        )
        
        session.messages.append(message)
        session.last_activity = message.timestamp
        session.message_count += 1
        
        # Обрезаем старые сообщения если превышен лимит
        if len(session.messages) > self.max_messages_per_session:
            # Сохраняем системные сообщения и важные пользовательские сообщения
            system_messages = [msg for msg in session.messages if msg.role == "system"]
            important_keywords = ["кодовое слово", "морковка", "важно", "запомни", "помни"]
            
            # Сохраняем сообщения с важными ключевыми словами
            important_messages = []
            for msg in session.messages:
                if any(keyword in msg.content.lower() for keyword in important_keywords):
                    important_messages.append(msg)
            
            # Берём последние сообщения
            keep_count = self.max_messages_per_session - len(system_messages) - len(important_messages)
            recent_messages = [msg for msg in session.messages[-keep_count:] if msg not in important_messages and msg not in system_messages]
            
            # Объединяем все типы сообщений
            session.messages = system_messages + important_messages + recent_messages
        
        # Обновляем профиль пользователя
        self._update_user_profile(session.user_id, content, role)
        
        # Автосохранение после каждого сообщения для важной информации
        if any(keyword in content.lower() for keyword in ["кодовое слово", "морковка", "важно", "запомни"]) or session.message_count % 3 == 0:
            self._save_data()
    
    def get_conversation_context(self, session: ConversationSession, max_tokens: int = None) -> List[Dict[str, str]]:
        """Получает контекст разговора для LLM"""
        max_tokens = max_tokens or self.max_context_tokens
        
        # Строим историю сообщений
        messages = []
        token_count = 0
        
        # Добавляем системное сообщение с контекстом
        system_content = self._build_system_context(session)
        messages.append({"role": "system", "content": system_content})
        token_count += len(system_content.split()) * 1.3  # Примерная оценка токенов
        
        # Добавляем сообщения с конца, пока не превысим лимит токенов
        for message in reversed(session.messages):
            if message.role == "system":
                continue  # Системные сообщения уже добавлены
                
            msg_tokens = len(message.content.split()) * 1.3
            if token_count + msg_tokens > max_tokens:
                break
                
            messages.insert(-1, {
                "role": message.role,
                "content": message.content
            })
            token_count += msg_tokens
        
        return messages
    
    def _build_system_context(self, session: ConversationSession) -> str:
        """Строит системный контекст для LLM"""
        context = f"""Ты - LLMStruct AI Assistant для Telegram бота.

📊 Информация о пользователе:
• Имя: {session.user_name}
• ID: {session.user_id}
• Сессия начата: {session.started_at}
• Сообщений в сессии: {session.message_count}
"""
        
        # Добавляем информацию о предыдущих темах
        if session.topic_tags:
            context += f"• Обсуждавшиеся темы: {', '.join(session.topic_tags)}\n"
        
        # Добавляем краткое резюме если есть
        if session.context_summary:
            context += f"• Контекст предыдущих разговоров: {session.context_summary}\n"
        
        # Добавляем информацию из профиля пользователя
        user_profile = self.user_profiles.get(session.user_id, {})
        if user_profile:
            if user_profile.get("interests"):
                context += f"• Интересы пользователя: {', '.join(user_profile['interests'])}\n"
            if user_profile.get("preferred_language"):
                context += f"• Предпочтительный язык: {user_profile['preferred_language']}\n"
        
        context += """
🎯 Твои возможности:
• Выполнение системных команд (/cmd)
• Интеграция с LLMStruct API
• Помощь по FastAPI, WebSocket, CLI
• Анализ проекта и кода

Отвечай полезно, учитывая контекст предыдущих сообщений."""
        
        return context
    
    def _update_user_profile(self, user_id: int, content: str, role: str):
        """Обновляет профиль пользователя на основе сообщений"""
        if role != "user":
            return
            
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "message_count": 0,
                "interests": set(),
                "preferred_language": "ru"  # По умолчанию русский
            }
        
        profile = self.user_profiles[user_id]
        profile["last_seen"] = datetime.now().isoformat()
        profile["message_count"] += 1
        
        # Анализируем язык
        if any(char in "abcdefghijklmnopqrstuvwxyz" for char in content.lower()):
            if len([c for c in content if c in "abcdefghijklmnopqrstuvwxyz"]) > len(content) * 0.6:
                profile["preferred_language"] = "en"
        
        # Извлекаем интересы из ключевых слов
        interests = profile.get("interests", set())
        if isinstance(interests, list):
            interests = set(interests)
            
        content_lower = content.lower()
        
        # Технические темы
        tech_keywords = {
            "api": "API development",
            "fastapi": "FastAPI",
            "websocket": "WebSocket",
            "cli": "Command Line",
            "python": "Python",
            "javascript": "JavaScript",
            "telegram": "Telegram Bot",
            "database": "Database",
            "docker": "Docker",
            "git": "Git"
        }
        
        for keyword, interest in tech_keywords.items():
            if keyword in content_lower:
                interests.add(interest)
        
        profile["interests"] = list(interests)
    
    def _archive_session(self, session_id: str):
        """Архивирует сессию"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Создаем краткое резюме сессии
            summary = self._create_session_summary(session)
            
            # Сохраняем в глобальную память
            archive_key = f"archived_session_{session_id}_{int(time.time())}"
            self.global_memory[archive_key] = {
                "session_id": session_id,
                "user_id": session.user_id,
                "summary": summary,
                "message_count": session.message_count,
                "archived_at": datetime.now().isoformat()
            }
            
            # Удаляем из активных
            del self.active_sessions[session_id]
    
    def _create_session_summary(self, session: ConversationSession) -> str:
        """Создает краткое резюме сессии"""
        if len(session.messages) < 3:
            return "Короткий разговор"
        
        topics = set()
        keywords = []
        
        for msg in session.messages[-10:]:  # Последние 10 сообщений
            if msg.role == "user":
                content_lower = msg.content.lower()
                words = content_lower.split()
                keywords.extend([w for w in words if len(w) > 3])
        
        # Находим наиболее частые ключевые слова
        from collections import Counter
        common_words = Counter(keywords).most_common(5)
        
        if common_words:
            summary = f"Обсуждение: {', '.join([word for word, count in common_words])}"
        else:
            summary = "Общий разговор"
        
        return summary
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получает статистику пользователя"""
        profile = self.user_profiles.get(user_id, {})
        active_session = None
        
        for session in self.active_sessions.values():
            if session.user_id == user_id:
                active_session = session
                break
        
        return {
            "profile": profile,
            "active_session": {
                "session_id": active_session.session_id if active_session else None,
                "message_count": active_session.message_count if active_session else 0,
                "started_at": active_session.started_at if active_session else None
            },
            "total_sessions": len([s for s in self.active_sessions.values() if s.user_id == user_id])
        }
    
    def cleanup_old_sessions(self):
        """Очищает старые сессии"""
        cutoff_time = datetime.now() - timedelta(hours=self.session_timeout_hours * 7)  # Неделя
        
        to_archive = []
        for session_id, session in self.active_sessions.items():
            last_activity = datetime.fromisoformat(session.last_activity)
            if last_activity < cutoff_time:
                to_archive.append(session_id)
        
        for session_id in to_archive:
            self._archive_session(session_id)
        
        if to_archive:
            logger.info(f"Archived {len(to_archive)} old sessions")
            self._save_data()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Получает статистику памяти"""
        total_messages = sum(len(session.messages) for session in self.active_sessions.values())
        
        return {
            "active_sessions": len(self.active_sessions),
            "total_messages": total_messages,
            "unique_users": len(set(session.user_id for session in self.active_sessions.values())),
            "user_profiles": len(self.user_profiles),
            "global_memory_items": len(self.global_memory),
            "storage_dir": str(self.storage_dir)
        }
    
    def save(self):
        """Принудительно сохраняет все данные"""
        self._save_data()
        logger.info("Memory data saved manually") 