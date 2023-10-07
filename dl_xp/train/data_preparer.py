""" Load data from GCS and prepare it for training and evaluation """

import glob
import logging
import os
import numpy as np
import pickle
import pandas as pd
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import DataLoader
from datasets import Dataset


class DataPreparer:  # pylint:disable=R0902
    """ Download & prepare data for training and evaluation"""

    def __init__(self,
                 config: dict,
                 model_name: str):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.id2label = None

    @staticmethod
    def load_file(filename: str, split):
        """Load a file from GCS with pandas"""
        data = pd.read_csv(
            filename, delimiter=split, usecols=['text', 'label'], low_memory=False).\
            rename(columns={'label': 'labels'})
        return data[['labels', 'text']]

    @staticmethod
    def get_id2label(train, dev, test):
        """Get the mapping between the id and the label"""
        id2label = dict(enumerate(
            sorted(list(set(train['labels'].unique().tolist() +
                            dev['labels'].unique().tolist() +
                            test['labels'].unique().tolist())))))
        return id2label

    @staticmethod
    def replace_label_by_id(data_set: pd.DataFrame, mapping: pd.DataFrame):
        """Map the id to the label"""
        data_set = data_set.join(
            mapping.set_index('labels'),
            on='labels',
            sort=False)[['id', 'text']]
        data_set.columns = ['labels', 'text']
        return data_set.reset_index(drop=True)

    def tokenize(self, row):
        """Tokenize a text based with self.tokenizer"""
        return self.tokenizer(
            row["text"],
            padding="max_length",
            truncation=True,
            max_length=self.config.get('MAX_LENGTH')
        )

    def store_data_locally(self, name_data: dict):
        """Save all the data locally"""
        self.logger.info("Start: store_data_locally")
        if not os.path.exists(self.config['DIR_DATA_SET_PREPARED']):
            os.makedirs(self.config['DIR_DATA_SET_PREPARED'])
        for name, data in name_data.items():
            data_path = os.path.join(self.config["DIR_DATA_SET_PREPARED"], name)
            with open(data_path, 'wb') as file_handler:
                pickle.dump(data, file_handler)
                self.logger.info(f"Data {data_path} stored locally")
        self.logger.info("Finished: store_data_locally")

    def store_data_to_cloud_storage(self, version_id: str):
        """Upload the prepared data to google cloud storage"""
        gcs_destination = f"{self.pytorch_prefix}/{version_id}_"

        self.logger.info(f"Start: store dataloaders under {gcs_destination} "
                         f"in bucket {self.client_data.bucket.name}")
        files = glob.glob(f"{self.config['DIR_DATA_SET_PREPARED']}/*")
        for file in tqdm(files):
            gcs_destination_file = f"{gcs_destination}{os.path.basename(file)}"
            self.client_data.upload_file(file, gcs_destination_file)
            self.logger.info(f"File {file} uploaded to {gcs_destination_file}")
        self.logger.info(f"Finished to upload {len(files)} files to {gcs_destination}")
        return gcs_destination

    def prepare(self):
        """Prepare data for train set"""


        data_frame = pd.read_csv(
            self.config["LOCAL_CSV_PATH"],
            delimiter=self.config.get('DELIMITER'),
            low_memory=False
        )[0:1000]
        # keep only features of interest from config
        data_frame = data_frame[self.config.get('INPUT_FEATURES') + [self.config.get('TARGET_FEATURE')]]
        data_frame = data_frame.rename(columns={self.config.get('TARGET_FEATURE'): 'labels'})
        # concatenate features of interest
        # convert float to string
        data_frame[self.config.get('INPUT_FEATURES')] = data_frame[self.config.get('INPUT_FEATURES')].astype(str)
        data_frame['text'] = data_frame[self.config.get('INPUT_FEATURES')].apply(lambda x: ' '.join(x), axis=1)

        # split data into train, dev and test with stratified sampling 70 / 15 / 15
        train, dev, test = np.split(
            data_frame.sample(frac=1, random_state=42),
            [int(.7 * len(data_frame)), int(.85 * len(data_frame))])

        self.logger.info('Create label2id mapping.')
        self.id2label = self.get_id2label(train, dev, test)

        id_to_label_df = pd.DataFrame.from_dict(self.id2label, orient='index'). \
            drop_duplicates().reset_index(drop=False)
        id_to_label_df.columns = ['id', 'labels']
        id_to_label_df['id'] = id_to_label_df['id'].astype(int)
        self.logger.info(f'Number of labels: {len(self.id2label)}')

        self.logger.info('Replace labels by their ids.')
        train = self.replace_label_by_id(train, id_to_label_df)
        dev = self.replace_label_by_id(dev, id_to_label_df)
        test = self.replace_label_by_id(test, id_to_label_df)

        self.logger.info('Convert pd.DataFrames to pytorch Datasets.')
        train = Dataset.from_pandas(train, split='train')
        dev = Dataset.from_pandas(dev, split='validation')
        test = Dataset.from_pandas(test, split='test')

        self.logger.info('Tokenize the data.')
        train_tokenized = train.map(self.tokenize, batched=True).remove_columns(["text"])
        dev_tokenized = dev.map(self.tokenize, batched=True).remove_columns(["text"])
        test_tokenized = test.map(self.tokenize, batched=True).remove_columns(["text"])
        self.tokenizer.save_pretrained(self.config["DIR_MODEL"])

        self.logger.info('Set torch format for tokenized data.')
        train_tokenized.set_format("torch")
        dev_tokenized.set_format("torch")
        test_tokenized.set_format("torch")

        self.logger.info('Convert the Datasets to DataLoader')
        train_dataloader = DataLoader(
            train_tokenized,
            shuffle=True,
            batch_size=self.config.get('BATCH_SIZE_TRAIN'))
        dev_dataloader = DataLoader(
            dev_tokenized,
            shuffle=True,
            batch_size=self.config.get('BATCH_SIZE_DEV'))
        test_dataloader = DataLoader(
            test_tokenized,
            shuffle=False,
            batch_size=self.config.get('BATCH_SIZE_TEST'),
            drop_last=False)

        self.logger.info('Load the model from local and update its label2id attribute.')
        model = AutoModelForSequenceClassification.from_pretrained(self.config["PYTORCH_BASE_MODEL"])
        model.config.num_labels = len(self.id2label)
        model.config.id2label = self.id2label
        model.config.label2id = {v: k for k, v in self.id2label.items()}

        self.logger.info('Save the updated model locally again.')
        model.save_pretrained(self.config["DIR_MODEL"], ignore_mismatched_sizes=True)
        return train_dataloader, dev_dataloader, test_dataloader