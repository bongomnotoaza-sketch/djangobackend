import torch
import torch.nn as nn


class CausalSelfAttention(nn.Module):

    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        dropout: float = 0.1,
    ):
        super().__init__()

        if embed_dim % num_heads != 0:
            raise ValueError(
                "embed_dim must be divisible by num_heads"
            )

        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads

        self.qkv = nn.Linear(
            embed_dim,
            embed_dim * 3,
        )

        self.output = nn.Linear(
            embed_dim,
            embed_dim,
        )

        self.dropout = nn.Dropout(dropout)

        self.register_buffer(
            "mask",
            torch.tril(
                torch.ones(
                    512,
                    512,
                )
            ).view(
                1,
                1,
                512,
                512,
            ),
            persistent=False,
        )

    def forward(self, x):

        batch_size, sequence_length, _ = x.shape

        qkv = self.qkv(x)

        q, k, v = qkv.chunk(
            3,
            dim=-1,
        )

        q = q.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim,
        ).transpose(1, 2)

        k = k.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim,
        ).transpose(1, 2)

        v = v.view(
            batch_size,
            sequence_length,
            self.num_heads,
            self.head_dim,
        ).transpose(1, 2)

        attention_scores = (
            q @ k.transpose(-2, -1)
        ) / (self.head_dim ** 0.5)

        attention_scores = attention_scores.masked_fill(
            self.mask[
                :,
                :,
                :sequence_length,
                :sequence_length,
            ] == 0,
            float("-inf"),
        )

        attention_weights = torch.softmax(
            attention_scores,
            dim=-1,
        )

        attention_weights = self.dropout(
            attention_weights
        )

        output = attention_weights @ v

        output = output.transpose(
            1,
            2,
        ).contiguous()

        output = output.view(
            batch_size,
            sequence_length,
            self.embed_dim,
        )

        return self.output(output)


class FeedForward(nn.Module):

    def __init__(
        self,
        embed_dim: int,
        hidden_dim: int,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(
                embed_dim,
                hidden_dim,
            ),
            nn.GELU(),
            nn.Linear(
                hidden_dim,
                embed_dim,
            ),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.network(x)


class TransformerBlock(nn.Module):

    def __init__(
        self,
        embed_dim: int,
        num_heads: int,
        ffn_dim: int,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.norm1 = nn.LayerNorm(
            embed_dim
        )

        self.attention = CausalSelfAttention(
            embed_dim=embed_dim,
            num_heads=num_heads,
            dropout=dropout,
        )

        self.norm2 = nn.LayerNorm(
            embed_dim
        )

        self.feed_forward = FeedForward(
            embed_dim=embed_dim,
            hidden_dim=ffn_dim,
            dropout=dropout,
        )

    def forward(self, x):

        x = x + self.attention(
            self.norm1(x)
        )

        x = x + self.feed_forward(
            self.norm2(x)
        )

        return x


class CubeTransformer(nn.Module):

    def __init__(
        self,
        vocab_size: int = 16_384,
        context_length: int = 512,
        embed_dim: int = 512,
        num_layers: int = 6,
        num_heads: int = 8,
        ffn_dim: int = 2_048,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.vocab_size = vocab_size
        self.context_length = context_length

        self.token_embedding = nn.Embedding(
            vocab_size,
            embed_dim,
        )

        self.position_embedding = nn.Embedding(
            context_length,
            embed_dim,
        )

        self.dropout = nn.Dropout(
            dropout
        )

        self.layers = nn.ModuleList(
            [
                TransformerBlock(
                    embed_dim=embed_dim,
                    num_heads=num_heads,
                    ffn_dim=ffn_dim,
                    dropout=dropout,
                )
                for _ in range(num_layers)
            ]
        )

        self.final_norm = nn.LayerNorm(
            embed_dim
        )

        self.output = nn.Linear(
            embed_dim,
            vocab_size,
            bias=False,
        )

        # Weight tying.
        self.output.weight = (
            self.token_embedding.weight
        )

    def forward(self, input_ids):

        batch_size, sequence_length = input_ids.shape

        if sequence_length > self.context_length:
            raise ValueError(
                f"Sequence length {sequence_length} "
                f"exceeds context length "
                f"{self.context_length}"
            )

        positions = torch.arange(
            sequence_length,
            device=input_ids.device,
        )

        token_embeddings = self.token_embedding(
            input_ids
        )

        position_embeddings = self.position_embedding(
            positions
        )

        x = (
            token_embeddings
            + position_embeddings
        )

        x = self.dropout(x)

        for layer in self.layers:
            x = layer(x)

        x = self.final_norm(x)

        logits = self.output(x)

        return logits