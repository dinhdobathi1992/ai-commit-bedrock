import requests
import json
from typing import List, Dict, Optional

class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

class LiteLLMClient:
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.total_tokens = 0
        self.endpoint = "https://litellm.shared-services.adb.adi.tech/v1/chat/completions"

    def chat_complete(self, messages: List[Message]) -> Optional[str]:
        """Send a chat completion request to LiteLLM proxy."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "ai-commit-python"
        }

        payload = {
            "model": self.model,
            "messages": [msg.to_dict() for msg in messages]
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            self.total_tokens += data.get("usage", {}).get("total_tokens", 0)
            
            answer = data["choices"][0]["message"]["content"]
            return answer.strip().strip('"')
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {str(e)}")
            return None

    def single_question(self, question: str) -> Optional[str]:
        """Ask a single question to the model."""
        messages = [Message(role="user", content=question)]
        return self.chat_complete(messages)
