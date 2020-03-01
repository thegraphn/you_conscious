import os,sys
import tqdm
from data_processing.utils.utils import createMappingBetween2Columns, getMappingColumnIndex
from nltk import word_tokenize
import csv
csv_file = r"C:\Users\graphn\PycharmProjects\you_conscious\data_processing\data_working_directory\filtered" \
           r"\labeled_data_feed.csv "

index_Sex = getMappingColumnIndex(csv_file,",")["Fashion:suitable_for"]
index_title = getMappingColumnIndex(csv_file, ",")["Title"]
index_description = getMappingColumnIndex (csv_file,",")["description"]
index_category = getMappingColumnIndex(csv_file,",")["category_name"]


mapping = createMappingBetween2Columns(file=r"C:\Users\graphn\PycharmProjects\you_conscious\utils\data_dependencies"
                                            r"\categoriesCleaning_fashionSuitableFor_mapping.csv",
                                       column1_id=2, column2_id=6, delimiter=";")
output_csv_file = r"C:\Users\graphn\PycharmProjects\you_conscious\data_processing\data_working_directory\filtered" \
                  r"\cleansed_data_feed.csv "
with open(csv_file,encoding="utf-8") as f:
    with open(output_csv_file,'w',encoding="utf-8") as o:
        csv_writer = csv.writer(o)
        csv_reader = csv.reader(f)
        num_lines = sum(1 for line in open(csv_file,encoding="utf-8"))
        for row in tqdm.tqdm(csv_reader,total=num_lines):
            sexe = row[index_Sex]
            words_title = word_tokenize(row[index_title])
            for word in words_title:
                for k,v in mapping.items():
                    if word == k:
                        row[index_category] = v
                        cat = row[index_category].split(" > ")
                        if len(cat) >= index_Sex:
                            cat[1] = row[index_Sex]
                            if cat[1] == "" or cat[1] == " ":
                                cat[1] = "Damen"
                            cat = " > ".join(cat)
                            cat = cat.replace("female","Damen")
                            cat = cat.replace("Female", "Damen")
                            cat = cat.replace("male","Herren")
                            cat = cat.replace("Male", "Herren")
                            break

                    else:
                        cat = row[index_category]


            row[index_category] = str(cat)
            csv_writer.writerow(row)