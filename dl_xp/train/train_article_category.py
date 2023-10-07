import torch
from transformers import AutoModelForSequenceClassification

from dl_xp.train.config import config_model_category
from dl_xp.train.data_preparer import DataPreparer
from dl_xp.train.predict import Predictor
from dl_xp.train.trainor import Trainor


def main():
    trainor = Trainor(config=config_model_category)

    data_preparator = DataPreparer(
        config=config_model_category,
        model_name=config_model_category.get('PYTORCH_BASE_MODEL'))

    train_dataloader, dev_dataloader, test_dataloader = data_preparator.prepare()

    model = AutoModelForSequenceClassification.from_pretrained(
        config_model_category["DIR_MODEL"],
        ignore_mismatched_sizes=True)

    # train the model on the train and devset
    trainor.train(model, train_dataloader, dev_dataloader)

    predictor = Predictor(config=config_model_category)
    print(predictor.run(["This is a test"]))


if __name__ == "__main__":
    main()
