import threading

from app import config


class ScriptLLM:
    """Qwen2.5 instruct model used to write voice-over scripts (lazy-loaded singleton)."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(config.LLM_MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(
            config.LLM_MODEL_ID, torch_dtype="auto", device_map="auto"
        )

    @classmethod
    def get(cls) -> "ScriptLLM":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
        return cls._instance

    def chat(self, system: str, user: str, max_new_tokens: int = 512) -> str:
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        output = self.model.generate(
            **inputs, max_new_tokens=max_new_tokens, do_sample=True, temperature=0.7, top_p=0.9
        )
        new_tokens = output[0][inputs.input_ids.shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True)
