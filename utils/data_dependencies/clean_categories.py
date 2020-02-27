from utils import getColumnIndex,getContentColumn,writeFile
import sys
from collections import Counter
from nltk import word_tokenize
import csv
csv_file = "datafeed.csv"
index_Sex = getColumnIndex(csv_file,"Fashion:suitable_for",",")
index_titel = getColumnIndex(csv_file,"Title",",")
index_description = getColumnIndex (csv_file,"description",",")
index_category = getColumnIndex(csv_file,"category_name",",")

def createMapping(csv_file):
    mapping = {}
    with open(csv_file,encoding="utf-8") as f:
        csv_reader = csv.reader(f,delimiter =";")
        for row in csv_reader:
            mapping[row[2]] = row[6]
    return mapping

mapping = createMapping("/Users/ConnyContini/Downloads/backend_backup_2019-4-29/utils/category/categoriesCleaning_mapping.csv")
output_csv_file = "/Users/ConnyContini/Downloads/DF_recategorized.csv"
with open(csv_file,encoding="utf-8") as f:
    with open(output_csv_file,'w',encoding="utf-8") as o:
        csv_writer = csv.writer(o)
        csv_reader = csv.reader(f)
        for row in csv_reader:
            sexe = row[index_Sex]
            words_title = word_tokenize(row[index_titel])
            for word in words_title:
                for k,v in mapping.items():
                    if word == k:
                        row[index_category] = v
                        cat = row[index_category].split(" > ")
                        if len(cat)!=0:
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

            row[index_category] = cat
            csv_writer.writerow(row)