# -*- coding: utf-8 -*-

""" Prepare input data so that it can be used by a Pytorch model """

from typing import List

import pandas as pd
from torch.utils.data import DataLoader
from datasets import Dataset
from transformers import DistilBertTokenizer


class PredictionDataPreparer:
    """ Data Preparer class """

    def __init__(self, tokenizer: DistilBertTokenizer, max_length: int, batch_size: int):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.batch_size = batch_size

    def tokenize(self, row):
        """Tokenize a text based with self.tokenizer"""
        return self.tokenizer(
            row['input_text'],
            padding='max_length',
            truncation=True,
            max_length=self.max_length
        )

    def prepare(self, inpt: List[str]):
        """ Converts list of input texts to dataloader object """

        dataset = Dataset.from_pandas(pd.DataFrame({'input_text': inpt}))
        tokenized = dataset.map(self.tokenize, batched=True).remove_columns(['input_text'])
        tokenized.set_format('torch')

        return DataLoader(
            tokenized,
            shuffle=False,
            batch_size=self.batch_size,
            drop_last=False)