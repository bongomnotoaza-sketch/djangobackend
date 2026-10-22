from pathlib import Path

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace


TRAIN_FILE = Path("data/processed/train.jsonl")
TOKENIZER_DIR = Path("tokenizer")

VOCAB_SIZE = 16_384


SPECIAL_TOKENS = [
    "<pad>",
    "<unk>",
    "<bos>",
    "<eos>",
    "<user>",
    "<assistant>",
]


def conversation_iterator():

    with TRAIN_FILE.open("r", encoding="utf-8") as file:

        for line in file:

            # We don't need the JSON structure here.
            # Extracting content directly keeps tokenizer training simple.
            import json

            record = json.loads(line)

            for message in record["messages"]:

                content = message["content"]

                yield content


def main():

    print("=" * 70)
    print("Training CUBE tokenizer")
    print("=" * 70)

    print()
    print(f"Training data: {TRAIN_FILE}")
    print(f"Vocabulary size: {VOCAB_SIZE:,}")

    tokenizer = Tokenizer(
        BPE(
            unk_token="<unk>"
        )
    )

    tokenizer.pre_tokenizer = Whitespace()

    trainer = BpeTrainer(
        vocab_size=VOCAB_SIZE,
        special_tokens=SPECIAL_TOKENS,
        min_frequency=2,
    )

    print()
    print("Training tokenizer...")

    tokenizer.train_from_iterator(
        conversation_iterator(),
        trainer=trainer,
    )

    TOKENIZER_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = TOKENIZER_DIR / "tokenizer.json"

    tokenizer.save(str(output_file))

    print()
    print("=" * 70)
    print("Tokenizer training complete")
    print("=" * 70)

    print(f"Saved to: {output_file}")
    print(f"Vocabulary: {tokenizer.get_vocab_size():,}")

    print()
    print("Test:")
    
    test_text = "Hello! How are you doing today?"

    encoded = tokenizer.encode(test_text)

    print("Text:")
    print(test_text)

    print()
    print("Tokens:")
    print(encoded.tokens)

    print()
    print("Token IDs:")
    print(encoded.ids)


if __name__ == "__main__":
    main()