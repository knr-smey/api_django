import requests

OLLAMA_URL = (
    "http://localhost:11434/api/generate"
)


def ask_ai(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False
        }
    )

    data = response.json()

    text = data.get(
        "response",
        "No response"
    )

    return text.strip()