from dataset import ConversationDataset


def main():

    dataset = ConversationDataset(
        data_file="data/processed/train.jsonl",
        tokenizer_file="tokenizer/tokenizer.json",
        context_length=512,
    )

    print()
    print("=" * 70)
    print("Dataset test")
    print("=" * 70)

    print("Samples:", len(dataset))

    sample = dataset[0]

    print(
        "Input shape:",
        sample["input_ids"].shape,
    )

    print(
        "Label shape:",
        sample["labels"].shape,
    )

    print()
    print("First 30 input IDs:")
    print(sample["input_ids"][:30].tolist())

    print()
    print("First 30 labels:")
    print(sample["labels"][:30].tolist())


if __name__ == "__main__":
    main()