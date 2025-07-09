"""
Ollama integration for the contemplation loop
"""
import requests
import json
from typing import Optional


class OllamaClient:
    """Simple Ollama client for contemplation loop"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        
    def generate(self, prompt: str, model: str = "llama3.2:latest", 
                max_tokens: int = 100) -> Optional[str]:
        """Generate response from Ollama"""
        try:
            url = f"{self.base_url}/api/generate"
            
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except requests.exceptions.RequestException as e:
            print(f"Ollama request failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False


# Global client instance
ollama = OllamaClient()
