# title and description
import csv
from random import shuffle


def create_data_set(input_file: str) -> list:
    data_set: list = []
    with open(input_file, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(delimiter=";")
        for row in csv_reader:
            data_set.append([row[10], row[10]])
    return data_set


list_non_vegan = []
list_vegan = []
with open("/data/train_non_vegan.csv", "r", encoding="utf-8") as f:
    csv_reader = csv.reader(f, delimiter=";")
    for r in f:
        r = r.replace("\n", "")

        list_non_vegan.append([r])

with open("/data/vegan_articles.csv", "r", encoding="utf-8") as f:
    csv_reader = csv.reader(f, delimiter=";")
    for r in f:
        r = r.replace("\n","")
        list_vegan.append([r])
data_set = []
for l in list_non_vegan:
    data_set.append(l)

for l in list_vegan:
    data_set.append(l)
with open("/data/train_data_set.csv", "w", encoding="utf-8") as o:
    csv_writer = csv.writer(o, delimiter=";")
    for r in data_set:

        csv_writer.writerow(r)

""""
with open("/home/graphn/repositories/you_conscious/dl_exp/data/non_vegan.csv", "r", encoding="utf-8") as f:
    csv_reader = csv.reader(f, delimiter=",")
    for l in csv_reader:

        list_non_vegan.append(l)

shuffle(list_non_vegan)
list_non_vegan = list_non_vegan[10:5000]
print(list_non_vegan[10])
with open("train_non_vegan.csv", "w", encoding="utf-8") as o:
    csv_writer = csv.writer(o, delimiter=";")
    for a in list_non_vegan:
        print(type(a), a)
        a[1] = "non_vegan"
        csv_writer.writerow(a)
"""
