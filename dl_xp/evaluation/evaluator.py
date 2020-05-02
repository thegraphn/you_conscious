from text_classification.main_category_de.data_utils.data_utils import DataLoaderCsvTextClassification
from text_classification.main_category_de.pre_processing.pre_processing import PreProcessing
from text_classification.main_category_de.utils.utils import load_model, load_model_dependencies


class Evaluator:
    def __init__(self, model_path: str, model_path_dependencies: bool, data_set_path: str, batch_size: int,
                 csv_delimiter: str, label_delimiter: str, label_row_index: int, text_row_index: int):
        self.model_path: str = model_path
        self.model_path_dependencies = model_path_dependencies
        self.data_set_path = data_set_path
        self.batch_size = batch_size
        self.csv_delimiter = csv_delimiter
        self.label_delimiter = label_delimiter
        self.label_row_index = label_row_index
        self.text_row_index = text_row_index

        """
        Creation of all the dependencies in order to predict
        """
        self.data_loader: DataLoaderCsvTextClassification = DataLoaderCsvTextClassification(
            input_path=self.data_set_path,
            position_text=self.text_row_index,
            position_label=self.label_row_index,
            input_path_delimiter=self.csv_delimiter,
            label_delimiter=self.label_delimiter)
        self.model = load_model(self.model_path)
        if model_path_dependencies:
            self.word2id, self.id2label = load_model_dependencies(self.model_path)

        self.test_set = self.data_loader.load_data_set()
        self.pre_processor: PreProcessing = PreProcessing(self.test_set)

        self.test_set = self.pre_processor.data_set_2_matrices(self.test_set, self.pre_processor.word2id,
                                                               self.pre_processor.label2id,
                                                               multi_label=True)

        self.x_test, self.y_test = self.pre_processor.create_x_y(self.test_set, max_length=150)

    def evaluate(self, x_test, y_test):
        history = self.model.evaluate(x_test, y_test,
                                      verbose=1,
                                      batch_size=256)
        return history
