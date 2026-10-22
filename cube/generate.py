import torch

from model.transformer import CubeTransformer
from tokenizers import Tokenizer


# ============================================================
# Configuration
# ============================================================

CHECKPOINT = "checkpoints/best.pt"
TOKENIZER_FILE = "tokenizer/tokenizer.json"

VOCAB_SIZE = 16_384
CONTEXT_LENGTH = 512

EMBED_DIM = 512
NUM_LAYERS = 6
NUM_HEADS = 8
FFN_DIM = 2_048
DROPOUT = 0.1

MAX_NEW_TOKENS = 80
TEMPERATURE = 0.8

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# Load tokenizer
# ============================================================

tokenizer = Tokenizer.from_file(
    TOKENIZER_FILE
)

USER_ID = tokenizer.token_to_id("<user>")
ASSISTANT_ID = tokenizer.token_to_id("<assistant>")
EOS_ID = tokenizer.token_to_id("<eos>")


# ============================================================
# Load model
# ============================================================

model = CubeTransformer(
    vocab_size=VOCAB_SIZE,
    context_length=CONTEXT_LENGTH,
    embed_dim=EMBED_DIM,
    num_layers=NUM_LAYERS,
    num_heads=NUM_HEADS,
    ffn_dim=FFN_DIM,
    dropout=DROPOUT,
)

checkpoint = torch.load(
    CHECKPOINT,
    map_location=DEVICE,
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.to(DEVICE)
model.eval()

print("=" * 70)
print("CUBE Transformer")
print("=" * 70)
print("Device:", DEVICE)
print("Checkpoint:", CHECKPOINT)
print()


# ============================================================
# Generation
# ============================================================

def generate(
    message: str,
    max_new_tokens=MAX_NEW_TOKENS,
    temperature=TEMPERATURE,
):

    # Encode the user's message
    message_tokens = tokenizer.encode(
        message
    ).ids

    # Build conversation format used during training:
    #
    # <user> message <assistant>
    #
    input_ids = [
        USER_ID,
        *message_tokens,
        ASSISTANT_ID,
    ]

    generated_tokens = []

    for _ in range(max_new_tokens):

        # Keep within model context
        context = input_ids[-CONTEXT_LENGTH:]

        x = torch.tensor(
            [context],
            dtype=torch.long,
            device=DEVICE,
        )

        with torch.no_grad():

            logits = model(x)

        # Only use prediction for the final position
        logits = logits[:, -1, :]

        # Temperature
        logits = logits / temperature

        probabilities = torch.softmax(
            logits,
            dim=-1,
        )

        # Sample next token
        next_token = torch.multinomial(
            probabilities,
            num_samples=1,
        ).item()

        # Stop at EOS
        if next_token == EOS_ID:
            break

        # Stop if model starts another user turn
        if next_token == USER_ID:
            break

        generated_tokens.append(
            next_token
        )

        input_ids.append(
            next_token
        )

    # Decode only generated assistant tokens
    response = tokenizer.decode(
        generated_tokens
    )

    return response.strip()


# ============================================================
# Test prompts
# ============================================================

if __name__ == "__main__":

    prompts = [
        "Hello! How are you?",
        "What is your name?",
        "How was your day?",
        "What do you like to talk about?",
        "What is your favorite food?",
    ]

    for prompt in prompts:

        print("=" * 70)
        print("USER:", prompt)
        print()

        response = generate(prompt)

        print("ASSISTANT:", response)
        print()