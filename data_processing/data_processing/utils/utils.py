import csv
from tokenizer import tokenize
import tqdm
from progressbar import *
import pandas as pd

root_folder = os.path.dirname(os.path.realpath(__file__))
root_folder = root_folder.replace(r"\data_processing\data_processing\utils", "")
root_folder = root_folder.replace(r"data_processing/data_processing/utils", "")

filters_black_file_path = os.path.join(root_folder, "data_processing")
filters_black_file_path = os.path.join(filters_black_file_path, "utils")
filters_black_file_path = os.path.join(filters_black_file_path, "data_dependencies")
filters_black_file_path = os.path.join(filters_black_file_path, "blacklist.csv")

filters_white_file_path = os.path.join(root_folder, "data_processing")
filters_white_file_path = os.path.join(filters_white_file_path, "utils")
filters_white_file_path = os.path.join(filters_white_file_path, "data_dependencies")
filters_white_file_path = os.path.join(filters_white_file_path, "whitelist.csv")

files_mapping_categories_path = os.path.join(root_folder, "data_processing")
files_mapping_categories_path = os.path.join(files_mapping_categories_path, "utils")
files_mapping_categories_path = os.path.join(files_mapping_categories_path, "data_dependencies")
files_mapping_categories_path = os.path.join(files_mapping_categories_path, "categories_mapping.csv")

mapping_fashionSuitableFor = os.path.join(root_folder, "data_processing")
mapping_fashionSuitableFor = os.path.join(mapping_fashionSuitableFor, "utils")
mapping_fashionSuitableFor = os.path.join(mapping_fashionSuitableFor, "data_dependencies")
mapping_fashionSuitableFor = os.path.join(mapping_fashionSuitableFor,
                                          "categoriesCleaning_fashionSuitableFor_mapping.csv")

column_mapping_merging_path = os.path.join(root_folder, "data_processing")
column_mapping_merging_path = os.path.join(column_mapping_merging_path, "utils")
column_mapping_merging_path = os.path.join(column_mapping_merging_path, "data_dependencies")
column_mapping_merging_path = os.path.join(column_mapping_merging_path, "column_mapping_merging.csv")

features_mapping_path = os.path.join(root_folder, "data_processing")
features_mapping_path = os.path.join(features_mapping_path, "utils")
features_mapping_path = os.path.join(features_mapping_path, "data_dependencies")
features_mapping_path = os.path.join(features_mapping_path, "features.csv")

download_data_feeds_directory_path = os.path.join(root_folder, "data_processing")
download_data_feeds_directory_path = os.path.join(download_data_feeds_directory_path, "data_working_directory")
download_data_feeds_directory_path = os.path.join(download_data_feeds_directory_path, "download")

merged_data_feeds_directory_path = os.path.join(root_folder, "data_processing")
merged_data_feeds_directory_path = os.path.join(merged_data_feeds_directory_path, "data_working_directory")
merged_data_feeds_directory_path = os.path.join(merged_data_feeds_directory_path, "merged")

merging_features_path = os.path.join(root_folder, "data_processing")
merging_features_path = os.path.join(merging_features_path, "utils")
merging_features_path = os.path.join(merging_features_path, "data_dependencies")
merging_features_path = os.path.join(merging_features_path, "merging_features.csv")

shops_ids_names_path = os.path.join(root_folder, "data_processing")
shops_ids_names_path = os.path.join(shops_ids_names_path, "utils")
shops_ids_names_path = os.path.join(shops_ids_names_path, "data_dependencies")
shops_ids_names_path = os.path.join(shops_ids_names_path, "shops_ids_names.csv")

merged_data_feed_path = os.path.join(root_folder, "data_processing")
merged_data_feed_path = os.path.join(merged_data_feed_path, "data_working_directory")
merged_data_feed_path = os.path.join(merged_data_feed_path, "merged")
merged_data_feed_path = os.path.join(merged_data_feed_path, "merged_datafeeds.csv")

merged_data_feed_with_IdNames_path = os.path.join(root_folder, "data_processing")
merged_data_feed_with_IdNames_path = os.path.join(merged_data_feed_with_IdNames_path, "data_working_directory")
merged_data_feed_with_IdNames_path = os.path.join(merged_data_feed_with_IdNames_path, "merged")
merged_data_feed_with_IdNames_path = os.path.join(merged_data_feed_with_IdNames_path,
                                                  "merged_datafeeds.csvshop_id_2_name.csv")

merged_data_feed_utf_path = os.path.join(root_folder, "data_processing")
merged_data_feed_utf_path = os.path.join(merged_data_feed_utf_path, "data_working_directory")
merged_data_feed_utf_path = os.path.join(merged_data_feed_utf_path, "merged")
merged_data_feed_utf_path = os.path.join(merged_data_feed_utf_path,
                                         "merged_datafeeds_utf.csv")

cleansed_categories_data_feed_path = os.path.join(root_folder, "data_processing")
cleansed_categories_data_feed_path = os.path.join(cleansed_categories_data_feed_path, "data_working_directory")
cleansed_categories_data_feed_path = os.path.join(cleansed_categories_data_feed_path, "cleansed")
cleansed_categories_data_feed_path = os.path.join(cleansed_categories_data_feed_path, "cleansed_datafeed.csv")

features_data_feed_path = os.path.join(root_folder, "data_processing")
features_data_feed_path = os.path.join(features_data_feed_path, "data_working_directory")
features_data_feed_path = os.path.join(features_data_feed_path, "featured")
features_data_feed_path = os.path.join(features_data_feed_path, "featured_datafeed.csv")

cleaning_categories_fashionSuitableFor_path: str = os.path.join(root_folder, "data_processing")
cleaning_categories_fashionSuitableFor_path: str = os.path.join(cleaning_categories_fashionSuitableFor_path,
                                                                "utils")
cleaning_categories_fashionSuitableFor_path: str = os.path.join(cleaning_categories_fashionSuitableFor_path,
                                                                "data_dependencies")
cleaning_categories_fashionSuitableFor_path: str = os.path.join(cleaning_categories_fashionSuitableFor_path,
                                                                "categoriesCleaning_fashionSuitableFor_mapping.csv")


def get_mapping_column_index(file, delimiter) -> dict:
    """
    Create the mapping columnName: Index
    :param delimiter:
    :param file:
    :return: dictionary: columnName: index
    """
    mapping = {}
    with open(file, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=delimiter)
        for row in csv_reader:
            mapping = {columnName: index for index, columnName in enumerate(row)}
            break
    return mapping


def get_lines_csv(file, delimiter) -> list:
    """
    Read a file and return the lines in a list
    :param delimiter:
    :param file:
    :return: List of lines
    """
    lines = []
    with open(file, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=delimiter)
        csv.field_size_limit(100100000000)
        for j, row in tqdm.tqdm(enumerate(csv_reader), desc="Getting lines of " + file):
            lines.append(row)
    return lines


def create_mapping_between_2_columns(file, column1_id, column2_id, delimiter):
    """
    From a file create a dict in order to map 2 columns
    :param delimiter:
    :param file:
    :param column1_id:
    :param column2_id:
    :return:
    """
    mapping = {}
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            splits = line.split(delimiter)
            mapping[splits[column1_id]] = splits[column2_id].replace("\n", "")
    return mapping


def write_2_file(list_articles, output_file, delimiter: str = "\t"):
    """
    write a list to a csv file
    :param delimiter:
    :param output_file:
    :param list_articles:
    """
    with open(output_file, "w", encoding="utf-8", newline="") as o:
        csv_writer = csv.writer(o, delimiter=delimiter)
        for element in list_articles:
            if element is not None:
                csv_writer.writerow(element)


def change_delimiter_csv(csv_input: str, csv_output: str, delimiter_input: str, delimiter_output: str):
    """
    Change the format of the csv file 
    """
    input_rows: list = []
    with open(csv_input, "r", encoding="utf-8") as ic:
        csv_reader = csv.reader(ic, delimiter=delimiter_input)
        for row in csv_reader:
            input_rows.append(row)
    with open(csv_output, "w", encoding="utf-8", newline="") as oc:
        csv_writer = csv.writer(oc, delimiter=delimiter_output, quoting=csv.QUOTE_ALL)
        for element in tqdm.tqdm(input_rows):
            csv_writer.writerow(element)


def get_tokens(text: str) -> list:
    list_tokens = []
    for token in tokenize(text):
        _, tkn, _ = token
        if tkn is not None:
            list_tokens.append(tkn)
    return list_tokens


def rename_column(file: str, sep: str, column_input: str, column_target: str):
    df = pd.read_csv(file, sep=sep)
    print(df.head())
    mapping = {column_input: column_target}
    df.rename(columns=mapping, inplace=False)
    return df


number_processes = os.cpu_count()

mapping_cleaning_fashionSuitableFor = create_mapping_between_2_columns(cleaning_categories_fashionSuitableFor_path,
                                                                       2, 6,
                                                                       ";")

awDeepLink_index = 42

maxNumberFashionSizeColumns = 100
affiliateId = "?affiliates=3"

synonym_female = ["female", "weiblich", "damen", "Female", "Weiblich", "Damen"]
synonym_male = ["male", "Male", "Herren", "Man", "männlich"]
synonym_euro = ["€", "EUR"]
