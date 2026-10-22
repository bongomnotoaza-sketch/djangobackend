from pathlib import Path
import json
import random
import re


INPUT_FILES = [
    Path("data/processed/daily_dialog.jsonl"),
    Path("data/processed/topical_chat.jsonl"),
]

OUTPUT_DIR = Path("data/processed")

TRAIN_FILE = OUTPUT_DIR / "train.jsonl"
VAL_FILE = OUTPUT_DIR / "validation.jsonl"

VAL_RATIO = 0.02

MIN_MESSAGES = 2
MAX_MESSAGES = 40

MIN_MESSAGE_CHARS = 1
MAX_MESSAGE_CHARS = 2000


def clean_text(text: str) -> str:
    text = text.strip()

    # Collapse repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    # Remove accidental speaker prefixes if any remain.
    text = re.sub(
        r"^(Person A|Person B)\s*:\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    return text.strip()


def load_conversations():
    conversations = []

    for input_file in INPUT_FILES:

        print(f"Loading: {input_file}")

        with input_file.open("r", encoding="utf-8") as source:

            for line in source:

                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                messages = record.get("messages")

                if not isinstance(messages, list):
                    continue

                cleaned_messages = []

                for message in messages:

                    if not isinstance(message, dict):
                        continue

                    role = message.get("role")
                    content = message.get("content")

                    if role not in {"user", "assistant"}:
                        continue

                    if not isinstance(content, str):
                        continue

                    content = clean_text(content)

                    if not content:
                        continue

                    if len(content) < MIN_MESSAGE_CHARS:
                        continue

                    if len(content) > MAX_MESSAGE_CHARS:
                        continue

                    cleaned_messages.append(
                        {
                            "role": role,
                            "content": content,
                        }
                    )

                if len(cleaned_messages) < MIN_MESSAGES:
                    continue

                if len(cleaned_messages) > MAX_MESSAGES:
                    cleaned_messages = cleaned_messages[:MAX_MESSAGES]

                # Make sure the conversation starts with the user.
                if cleaned_messages[0]["role"] != "user":
                    cleaned_messages = cleaned_messages[1:]

                if len(cleaned_messages) < MIN_MESSAGES:
                    continue

                conversations.append(
                    {
                        "messages": cleaned_messages
                    }
                )

    return conversations


def conversation_key(conversation):
    return json.dumps(
        conversation["messages"],
        ensure_ascii=False,
        sort_keys=True,
    )


def main():

    print("=" * 70)
    print("Combining conversational datasets")
    print("=" * 70)

    conversations = load_conversations()

    print()
    print(f"Before deduplication: {len(conversations):,}")

    # Remove exact duplicate conversations.
    unique = {}
    
    for conversation in conversations:
        key = conversation_key(conversation)
        unique[key] = conversation

    conversations = list(unique.values())

    print(f"After deduplication:  {len(conversations):,}")

    # Shuffle.
    random.Random(42).shuffle(conversations)

    validation_count = max(
        1,
        int(len(conversations) * VAL_RATIO)
    )

    validation = conversations[:validation_count]
    train = conversations[validation_count:]

    print()
    print(f"Training conversations:   {len(train):,}")
    print(f"Validation conversations: {len(validation):,}")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with TRAIN_FILE.open("w", encoding="utf-8") as destination:

        for index, conversation in enumerate(train):

            record = {
                "id": f"train_{index}",
                "messages": conversation["messages"],
            }

            destination.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                ) + "\n"
            )

    with VAL_FILE.open("w", encoding="utf-8") as destination:

        for index, conversation in enumerate(validation):

            record = {
                "id": f"validation_{index}",
                "messages": conversation["messages"],
            }

            destination.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                ) + "\n"
            )

    print()
    print("=" * 70)
    print("Dataset preparation complete")
    print("=" * 70)
    print(f"Train:      {TRAIN_FILE}")
    print(f"Validation: {VAL_FILE}")


if __name__ == "__main__":
    main()