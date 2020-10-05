import csv

csv.field_size_limit(100000000)
import glob
import os
import datetime
import sys
from multiprocessing import Pool

import tqdm

from data_processing.data_processing.utils.columns_order import column_ord

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/merging_datafeeds", "")
folder = folder.replace(r"\data_processing\merging_datafeeds", "")
sys.path.append(folder)
from data_processing.data_processing.utils.utils import download_data_feeds_directory_path, \
    column_mapping_merging_path, merged_data_feed_path, shops_ids_names_path, merged_data_feed_with_IdNames_path, \
    createMappingBetween2Columns

begin = datetime.datetime.now()
print("Merging script: Started ", begin)
enc = "utf-8"


class FilesAggregator:
    def __init__(self, input_directory: str):
        self.input_directory: str = input_directory
        self.mapping_column_names: dict = createMappingBetween2Columns(column_mapping_merging_path, 0, 1, ";")

    def change_programme_id_2_merchant_names(self, list_articles: list):
        with Pool() as p:
            list_articles = list(tqdm.tqdm(p.imap(self.change_programme_id_2_merchant_name, list_articles),
                                           total=len(list_articles)))

        return list_articles

    def change_programme_id_2_merchant_name(self):
        pass

    def change_column_name(self, csv_file):
        with open(csv_file, encoding=enc) as csv_to_rename:

            csv_reader = csv.reader(csv_to_rename, delimiter=",", quotechar='"')
            with open(csv_file + "change.csv", 'w') as output_csv:
                c = True
                csv_writer = csv.writer(output_csv, delimiter=",", quotechar='"')
                for row in csv_reader:
                    if c:
                        for key, value in self.mapping_column_names.items():
                            for i in range(len(row)):
                                if key == row[i]:
                                    row[i] = value
                        csv_writer.writerow(row)
                    else:
                        csv_writer.writerow(row)

    def change_column_names(self, list_files: list) -> list:
        with Pool() as p:
            list(tqdm.tqdm(p.imap(self.change_column_name, list_files),
                           total=len(list_files)))


def changeProgrammId2MerchentName(csv_file, shop_id_name_mapping_csv, ):
    shopId2Name = {}
    with open(shop_id_name_mapping_csv, encoding="utf-8-sig") as f:
        csv_reader_mapping = csv.reader(f, delimiter=";")
        for row in csv_reader_mapping:
            shopId2Name[row[0]] = row[1]
    with open(csv_file, encoding="utf-8") as csv_input:
        csv_reader = csv.reader(csv_input, delimiter=",", quotechar='"')
        pos_merchent_id = 0
        pos_merchant_name = 0
        for row in csv_reader:
            for i in range(len(row)):
                if "merchant_id" == row[i]:
                    pos_merchent_id = i
                if "merchant_name" == row[i]:
                    pos_merchant_name = i
            break

    with open(csv_file, encoding=enc) as input:
        csv_reader2 = csv.reader(input, delimiter=",", quotechar='"')
        with open(csv_file + "shopId2Name.csv", 'w', encoding="utf-8") as o:
            csv_writer = csv.writer(o, delimiter=",", quotechar='"')
            c = 0
            for row in csv_reader2:
                if c == 0:
                    for i in range(len(row)):
                        for key, value in shopId2Name.items():
                            if key == row[i]:
                                row[pos_merchant_name] = value
                csv_writer.writerow(row)

    print("id ", pos_merchent_id)
    print("name ", pos_merchant_name)


def change_column_name(csv_file, mapping_file):
    dict_mapping_column = {}
    print(csv_file)

    with open(mapping_file, encoding="utf-8-sig") as mapping_csv:
        csv_reader = csv.reader(mapping_csv, delimiter=";")
        for row in csv_reader:
            dict_mapping_column[row[0]] = row[1]
    with open(csv_file, encoding=enc) as csv_to_rename:

        csv_reader = csv.reader(csv_to_rename, delimiter=",", quotechar='"')
        with open(csv_file + "change.csv", 'w') as output_csv:
            c = True
            csv_writer = csv.writer(output_csv, delimiter=",", quotechar='"')
            for row in csv_reader:
                if c:
                    for key, value in dict_mapping_column.items():
                        for i in range(len(row)):
                            if key == row[i]:
                                row[i] = value
                    csv_writer.writerow(row)
                else:
                    csv_writer.writerow(row)


def merge_csv(list_files, fieldnames, output_data):
    fieldnames = list(fieldnames)
    with open(output_data, 'w', encoding=enc) as output_csv_file:
        writer = csv.DictWriter(output_csv_file, fieldnames=fieldnames, delimiter=",", quotechar='"')
        csv_writer = csv.writer(output_csv_file, delimiter=",", quotechar='"')
        csv_writer.writerow(fieldnames)
        for filename in list_files:
            with open(filename, "r", newline="") as f_in:
                reader = csv.DictReader(f_in, delimiter=",", quotechar='"')  # Uses the field names in this file
                for line in reader:
                    writer.writerow(line)


def merging():
    file_aggregator = FilesAggregator(download_data_feeds_directory_path)
    print("Begin merging")
    list_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*.csv"))
    print("Merging - Changing column names: Begin")
    for file in list_files:
        change_column_name(file, column_mapping_merging_path)
    print("Merging - Changing column names: Done")
    print("Merging - Merging : Begin")
    list_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*.csvchange.csv"))
    merge_csv(list_files, column_ord, merged_data_feed_path)
    os.system("rm " + os.path.join(download_data_feeds_directory_path, "*.csvchange.csv"))
    print("Merging - Merging : Done")
    print("Merging - Changing ID to Name: Begin")
    changeProgrammId2MerchentName(merged_data_feed_path, shops_ids_names_path)
    print("Merging - Changing ID to Name: Done")
    os.system("rm " + merged_data_feed_path)
    os.rename(merged_data_feed_with_IdNames_path, merged_data_feed_path)
    print("Merging: Done ", datetime.datetime.now())
