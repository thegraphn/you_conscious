import tokenizer


class PreProcessing:
    def __init__(self, data_set: list):
        self.data_set = data_set
        self.word2id, self.label2id = self.create_x2id(self.data_set)

    @staticmethod
    def create_x2id(data_set):
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
            set_labels.add(label)
            for token in tokens:
                set_words.add(token)
        for word in set_words:
            word2id[word] = len(word2id)
        for label in set_labels:
            label2id[label] = len(label2id)
        return word2id, label2id

    @staticmethod
    def data_set_2_matrices(data_set: list, word2id: dict, label2id: dict) -> list:
        for e, element in enumerate(data_set):
            text: list = element[0]
            label: list = element[1]
            for t, token in enumerate(text):
                text[t] = word2id[token]
            element[0] = text
            element[1] = label2id[label]
        return data_set
