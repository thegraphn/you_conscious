import logging
from pathlib import Path

from farm.data_handler.data_silo import DataSilo
from farm.data_handler.processor import TextClassificationProcessor
from farm.modeling.optimization import initialize_optimizer
from farm.infer import Inferencer
from farm.modeling.adaptive_model import AdaptiveModel
from farm.modeling.language_model import LanguageModel
from farm.modeling.prediction_head import MultiLabelTextClassificationHead
from farm.modeling.tokenization import Tokenizer
from farm.train import Trainer
from farm.utils import set_all_seeds, MLFlowLogger, initialize_device_settings
import pandas as pd
import csv

basic_texts = []
with open("/home/graphn/repositories/you_conscious/cli/colors.csv", "r", encoding="utf-8") as o:
    csv_reader = csv.reader(o)
    for row in csv_reader:
        basic_texts.append({"text": row[0]})
label_list = []
with open("/home/graphn/repositories/you_conscious/dl_xp/data/colour/colors.csv", "r", encoding="utf-8") as f:
    csv_reader = csv.reader(f, delimiter=";")
    for row in csv_reader:
        label_list.append(row[1])
label_list = list(set(label_list))
id_2_label = {i: label for i, label in enumerate(label_list)}
save_dir = "/home/graphn/repositories/you_conscious/dl_xp/saved_models/bert-german-multi-doc-tutorial"
model = Inferencer.load(save_dir,gpu=True)
result = model.inference_from_dicts(dicts=basic_texts)
for batch in result:

    pred = batch["predictions"]
    for p in pred:
        labels = []
        for i, proba in enumerate(p["probability"]):
            if proba > 0.3:
                labels.append(id_2_label[i])
        if len(labels)==0:
            print(p["context"], labels)
