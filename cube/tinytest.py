"""
Chat with a local Ollama model via /api/chat, with tunable generation
parameters, so you can compare behavior across settings without editing
the Modelfile each time.

Requires the Ollama server running locally (default: http://localhost:11434)
and the `requests` package: pip install requests
"""

import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:0.5b"

# ------------------------------------------------------------------
# Tune these. Start here, then adjust based on what you see.
# ------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are a helpful, concise AI assistant. "
    "Only respond to what the user actually says."
)

GENERATION_OPTIONS = {
    "temperature": 0.6,       # lower = more focused/deterministic (try 0.3-0.8)
    "top_p": 0.9,              # nucleus sampling cutoff
    "repeat_penalty": 1.1,     # mild repetition discouragement
    "num_predict": 150,        # max tokens per reply
}


def chat():
    history = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"Chatting with {MODEL} (Ctrl+C to quit)")
    print(f"Params: {GENERATION_OPTIONS}\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break

        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": history,
                "stream": False,
                "options": GENERATION_OPTIONS,
            },
        )
        response.raise_for_status()
        data = response.json()

        reply = data["message"]["content"].strip()
        print(f"\n{MODEL}: {reply}\n")

        history.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    chat()