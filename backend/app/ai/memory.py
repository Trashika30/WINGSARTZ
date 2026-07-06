from collections import defaultdict
from typing import List, Dict

class ConversationMemory:
    def __init__(self, max_history: int = 6):
        self.max_history = max_history
        self.memory: Dict[int, List[Dict[str, str]]] = defaultdict(list)

    def add_message(self, user_id: int, role: str, content: str):
        self.memory[user_id].append({"role": role, "content": content})
        if len(self.memory[user_id]) > self.max_history:
            self.memory[user_id] = self.memory[user_id][-self.max_history:]

    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        return self.memory[user_id]

    def format_history(self, user_id: int) -> str:
        history = self.get_history(user_id)
        if not history:
            return "No previous conversation history."
        
        formatted = []
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

memory = ConversationMemory()
