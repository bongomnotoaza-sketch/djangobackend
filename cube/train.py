from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from dataset import ConversationDataset
from model.transformer import CubeTransformer


# ============================================================
# Configuration
# ============================================================

TRAIN_FILE = Path("data/processed/train.jsonl")
VAL_FILE = Path("data/processed/validation.jsonl")
TOKENIZER_FILE = Path("tokenizer/tokenizer.json")

CHECKPOINT_DIR = Path("checkpoints")
RESUME_CHECKPOINT = CHECKPOINT_DIR / "best.pt"

VOCAB_SIZE = 16_384
CONTEXT_LENGTH = 512

EMBED_DIM = 512
NUM_LAYERS = 6
NUM_HEADS = 8
FFN_DIM = 2_048

DROPOUT = 0.1

# Keep the same conservative settings.
BATCH_SIZE = 2

GRADIENT_ACCUMULATION_STEPS = 8

LEARNING_RATE = 3e-4
WEIGHT_DECAY = 0.1

# IMPORTANT:
# This means ONE additional epoch from the checkpoint.
EPOCHS = 1

NUM_WORKERS = 0

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# Validation
# ============================================================

def evaluate(
    model,
    dataloader,
    criterion,
):

    model.eval()

    total_loss = 0.0
    batches = 0

    with torch.no_grad():

        for batch in dataloader:

            input_ids = batch["input_ids"].to(
                DEVICE
            )

            labels = batch["labels"].to(
                DEVICE
            )

            logits = model(input_ids)

            loss = criterion(
                logits.reshape(
                    -1,
                    VOCAB_SIZE,
                ),
                labels.reshape(-1),
            )

            total_loss += loss.item()
            batches += 1

    model.train()

    if batches == 0:
        return float("inf")

    return total_loss / batches


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 70)
    print("CUBE Transformer Training")
    print("=" * 70)

    print()
    print("Device:", DEVICE)

    if DEVICE.type == "cuda":
        print(
            "GPU:",
            torch.cuda.get_device_name(0)
        )

    print()
    print("Resume checkpoint:", RESUME_CHECKPOINT)

    # --------------------------------------------------------
    # Dataset
    # --------------------------------------------------------

    print()
    print("Loading training dataset...")

    train_dataset = ConversationDataset(
        data_file=TRAIN_FILE,
        tokenizer_file=TOKENIZER_FILE,
        context_length=CONTEXT_LENGTH,
    )

    print()
    print("Loading validation dataset...")

    validation_dataset = ConversationDataset(
        data_file=VAL_FILE,
        tokenizer_file=TOKENIZER_FILE,
        context_length=CONTEXT_LENGTH,
    )

    # --------------------------------------------------------
    # DataLoader
    # --------------------------------------------------------

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=False,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=False,
    )

    print()
    print(
        f"Training batches: "
        f"{len(train_loader):,}"
    )

    print(
        f"Validation batches: "
        f"{len(validation_loader):,}"
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    print()
    print("Building model...")

    model = CubeTransformer(
        vocab_size=VOCAB_SIZE,
        context_length=CONTEXT_LENGTH,
        embed_dim=EMBED_DIM,
        num_layers=NUM_LAYERS,
        num_heads=NUM_HEADS,
        ffn_dim=FFN_DIM,
        dropout=DROPOUT,
    )

    model.to(DEVICE)

    parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    print(
        f"Parameters: {parameters:,}"
    )

    # --------------------------------------------------------
    # Optimizer
    # --------------------------------------------------------

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    criterion = nn.CrossEntropyLoss(
        ignore_index=-100
    )

    # --------------------------------------------------------
    # Load checkpoint
    # --------------------------------------------------------

    if not RESUME_CHECKPOINT.exists():

        raise FileNotFoundError(
            f"Checkpoint not found: "
            f"{RESUME_CHECKPOINT}"
        )

    print()
    print("Loading checkpoint...")

    checkpoint = torch.load(
        RESUME_CHECKPOINT,
        map_location=DEVICE,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    optimizer.load_state_dict(
        checkpoint["optimizer_state_dict"]
    )

    previous_epoch = checkpoint.get(
        "epoch",
        0,
    )

    previous_validation_loss = checkpoint.get(
        "validation_loss",
        float("inf"),
    )

    print(
        f"Checkpoint epoch: "
        f"{previous_epoch}"
    )

    print(
        f"Checkpoint validation loss: "
        f"{previous_validation_loss:.4f}"
    )

    print()
    print(
        f"Continuing for "
        f"{EPOCHS} additional epoch."
    )

    # The previous best loss must be preserved.
    best_validation_loss = (
        previous_validation_loss
    )

    # --------------------------------------------------------
    # Training
    # --------------------------------------------------------

    CHECKPOINT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for epoch in range(EPOCHS):

        current_epoch = (
            previous_epoch
            + epoch
            + 1
        )

        print()
        print("=" * 70)
        print(
            f"Epoch {current_epoch}"
        )
        print("=" * 70)

        model.train()

        optimizer.zero_grad()

        running_loss = 0.0
        running_batches = 0

        for step, batch in enumerate(
            train_loader
        ):

            input_ids = batch[
                "input_ids"
            ].to(DEVICE)

            labels = batch[
                "labels"
            ].to(DEVICE)

            logits = model(
                input_ids
            )

            loss = criterion(
                logits.reshape(
                    -1,
                    VOCAB_SIZE,
                ),
                labels.reshape(-1),
            )

            # Save the ORIGINAL loss for
            # correct reporting.
            actual_loss = loss.item()

            # Scale loss for gradient accumulation.
            loss = (
                loss
                / GRADIENT_ACCUMULATION_STEPS
            )

            loss.backward()

            running_loss += actual_loss
            running_batches += 1

            should_update = (
                (step + 1)
                % GRADIENT_ACCUMULATION_STEPS
                == 0
            )

            is_last_batch = (
                step + 1
                == len(train_loader)
            )

            if should_update or is_last_batch:

                torch.nn.utils.clip_grad_norm_(
                    model.parameters(),
                    1.0,
                )

                optimizer.step()

                optimizer.zero_grad()

            if (
                step + 1
            ) % 100 == 0:

                average_loss = (
                    running_loss
                    / running_batches
                )

                print(
                    f"Step "
                    f"{step + 1:>6,}"
                    f"/{len(train_loader):,} "
                    f"| Loss: "
                    f"{average_loss:.4f}"
                )

                running_loss = 0.0
                running_batches = 0

        # ----------------------------------------------------
        # Validation
        # ----------------------------------------------------

        validation_loss = evaluate(
            model,
            validation_loader,
            criterion,
        )

        print()
        print(
            f"Validation loss: "
            f"{validation_loss:.4f}"
        )

        # ----------------------------------------------------
        # Save latest checkpoint
        # ----------------------------------------------------

        latest_checkpoint = (
            CHECKPOINT_DIR
            / "latest.pt"
        )

        torch.save(
            {
                "epoch": current_epoch,
                "model_state_dict":
                    model.state_dict(),
                "optimizer_state_dict":
                    optimizer.state_dict(),
                "validation_loss":
                    validation_loss,
            },
            latest_checkpoint,
        )

        print(
            f"Saved: {latest_checkpoint}"
        )

        # ----------------------------------------------------
        # Save best checkpoint
        # ----------------------------------------------------

        if validation_loss < best_validation_loss:

            best_validation_loss = (
                validation_loss
            )

            best_checkpoint = (
                CHECKPOINT_DIR
                / "best.pt"
            )

            torch.save(
                {
                    "epoch": current_epoch,
                    "model_state_dict":
                        model.state_dict(),
                    "optimizer_state_dict":
                        optimizer.state_dict(),
                    "validation_loss":
                        validation_loss,
                },
                best_checkpoint,
            )

            print(
                f"New best checkpoint: "
                f"{best_checkpoint}"
            )

        else:

            print(
                "Best checkpoint unchanged."
            )

    print()
    print("=" * 70)
    print("Additional training complete")
    print("=" * 70)

    print()
    print(
        f"Model is now trained through "
        f"epoch {previous_epoch + EPOCHS}."
    )


if __name__ == "__main__":
    main()