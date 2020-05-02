import csv

import tokenizer


class DataLoaderCsvTextClassification:
    def __init__(self, input_path: str):
        self.input_path: str = input_path

    def load_data_set(self, skip_header: bool, input_path_delimiter: str, position_text: int, position_label: int,
                      class_delimiter: str,multi_label:bool) -> list:
        """
        Read the data and returns the data set
        :return: List of the texts and labels. First element in the list is the text, second is the label
        """
        data_set: list = []
        with open(self.input_path, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f, delimiter=input_path_delimiter)
            if skip_header:
                next(csv_reader)
            for row in csv_reader:
                tokens: list = []
                text: str = row[position_text]
                for token in tokenizer.tokenize(text):
                    kind, txt, val = token
                    if txt is not None:
                        tokens.append(txt)
                labels: str = row[position_label]
                if multi_label:
                    labels: list = labels.split(class_delimiter)
                data_set.append([tokens, labels])
        return data_set

    def load_data_set_prediction(self) -> list:
        data_set: list = []
        with open(self.input_path, "r", encoding="utf-8") as f:

            for line in f:
                tokens: list = []
                text: str = line.replace("\n","")
                for token in tokenizer.tokenize(text):
                    kind, txt, val = token
                    if txt is not None:
                        tokens.append(txt)
                data_set.append(tokens)
        return data_set
