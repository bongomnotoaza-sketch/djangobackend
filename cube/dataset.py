import json
from pathlib import Path

import torch
from torch.utils.data import Dataset

from tokenizers import Tokenizer


TRAIN_FILE = Path("data/processed/train.jsonl")
TOKENIZER_FILE = Path("tokenizer/tokenizer.json")

CONTEXT_LENGTH = 512


class ConversationDataset(Dataset):

    def __init__(
        self,
        data_file: Path,
        tokenizer_file: Path,
        context_length: int = 512,
    ):
        
        data_file = Path(data_file)
        tokenizer_file = Path(tokenizer_file)
    
        self.context_length = context_length

        self.tokenizer = Tokenizer.from_file(
            str(tokenizer_file)
        )

        self.pad_id = self.tokenizer.token_to_id(
            "<pad>"
        )

        self.bos_id = self.tokenizer.token_to_id(
            "<bos>"
        )

        self.eos_id = self.tokenizer.token_to_id(
            "<eos>"
        )

        self.user_id = self.tokenizer.token_to_id(
            "<user>"
        )

        self.assistant_id = self.tokenizer.token_to_id(
            "<assistant>"
        )

        self.samples = []

        print(f"Loading: {data_file}")

        with data_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                record = json.loads(line)

                messages = record.get(
                    "messages",
                    []
                )

                token_ids = self.encode_conversation(
                    messages
                )

                if len(token_ids) < 2:
                    continue

                # Split long conversations into
                # context-length chunks.
                for start in range(
                    0,
                    len(token_ids),
                    context_length,
                ):

                    chunk = token_ids[
                        start:start + context_length
                    ]

                    if len(chunk) < 2:
                        continue

                    self.samples.append(chunk)

        print(
            f"Training samples: {len(self.samples):,}"
        )

    def encode_conversation(self, messages):

        token_ids = [
            self.bos_id
        ]

        for message in messages:

            role = message["role"]
            content = message["content"]

            if role == "user":

                token_ids.append(
                    self.user_id
                )

            elif role == "assistant":

                token_ids.append(
                    self.assistant_id
                )

            else:
                continue

            encoded = self.tokenizer.encode(
                content
            )

            token_ids.extend(
                encoded.ids
            )

        token_ids.append(
            self.eos_id
        )

        return token_ids

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):

        tokens = self.samples[index]

        input_ids = tokens[:-1]
        labels = tokens[1:]

        # Pad to context length - 1.
        padding_length = (
            self.context_length
            - 1
            - len(input_ids)
        )

        if padding_length > 0:

            input_ids = (
                input_ids
                + [self.pad_id] * padding_length
            )

            labels = (
                labels
                + [-100] * padding_length
            )

        else:

            input_ids = input_ids[
                :self.context_length - 1
            ]

            labels = labels[
                :self.context_length - 1
            ]

        return {
            "input_ids": torch.tensor(
                input_ids,
                dtype=torch.long,
            ),
            "labels": torch.tensor(
                labels,
                dtype=torch.long,
            ),
        }