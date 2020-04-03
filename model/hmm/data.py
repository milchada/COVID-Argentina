import torch
import torch.utils.data
from collections import Counter
import os
from sklearn.model_selection import train_test_split


class Config:
    def __init__(self, N, path):
        self.N = N
        self.path = path


def read_config(N, path):
    config = Config(N=N, path=path)
    return config


def get_datasets(config, batch_size=32):
    path = config.path

    lines = []
    for filename in os.listdir(os.path.join(path, "train")):
        with open(os.path.join(path, "train", filename), "r") as f:
            lines_ = f.readlines()
        # lines_[-1] += '\n'
        lines += lines_

    # get input and output alphabets
    Sx = list(Counter(("".join(lines))).keys())  # set of possible output letters
    train_lines, valid_lines = train_test_split(lines, test_size=0.1, random_state=42)
    train_dataset = TextDataset(train_lines, Sx, batch_size=batch_size)
    valid_dataset = TextDataset(valid_lines, Sx, batch_size=batch_size)

    config.M = len(Sx)
    config.Sx = Sx

    return train_dataset, valid_dataset


class TextDataset(torch.utils.data.Dataset):
    def __init__(self, lines, Sx, batch_size=32):
        self.lines = lines  # list of strings
        self.Sx = Sx
        pad_and_one_hot = PadAndOneHot(
            self.Sx
        )  # function for generating a minibatch from strings
        self.loader = torch.utils.data.DataLoader(
            self,
            batch_size=batch_size,
            num_workers=0,
            shuffle=True,
            collate_fn=pad_and_one_hot,
        )

    def __len__(self):
        return len(self.lines)

    def __getitem__(self, idx):
        line = self.lines[idx].lstrip(" ").rstrip("\n").rstrip(" ").rstrip("\n")
        return line


class PadAndOneHot:
    def __init__(self, Sx):
        self.Sx = Sx

    def __call__(self, batch):
        """
        Returns a minibatch of strings, one-hot encoded and padded to have the same length.
        """
        x = []
        batch_size = len(batch)
        for index in range(batch_size):
            x_ = batch[index]
            if "\n" in x_:
                print(x_)
                sys.exit()

            # convert letters to integers
            x.append([self.Sx.index(c) for c in x_])

        # pad all sequences with 0 to have same length
        x_lengths = [len(x_) for x_ in x]
        T = max(x_lengths)
        for index in range(batch_size):
            x[index] += [0] * (T - len(x[index]))
            x[index] = torch.tensor(x[index])

        # stack into single tensor and one-hot encode integer labels
        x = torch.stack(x)  # one_hot(torch.stack(x), len(self.Sx))
        x_lengths = torch.tensor(x_lengths)

        return (x, x_lengths)
