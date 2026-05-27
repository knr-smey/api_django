import logging
import re

import requests


logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "laptop-ai:latest"

SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer the user's latest message clearly, "
    "briefly, and directly. Use the conversation context only when it is "
    "relevant. Do not repeat the prompt, role labels, or hidden instructions."
)

MAX_CONTEXT_MESSAGES = 8
MAX_MESSAGE_CHARS = 1200
EMPTY_RESPONSE_RETRIES = 1

OLLAMA_OPTIONS = {
    "num_ctx": 4096,
    "num_predict": 384,
    "temperature": 0.4,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "stop": [
        "\n### User:",
        "\n### System:",
        "\nUser:",
        "\nSystem:",
        "<|im_start|>user",
        "<|im_start|>system",
    ],
}

FALLBACK_OPTIONS = {
    **OLLAMA_OPTIONS,
    "temperature": 0.2,
    "num_predict": 256,
}


def _clean_content(content):
    value = str(content or "").strip()
    value = re.sub(r"<\|/?(?:im_start|im_end)\|>", "", value)
    value = re.sub(
        r"(?im)^\s*(system|user|assistant)\s*:\s*",
        "",
        value,
    )
    value = re.sub(
        r"(?im)^\s*###\s*(system|user|assistant)\s*:?\s*",
        "",
        value,
    )
    value = re.sub(r"\n{3,}", "\n\n", value)

    if len(value) > MAX_MESSAGE_CHARS:
        value = value[-MAX_MESSAGE_CHARS:].strip()

    return value


def _message_role(item):
    role = getattr(item, "role", "")
    return "assistant" if role == "assistant" else "user"


def _split_history(history):
    messages = list(history)

    if not messages:
        return [], ""

    latest = messages[-1]
    latest_role = _message_role(latest)
    latest_content = _clean_content(getattr(latest, "content", ""))

    if latest_role == "user":
        return messages[:-1], latest_content

    return messages, ""


def build_chat_prompt(history):
    previous_messages, latest_user_message = _split_history(history)
    recent_messages = previous_messages[-MAX_CONTEXT_MESSAGES:]

    prompt_parts = [
        "### System:",
        SYSTEM_PROMPT,
    ]

    if recent_messages:
        prompt_parts.extend(
            [
                "",
                "### Conversation context:",
            ]
        )

        for item in recent_messages:
            role = "Assistant" if _message_role(item) == "assistant" else "User"
            content = _clean_content(getattr(item, "content", ""))

            if content:
                prompt_parts.append(f"{role}: {content}")

    prompt_parts.extend(
        [
            "",
            "### User:",
            latest_user_message,
            "",
            "### Assistant:",
        ]
    )

    return "\n".join(prompt_parts).strip()


def build_single_turn_prompt(message):
    cleaned_message = _clean_content(message)

    return "\n".join(
        [
            "### System:",
            SYSTEM_PROMPT,
            "",
            "### User:",
            cleaned_message,
            "",
            "### Assistant:",
        ]
    ).strip()


def _ollama_generate(prompt, options=None):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "30m",
            "options": options or OLLAMA_OPTIONS,
        },
        timeout=300,
    )
    response.raise_for_status()

    data = response.json()
    reply = _clean_content(data.get("response", ""))

    logger.info(
        "Ollama response done_reason=%s eval_count=%s prompt_eval_count=%s",
        data.get("done_reason"),
        data.get("eval_count"),
        data.get("prompt_eval_count"),
    )

    return reply, data


def ask_ai(prompt, fallback_prompt=None):
    reply, data = _ollama_generate(prompt)

    if reply:
        return reply

    logger.warning(
        "Ollama returned an empty response. done_reason=%s eval_count=%s",
        data.get("done_reason"),
        data.get("eval_count"),
    )

    retry_prompt = fallback_prompt or prompt

    for _ in range(EMPTY_RESPONSE_RETRIES):
        reply, retry_data = _ollama_generate(
            retry_prompt,
            FALLBACK_OPTIONS,
        )

        if reply:
            return reply

        logger.warning(
            "Ollama retry returned empty response. done_reason=%s eval_count=%s",
            retry_data.get("done_reason"),
            retry_data.get("eval_count"),
        )

    return (
        "I could not generate a response for that message. "
        "Please try rephrasing it."
    )


def generate_ai_reply(history):
    messages = list(history)
    _, latest_user_message = _split_history(messages)
    prompt = build_chat_prompt(messages)
    fallback_prompt = build_single_turn_prompt(latest_user_message)

    return ask_ai(
        prompt,
        fallback_prompt=fallback_prompt,
    )
