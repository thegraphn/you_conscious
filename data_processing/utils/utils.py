import csv
import os

from progressbar import *

root_folder = os.path.dirname(os.path.realpath(__file__))

root_folder = root_folder.replace(r"\data_processing\utils", "")
root_folder = root_folder.replace(r"data_processing/utils", "")

filters_file_path = os.path.join(root_folder, "utils")
filters_file_path = os.path.join(filters_file_path, "data_dependencies")
filters_file_path = os.path.join(filters_file_path, "blacklist.csv")

files_mapping_categories_path = os.path.join(root_folder, "utils")
files_mapping_categories_path = os.path.join(files_mapping_categories_path, "data_dependencies")
files_mapping_categories_path = os.path.join(files_mapping_categories_path, "categories_mapping.csv")

mapping_fashionSuitableFor = os.path.join(root_folder, "utils")
mapping_fashionSuitableFor = os.path.join(mapping_fashionSuitableFor, "data_dependencies")
mapping_fashionSuitableFor = os.path.join(mapping_fashionSuitableFor,
                                          "categoriesCleaning_fashionSuitableFor_mapping.csv")

features_mapping_path = os.path.join(root_folder, "utils")
features_mapping_path = os.path.join(features_mapping_path, "data_dependencies")
features_mapping_path = os.path.join(features_mapping_path, "features.csv")

merged_data_feed_path = os.path.join(root_folder, "data_processing")
merged_data_feed_path = os.path.join(merged_data_feed_path, "data_working_directory")
merged_data_feed_path = os.path.join(merged_data_feed_path, "merged")
merged_data_feed_path = os.path.join(merged_data_feed_path, "merged_datafeeds.csv")

filtered_data_feed_path = os.path.join(root_folder, "data_processing")
filtered_data_feed_path = os.path.join(filtered_data_feed_path, "data_working_directory")
filtered_data_feed_path = os.path.join(filtered_data_feed_path, "filtered")
filtered_data_feed_path = os.path.join(filtered_data_feed_path, "filtered_datafeed.csv")

cleansed_categories_data_feed_path = os.path.join(root_folder, "data_processing")
cleansed_categories_data_feed_path = os.path.join(cleansed_categories_data_feed_path, "data_working_directory")
cleansed_categories_data_feed_path = os.path.join(cleansed_categories_data_feed_path, "cleansed")
cleansed_categories_data_feed_path = os.path.join(cleansed_categories_data_feed_path, "cleansed_datafeed.csv")

cleansed_sex_data_feed_path = os.path.join(root_folder, "data_processing")
cleansed_sex_data_feed_path = os.path.join(cleansed_sex_data_feed_path, "data_working_directory")
cleansed_sex_data_feed_path = os.path.join(cleansed_sex_data_feed_path, "cleansed")
cleansed_sex_data_feed_path = os.path.join(cleansed_sex_data_feed_path, "cleansedSexes_datafeed.csv")

features_data_feed_path = os.path.join(root_folder, "data_processing")
features_data_feed_path = os.path.join(features_data_feed_path, "data_working_directory")
features_data_feed_path = os.path.join(features_data_feed_path, "featured")
features_data_feed_path = os.path.join(features_data_feed_path, "featured_datafeed.csv")

features_affiliateId_data_feed_path = os.path.join(root_folder, "data_processing")
features_affiliateId_data_feed_path = os.path.join(features_affiliateId_data_feed_path, "data_working_directory")
features_affiliateId_data_feed_path = os.path.join(features_affiliateId_data_feed_path, "featured")
features_affiliateId_data_feed_path = os.path.join(features_affiliateId_data_feed_path,
                                                   "featured_affiliateIds_datafeed.csv")

labeled_data_feed_path = os.path.join(root_folder, "data_processing")
labeled_data_feed_path = os.path.join(labeled_data_feed_path, "data_working_directory")
labeled_data_feed_path = os.path.join(labeled_data_feed_path, "filtered")
labeled_data_feed_path = os.path.join(labeled_data_feed_path, "labeled_data_feed.csv")


number_processes = 4

categoryName_index = 43
fashionSuitableFor_index = 25
awDeepLink_index = 42
label_index = 0
material_index = 3
search_price_index = 79
delivery_cost_index = 7
rrp_price_index = 70
maxNumberFashionSizeColumns = 100
affiliateId = "?affiliates=3"


def getMappingColumnIndex(file, delimiter):
    '''
    Create the mapping columnName: Index
    :param delimiter:
    :param file:
    :return:
    '''
    mapping = {}
    with open(file, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=delimiter)
        for row in csv_reader:
            mapping = {columnName: index for index, columnName in enumerate(row)}
            break
    return mapping


def getLinesCSV(file, delimiter):
    """
    Read a file and return the lines in a list
    :param delimiter:
    :param file:
    :return: List of lines
    """
    lines = []
    with open(file, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter=delimiter)
        for j, row in enumerate(csv_reader):
            lines.append(row)
    return lines


def createMappingBetween2Columns(file, column1_id, column2_id, delimiter):
    '''
    From a file create a dict in order to map 2 columns
    :param delimiter:
    :param file:
    :param column1_id:
    :param column2_id:
    :return:
    '''
    mapping = {}
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            splits = line.split(delimiter)
            mapping[splits[column1_id]] = splits[column2_id].replace("\n", "")
    return mapping


def write2File(list_articles, output_file):
    '''
    write a list to a csv file
    :param output_file:
    :param list_articles:
    :return:
    '''
    with open(output_file, "w", encoding="utf-8", newline="") as o:
        csv_writer = csv.writer(o, delimiter=",")
        for element in list_articles:
            if element is not None:
                csv_writer.writerow(element)


