# Ollama LLM Service
import logging
import httpx
from typing import Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama LLM"""

    def __init__(self):
        self.api_url = settings.OLLAMA_API_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = 120.0  # seconds

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """
        Generate a response from Ollama
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response dict with 'response' key
        """
        try:
            url = f"{self.api_url}/api/generate"
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt

            logger.info(f"Calling Ollama at {url} with model {self.model}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
                
            return {
                "response": result.get("response", ""),
                "model": result.get("model", self.model),
                "done": result.get("done", True),
            }

        except httpx.TimeoutException:
            logger.error("Ollama request timed out")
            return {"response": "Error: LLM request timed out. Please try again.", "error": "timeout"}
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e}")
            return {"response": f"Error: LLM service error ({e.response.status_code})", "error": str(e)}
        except Exception as e:
            logger.error(f"Ollama error: {str(e)}")
            return {"response": f"Error: Could not connect to LLM service. Is Ollama running?", "error": str(e)}

    async def chat(
        self,
        messages: list,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Chat completion with message history"""
        try:
            url = f"{self.api_url}/api/chat"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                }
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()

            return {
                "response": result.get("message", {}).get("content", ""),
                "model": result.get("model", self.model),
            }

        except Exception as e:
            logger.error(f"Ollama chat error: {str(e)}")
            return {"response": f"Error: {str(e)}", "error": str(e)}

    async def health_check(self) -> bool:
        """Check if Ollama is available"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.api_url}/api/tags")
                return response.status_code == 200
        except:
            return False


# Singleton instance
ollama_service = OllamaService()
