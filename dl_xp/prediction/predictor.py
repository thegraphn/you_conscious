from text_classification.main_category_de.data_utils.data_utils import DataLoaderCsvTextClassification
from text_classification.main_category_de.utils.utils import load_model, load_model_dependencies


class Predictor:
    def __init__(self, model_path: str, model_path_dependencies: bool, data_path: str, batch_size: int):
        self.model_path: str = model_path
        self.model_path_dependencies = model_path_dependencies
        self.data_path = data_path
        self.batch_size = batch_size

        """
        prepare data in order to be predicted
        """

        self.data_loader: DataLoaderCsvTextClassification = DataLoaderCsvTextClassification(
            input_path=self.data_path,
        )
        self.data_set = self.data_loader.load_data_set_prediction()
        self.model = load_model(self.model_path)
        if self.model_path_dependencies:
            self.word2id, self.id2label = load_model_dependencies(self.model_path)
        for e, element in enumerate(self.data_set):
            for t, token in enumerate(element):
                if token not in self.word2id:
                    element[t] = 0
                else:
                    element[t] = self.word2id[token]
            self.data_set[e] = element

    def create_batches(self, list_sentences: list, batch_size: int) -> list:
        return [list_sentences[i:i + batch_size] for i in range(0, len(list_sentences), batch_size)]

    def _predict(self, input_text: list):
        prediction = self.model.predict(input_text)
        prediction = prediction[0]
        return prediction
