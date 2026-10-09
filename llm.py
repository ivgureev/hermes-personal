from __future__ import annotations
import os
from pathlib import Path
import requests

ROOT = Path(__file__).parent
SYSTEM_PROMPT = (ROOT / "prompt" / "system_prompt.md").read_text(encoding="utf-8")

class LLMError(RuntimeError):
    pass


def configured() -> bool:
    return bool(os.getenv("LLM_API_KEY"))


def provider_summary() -> str:
    if not configured():
        return "Демонстрационный режим"
    return f"{os.getenv('LLM_MODEL', 'deepseek-chat')} · OpenAI-compatible API"


def demo_answer(user_text: str, risk_level: str) -> str:
    return (
        "[Допущение] Подключение к языковой модели не настроено, поэтому показан безопасный демонстрационный ответ.\n\n"
        f"[Факт] Запрос принят. Уровень риска: **{risk_level}**.\n\n"
        "Для полноценного ответа задайте `LLM_API_KEY`, `LLM_BASE_URL` и `LLM_MODEL` "
        "по примеру файла `.env.example`, затем перезапустите приложение."
    )


def chat(messages: list[dict], risk_level: str) -> str:
    if not configured():
        return demo_answer(messages[-1]["content"], risk_level)
    base = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/")
    model = os.getenv("LLM_MODEL", "deepseek-chat")
    timeout = int(os.getenv("LLM_TIMEOUT", "120"))
    payload = {
        "model": model,
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.2")),
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + [
            {"role": m["role"], "content": m["content"]} for m in messages[-30:]
        ],
    }
    try:
        response = requests.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}", "Content-Type": "application/json"},
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError, ValueError) as exc:
        raise LLMError(f"Модель не вернула корректный ответ: {exc}") from exc
