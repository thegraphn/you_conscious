import logging
from typing import Tuple
import numpy as np
import torch
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, DistilBertConfig, AutoTokenizer

from dl_xp.train.prediction_data_preparer import PredictionDataPreparer


class Predictor:
    def __init__(self, config: dict):
        self.config = config
        self.model_dir = config.get('DIR_MODEL')
        self.device = None
        self.logger = logging.getLogger(__name__)
        self.model, self.id2label, self.tokenizer = self.load_model()
        self.data_handler = PredictionDataPreparer(
            self.tokenizer, self.model.config.max_position_embeddings, config.get('PRED_BATCH_SIZE'))

    def load_model(self) -> Tuple:
        """ load the distilbert model, its id2label mapping and its tokenizer into memory """

        id2label = DistilBertConfig.from_pretrained(self.model_dir).id2label
        model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
        self.logger.info(f"Maximum sequence length is {model.config.max_position_embeddings}")
        tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.logger.info(f"Distilbert model loaded from {self.model_dir} into memory.")

        return model, id2label, tokenizer
    def predict(self, dataloader: DataLoader):
        """
        Takes a dataloader object and returns the predictions as list of dictionaries.
        """
        self.logger.info("Applying model on the dataloader object.")
        predictions = []
        for batch in dataloader:
            # transfer test data batch to GPU
            batch = {k: v.to(self.device) for k, v in batch.items()}
            # run a forward pass with the model on the current batch
            with torch.no_grad():
                logits = self.model.forward(**batch).logits.softmax(dim=1).cpu().detach().numpy()
                # find predicted categories and their probabilities for the current batch
                predictions = predictions + self.derive_predictions_from_array(logits)
        return predictions

    def run(self, list_input: list) -> list:
        """
        Method that is called from the endpoint.
        """
        self.logger.info('Prediction service is running the KopPredictor.')

        input_texts: list = list_input

        dataloader = self.data_handler.prepare(input_texts)
        results = self.predict(dataloader)
        # take the highest probability for each product
        results = [max(result, key=result.get) for result in results]
        torch.cuda.empty_cache()

        return results
    def derive_predictions_from_array(self, arr: np.array):
        """
        Returns list of dicts from a numpy array.
        Each list item contains predictions for 1 product.
        The dictionary has kind_of_product codes as key and probabilities as value.
        """
        products = []
        for product in arr:
            preds = {}
            for idx, prob in enumerate(product):
                preds.update({self.id2label.get(idx): float(prob)})
            products.append(preds)
        return products