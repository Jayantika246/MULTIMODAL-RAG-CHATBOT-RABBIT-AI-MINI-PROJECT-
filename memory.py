import uuid
from collections import defaultdict
from typing import List, Dict

class ConversationMemory:
    def __init__(self, max_exchanges=5):
        self.sessions = defaultdict(list)
        self.max_exchanges = max_exchanges
    
    def generate_session_id(self) -> str:
        """Generate a new unique session ID"""
        return str(uuid.uuid4())
    
    def add_exchange(self, session_id: str, user_message: str, assistant_message: str):
        """Add a user-assistant exchange to session history"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        # Add user message
        self.sessions[session_id].append({
            'role': 'user',
            'content': user_message
        })
        
        # Add assistant message
        self.sessions[session_id].append({
            'role': 'assistant',
            'content': assistant_message
        })
        
        # Keep only last max_exchanges (each exchange = 2 messages)
        max_messages = self.max_exchanges * 2
        if len(self.sessions[session_id]) > max_messages:
            self.sessions[session_id] = self.sessions[session_id][-max_messages:]
    
    def get_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        return self.sessions.get(session_id, [])
    
    def format_history(self, session_id: str) -> str:
        """Format conversation history as a string for LLM prompt"""
        history = self.get_history(session_id)
        
        if not history:
            return "No previous conversation."
        
        formatted = []
        for msg in history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted)
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
