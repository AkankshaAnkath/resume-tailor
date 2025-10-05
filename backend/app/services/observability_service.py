from langfuse import Langfuse
from app.core.config import settings
import logging
import time
from typing import Dict, Optional, Any
from functools import wraps
import traceback

logger = logging.getLogger(__name__)

class ObservabilityService:
    def __init__(self):
        self.enabled = settings.USE_LANGFUSE
        
        if self.enabled and settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY:
            self.langfuse = Langfuse(
                public_key=settings.LANGFUSE_PUBLIC_KEY,
                secret_key=settings.LANGFUSE_SECRET_KEY,
                host=settings.LANGFUSE_HOST
            )
        else:
            self.langfuse = None
            self.enabled = False
    
    def create_trace(self, name: str, user_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Any:
        if not self.enabled or not self.langfuse:
            return DummyTrace()
        
        try:
            trace = self.langfuse.trace(
                name=name,
                user_id=user_id,
                metadata=metadata or {}
            )
            return trace
        except Exception as e:
            logger.error(f"Failed to create Langfuse trace: {e}")
            return DummyTrace()
    
    def log_llm_call(self, trace: Any, model: str, prompt: str, response: str, 
                     metadata: Optional[Dict] = None, latency_ms: Optional[float] = None):
        if not self.enabled or not self.langfuse:
            return
        
        try:
            trace.generation(
                name="llm_generation",
                model=model,
                input=prompt,
                output=response,
                metadata=metadata or {},
                latency=latency_ms
            )
        except Exception as e:
            logger.error(f"Failed to log LLM call: {e}")
    
    def log_embedding_call(self, trace: Any, model: str, input_texts: list, 
                          metadata: Optional[Dict] = None, latency_ms: Optional[float] = None):
        if not self.enabled or not self.langfuse:
            return
        
        try:
            trace.span(
                name="embedding_generation",
                input={"texts": input_texts, "count": len(input_texts)},
                metadata={
                    "model": model,
                    **(metadata or {})
                },
                latency=latency_ms
            )
        except Exception as e:
            logger.error(f"Failed to log embedding call: {e}")
    
    def log_error(self, trace: Any, error: Exception, context: Optional[Dict] = None):
        if not self.enabled or not self.langfuse:
            return
        
        try:
            trace.span(
                name="error",
                input=context or {},
                output={
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "traceback": traceback.format_exc()
                }
            )
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
    
    def flush(self):
        if self.enabled and self.langfuse:
            try:
                self.langfuse.flush()
            except Exception as e:
                logger.error(f"Failed to flush Langfuse: {e}")

class DummyTrace:
    def generation(self, *args, **kwargs):
        pass
    
    def span(self, *args, **kwargs):
        pass
    
    def event(self, *args, **kwargs):
        pass

def trace_function(name: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            obs_service = ObservabilityService()
            func_name = name or func.__name__
            
            trace = obs_service.create_trace(
                name=func_name,
                metadata={"function": func.__name__, "module": func.__module__}
            )
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                
                trace.span(
                    name=f"{func_name}_execution",
                    metadata={"latency_ms": latency_ms, "status": "success"}
                )
                
                return result
            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                obs_service.log_error(trace, e, {"function": func_name, "latency_ms": latency_ms})
                raise
            finally:
                obs_service.flush()
        
        return wrapper
    return decorator