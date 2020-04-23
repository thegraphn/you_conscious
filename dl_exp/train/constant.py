import csv
import os

import numpy as np
from sklearn.metrics import precision_score, recall_score  # type: ignore

MAX_LENGTH_TEXT = 100
EMBEDDING_LENGTH = 300
batch_size = 200
number_epochs = 1
units = 128

if False:
    l = []
    with open(
            "/home/aurelien/privat_repositories/you_conscious/dl_exp/data/data_feed-issues-200418.csv",
            "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=";")
        for row in csv_reader:
            text = " ".join([row[2]] + [row[3]])
            l.append([text])
    with open("/home/aurelien/privat_repositories/you_conscious/dl_exp/data/tobe_pred_data_set.csv","w",encoding="utf-8") as o:
        csv_writer = csv.writer(o)
        for a in l:
            csv_writer.writerow(a)


if True:
    list_true_label = []
    with open("/home/aurelien/privat_repositories/you_conscious/dl_exp/data/data_feed-issues-200418.csv","r",encoding="utf-8") as f:
        csv_reader = csv.reader(f,delimiter=";")
        for row in csv_reader:
            list_true_label.append(row[0])
    list_pred_label = []
    with open("/home/aurelien/privat_repositories/you_conscious/dl_exp/data/test_pred1.txt","r",encoding="utf-8") as f:
        csv_reader = csv.reader(f,delimiter="\t")
        for row in csv_reader:
            list_pred_label.append(row[0])

    def compute_recall(list_true_label: list, list_pred_label: list) -> float: # pylint: disable=no-self-use

        """
        Based on predicted label and correct label compute recall and
        return the result
        """

        return recall_score(np.array(list_true_label), np.array(list_pred_label), average="macro")

    def compute_precision( list_true_label: list, list_pred_label: list) -> float:  # pylint: disable=no-self-use
        """
        Based on predicted label and correct label compute precision and
        return the result
        """
        return precision_score(np.array(list_true_label), np.array(list_pred_label), average="macro")
    print(len(list_pred_label),len(list_true_label))
    c = 0
    for true,pred in zip(list_true_label,list_pred_label):
        print(true,"+",pred)
        if true==pred:
            c+=1
    print(c,len(list_pred_label))