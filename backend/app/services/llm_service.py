import ollama
import google.generativeai as genai
from typing import Dict, List, Optional
from app.core.config import settings
from app.services.observability_service import ObservabilityService
import json
import time

class LLMService:
    def __init__(self):
        self.provider = settings.DEFAULT_LLM_PROVIDER
        self.fallback_provider = settings.FALLBACK_LLM_PROVIDER
        self.obs_service = ObservabilityService()
        
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
        
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.ollama_model = settings.OLLAMA_MODEL
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.3, trace: Optional[any] = None) -> str:
        start_time = time.time()
        
        try:
            if self.provider == "ollama":
                response = self._generate_ollama(prompt, system_prompt, temperature)
            elif self.provider == "gemini" and self.gemini_model:
                response = self._generate_gemini(prompt, system_prompt, temperature)
            else:
                if self.fallback_provider == "ollama":
                    response = self._generate_ollama(prompt, system_prompt, temperature)
                elif self.fallback_provider == "gemini" and self.gemini_model:
                    response = self._generate_gemini(prompt, system_prompt, temperature)
                else:
                    raise Exception("No LLM provider available")
            
            latency_ms = (time.time() - start_time) * 1000
            
            if trace:
                self.obs_service.log_llm_call(
                    trace=trace,
                    model=self.provider,
                    prompt=prompt[:500],
                    response=response[:500],
                    metadata={"temperature": temperature, "has_system_prompt": system_prompt is not None},
                    latency_ms=latency_ms
                )
            
            return response
            
        except Exception as e:
            if self.fallback_provider and self.fallback_provider != self.provider:
                if self.fallback_provider == "ollama":
                    return self._generate_ollama(prompt, system_prompt, temperature)
                elif self.fallback_provider == "gemini" and self.gemini_model:
                    return self._generate_gemini(prompt, system_prompt, temperature)
            raise e
    
    def _generate_ollama(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = ollama.chat(
            model=self.ollama_model,
            messages=messages,
            options={"temperature": temperature}
        )
        
        return response['message']['content']
    
    def _generate_gemini(self, prompt: str, system_prompt: Optional[str], temperature: float) -> str:
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self.gemini_model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(temperature=temperature)
        )
        
        return response.text
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, trace: Optional[any] = None) -> Dict:
        response_text = self.generate(prompt, system_prompt, temperature=0.1, trace=trace)
        
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            else:
                return json.loads(response_text)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON", "raw_response": response_text}