import csv

import tokenizer


class DataLoaderCsvTextClassification:
    def __init__(self, input_path: str, position_text: int, position_label: int, input_path_delimiter: str,
                 class_delimiter: str):
        self.input_path: str = input_path
        self.position_text: int = position_text
        self.position_label: int = position_label
        self.input_path_delimiter: str = input_path_delimiter
        self.class_delimiter: str = class_delimiter

    def load_data_set(self, skip_header: bool = True) -> list:
        """
        Read the data and returns the data set
        :return: List of the texts and labels. First element in the list is the text, second is the label
        """
        data_set: list = []
        with open(self.input_path, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f, delimiter=self.input_path_delimiter)
            if skip_header:
                next(csv_reader)
            for row in csv_reader:
                tokens: list = []
                text: str = row[self.position_text]
                for token in tokenizer.tokenize(text):
                    kind, txt, val = token
                    if txt != None:
                        tokens.append(txt)
                labels: str = row[self.position_label]
                data_set.append([tokens, labels])
        return data_set
