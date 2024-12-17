import requests
import json
from typing import List, Dict, Optional
from config import load_config

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
        
        # Load configuration
        config = load_config()
        self.endpoint = config.get('litellm_endpoint', 'https://api.litellm.ai/v1/chat/completions')
        self.max_tokens = config.get('max_tokens', 500)
        self.temperature = config.get('temperature', 0.7)

    def chat_complete(self, messages: List[Message]) -> Optional[str]:
        """Send a chat completion request to LiteLLM proxy."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "ai-commit-python"
        }

        payload = {
            "model": self.model,
            "messages": [msg.to_dict() for msg in messages],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": False
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 400 and "Input is too long" in response.text:
                print("Warning: The diff was too large and was truncated. The commit message will be based on the visible changes.")
            
            response.raise_for_status()
            
            data = response.json()
            self.total_tokens += data.get("usage", {}).get("total_tokens", 0)
            
            answer = data["choices"][0]["message"]["content"]
            return answer.strip().strip('"')
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response details: {e.response.text}")
            return None

    def single_question(self, question: str) -> Optional[str]:
        """Ask a single question to the model."""
        messages = [Message(role="user", content=question)]
        return self.chat_complete(messages)
