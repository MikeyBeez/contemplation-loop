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
        """Generate response from Ollama with streaming"""
        try:
            url = f"{self.base_url}/api/generate"
            
            data = {
                "model": model,
                "prompt": prompt,
                "stream": True,  # Enable streaming
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
            
            full_response = ""
            # Longer timeout for deepseek-r1
            timeout_seconds = 300 if model.startswith('deepseek') else 60
            print(f"[Ollama] Sending request to {model} with {timeout_seconds}s timeout...")
            
            with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
                for line in response:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'response' in chunk:
                            full_response += chunk['response']
                        if chunk.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
                        
            return full_response.strip()
                
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
