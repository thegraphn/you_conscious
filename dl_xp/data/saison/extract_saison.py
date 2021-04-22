import pandas as pd
import csv
import math

df = pd.read_csv("/home/graphn/repositories/you_conscious/dl_xp/data/category/training_category.csv", sep=";")

list_saison = ["Winter", "Herbst", "Frühling", "Sommer"]
column_features = ["brand",
                   "merchant_name",
                   "Fashion:suitable_for",
                   "Title",
                   "description"]

training_data = []
for index, row in df.iterrows():
    labels = []
    feat = []
    title_content = row["Title"]
    description_content = row["description"]
    x = False
    if type(description_content) is not str:
        x = float(description_content)
        x = math.isnan(x)
    if x == True:
        continue

    for saison in list_saison:
        if saison in title_content or saison in description_content:
            labels.append(saison)
    labels = list(set(labels))
    if len(labels) > 0:
        for f in column_features:
            feat.append(f)
    feat = [title_content,description_content]
    feat = " [SEP] ".join(feat)
    if len(labels)>0:
        training_data.append([feat, ",".join(labels)])
with open("training_saison.csv", "w", encoding="utf-8") as o:
    csv_writer = csv.writer(o, delimiter="\t")
    csv_writer.writerow(["text","label"])
    for x in training_data:
        csv_writer.writerow(x)
