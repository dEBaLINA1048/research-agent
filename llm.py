"""IBM Granite wrapper (watsonx.ai on IBM Cloud Lite)."""
import json
import os
import re

from dotenv import load_dotenv

load_dotenv()


class GraniteLLM:
    def __init__(self):
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.url = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        self.model_id = os.getenv("GRANITE_MODEL_ID", "ibm/granite-3-8b-instruct")
        self._model = None

    def _get_model(self):
        if self._model is None:
            if not self.api_key or not self.project_id:
                raise RuntimeError(
                    "Missing WATSONX_API_KEY / WATSONX_PROJECT_ID. Copy .env.example to .env and fill it in."
                )
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference

            self._model = ModelInference(
                model_id=self.model_id,
                credentials=Credentials(url=self.url, api_key=self.api_key),
                project_id=self.project_id,
            )
        return self._model

    def ask(self, system: str, user: str, max_tokens: int = 900, temperature: float = 0.2) -> str:
        model = self._get_model()
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        params = {"max_tokens": max_tokens, "temperature": temperature}
        try:
            resp = model.chat(messages=messages, params=params)
            return resp["choices"][0]["message"]["content"].strip()
        except Exception:
            # Fallback to plain text generation
            prompt = f"{system}\n\n{user}"
            gen_params = {
                "decoding_method": "greedy",
                "max_new_tokens": max_tokens,
                "repetition_penalty": 1.05,
            }
            return model.generate_text(prompt=prompt, params=gen_params).strip()

    def ask_json(self, system: str, user: str, max_tokens: int = 700):
        raw = self.ask(system + "\nRespond with valid JSON only, no commentary.", user, max_tokens, 0.0)
        match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
        try:
            return json.loads(match.group(1) if match else raw)
        except Exception:
            return None
