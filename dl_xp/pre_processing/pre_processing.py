import tokenizer
from tensorflow.python.keras.preprocessing.sequence import pad_sequences
import numpy as np


class PreProcessing:
    def __init__(self, data_set: list):
        self.data_set = data_set


    @staticmethod
    def create_x2id(data_set,multi_label:bool):
        """
        Create word2id and label2id
        :return: two dicts word2id and label2id
        """
        word2id: dict = {"PADDING_TOKEN": 0, "UNKNOWN_TOKEN": 1}
        label2id: dict = {"UNKNOWN_LABEL": 0}
        set_words: set = set()
        set_labels: set = set()
        for element in data_set:
            tokens, label = element
            if not multi_label:
                set_labels.add(label)
            if multi_label:
                print("XXXXXXXXXXXXXXXX")
                for lbl in label:
                    set_labels.add(lbl)
            for token in tokens:
                set_words.add(token)
        for word in set_words:
            word2id[word] = len(word2id)
        for label in set_labels:
            label2id[label] = len(label2id)
        return word2id, label2id

    @staticmethod
    def data_set_2_matrices(data_set: list, word2id: dict, label2id: dict, multi_label: bool) -> list:
        for e, element in enumerate(data_set):
            text: list = element[0]
            label: list = element[1]
            one_hot_label: list = []
            for t, token in enumerate(text):
                text[t] = word2id[token]
            element[0] = text
            if multi_label:
                for i in range(len(list(label2id.keys()))):
                    one_hot_label.append(0)
                for lbl in label:
                    one_hot_label[label2id[lbl]] = 1
                label = one_hot_label
            if not multi_label:
                label = label2id[label]

            element[1] = label
        return data_set

    @staticmethod
    def create_x_y(data_set, max_length: int):

        x_test = []
        y_test = []
        for data in data_set:
            text, label = data
            x_test.append(text)
            y_test.append(label)
        x_test = np.asarray(x_test)
        # add padding
        X_test = pad_sequences(x_test, max_length, dtype='int32', padding='post', truncating='post', value=0)
        Y_test = np.asarray(y_test)

        return X_test, Y_test
