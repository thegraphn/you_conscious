import os, sys

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/utils/data_dependencies", "")
sys.path.append(folder)
import csv
from data_processing.utils.utils import getMappingColumnIndex

from nltk import word_tokenize

csv_file = "/Volumes/home/YouConscious/YouConscious/it/data_checking/labeled_data_feed_1.csv"
index_Sex = getMappingColumnIndex(csv_file, ",")["Fashion:suitable_for"]
index_titel = getMappingColumnIndex(csv_file, ",")["Title"]
index_description = getMappingColumnIndex(csv_file, ",")["description"]
index_category = getMappingColumnIndex(csv_file, ",")["category_name"]


def createMapping(csv_file):
    mapping = {}
    with open(csv_file, encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=";")
        for row in csv_reader:
            mapping[row[2]] = row[6]
    return mapping


mapping = createMapping(
    "/Users/ConnyContini/repositories/you_conscious/utils/data_dependencies/categoriesCleaning_fashionSuitableFor_mapping.csv")
output_csv_file = "/Volumes/home/YouConscious/YouConscious/it/data_checking/datafeed_cleaned_categories.csv"
with open(csv_file, encoding="utf-8") as f:
    with open(output_csv_file, 'w', encoding="utf-8") as o:
        csv_writer = csv.writer(o)
        csv_reader = csv.reader(f)
        for row in csv_reader:
            sexe = row[index_Sex]
            words_title = word_tokenize(row[index_titel])
            for word in words_title:
                for k, v in mapping.items():
                    if word == k:
                        row[index_category] = v
                        cat = row[index_category].split(" > ")
                        if len(cat) != 0:
                            cat[1] = row[index_Sex]
                            if cat[1] == "" or cat[1] == " ":
                                cat[1] = "Damen"
                            cat = " > ".join(cat)
                            cat = cat.replace("female", "Damen")
                            cat = cat.replace("Female", "Damen")
                            cat = cat.replace("male", "Herren")
                            cat = cat.replace("Male", "Herren")
                            break
                    else:
                        cat = row[index_category]

            row[index_category] = cat
            csv_writer.writerow(row)
