"""
Ollama integration using urllib (no external dependencies)
"""
import json
import urllib.request
import urllib.error
from typing import Optional


class OllamaClient:
    """Simple Ollama client using urllib"""
    
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
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("response", "").strip()
                
        except urllib.error.URLError as e:
            print(f"Ollama request failed: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            url = f"{self.base_url}/api/tags"
            with urllib.request.urlopen(url, timeout=2) as response:
                return response.status == 200
        except:
            return False


# Global client instance
ollama = OllamaClient()
