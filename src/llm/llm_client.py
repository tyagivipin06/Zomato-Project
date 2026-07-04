import time
import logging
from typing import List, Dict, Any
import groq
from groq import Groq
from src.config import settings

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        # The Groq client automatically picks up GROQ_API_KEY from the environment
        # as long as it is set, which is handled by our settings.
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        
    def complete(self, messages: List[Dict[str, str]], temperature: float = None) -> str:
        temp = temperature if temperature is not None else settings.GROQ_TEMPERATURE
        model = settings.GROQ_MODEL
        
        max_retries = 3
        base_wait = 2
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                response = self.client.chat.completions.create(
                    messages=messages,
                    model=model,
                    temperature=temp,
                    response_format={"type": "json_object"}
                )
                latency = time.time() - start_time
                tokens = response.usage.total_tokens if hasattr(response, 'usage') and response.usage else 0
                logger.info(f"LLM call completed in {latency:.2f}s | tokens used: {tokens}")
                return response.choices[0].message.content
            except groq.RateLimitError as e:
                wait_time = base_wait * (2 ** attempt)
                logger.warning(f"Groq Rate limit hit. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            except Exception as e:
                logger.error(f"Groq API error: {e}")
                raise
                
        raise Exception("Groq API failed after max retries")
