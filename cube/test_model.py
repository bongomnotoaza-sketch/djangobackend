import torch

from model.transformer import CubeTransformer


def main():

    model = CubeTransformer()

    total_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    print("=" * 70)
    print("CUBE Transformer")
    print("=" * 70)

    print(f"Parameters: {total_parameters:,}")

    input_ids = torch.randint(
        0,
        16_384,
        (2, 32),
    )

    print()
    print("Input shape:", input_ids.shape)

    with torch.no_grad():

        logits = model(input_ids)

    print("Output shape:", logits.shape)


if __name__ == "__main__":
    main()