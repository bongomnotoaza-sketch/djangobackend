from pathlib import Path
import json
import numpy as np

import pandas as pd


DAILY_DIALOG_FILE = Path(
    "data/raw/daily_dialog/data/train-00000-of-00001.parquet"
)

PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def convert_daily_dialog():
    output_file = PROCESSED_DIR / "daily_dialog.jsonl"

    print("Loading DailyDialog...")
    print(f"Input: {DAILY_DIALOG_FILE}")

    dataframe = pd.read_parquet(DAILY_DIALOG_FILE)

    print()
    print("Columns:")
    print(dataframe.columns.tolist())

    print()
    print("First record:")
    print(dataframe.iloc[0].to_dict())

    print()
    print("=" * 70)
    print("Converting DailyDialog")
    print("=" * 70)

    conversations = 0
    messages = 0

    with output_file.open("w", encoding="utf-8") as destination:

        for index, row in dataframe.iterrows():

            conversation = row["conversation"]

            if not isinstance(conversation, (list, tuple, np.ndarray)):
                continue

            messages_list = []

            for turn_index, message in enumerate(conversation):

                if not isinstance(message, str):
                    continue

                message = message.strip()

                if not message:
                    continue

                # Remove dataset speaker prefix
                if message.startswith("Person A:"):
                    message = message[len("Person A:"):].strip()

                elif message.startswith("Person B:"):
                    message = message[len("Person B:"):].strip()

                if not message:
                    continue

                role = (
                    "user"
                    if turn_index % 2 == 0
                    else "assistant"
                )

                messages_list.append(
                    {
                        "role": role,
                        "content": message,
                    }
                )

            if len(messages_list) < 2:
                continue

            converted = {
                "id": f"dailydialog_{index}",
                "messages": messages_list,
            }

            destination.write(
                json.dumps(
                    converted,
                    ensure_ascii=False
                ) + "\n"
            )

            conversations += 1
            messages += len(messages_list)

    print()
    print("=" * 70)
    print("DailyDialog conversion complete")
    print("=" * 70)
    print(f"Conversations: {conversations:,}")
    print(f"Messages:      {messages:,}")
    print(f"Output:        {output_file}")


def main():
    convert_daily_dialog()


if __name__ == "__main__":
    main()