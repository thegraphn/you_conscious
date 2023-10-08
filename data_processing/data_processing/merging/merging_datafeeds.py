import pandas as pd
from data_processing.data_processing.cleansing_datafeed.utils import mapping_to_utf
import glob
import os
import datetime
import sys
from multiprocessing import Pool
import tqdm
from data_processing.data_processing.utils.columns_order import column_ord
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/merging_datafeeds", "")
folder = folder.replace(r"\data_processing\merging_datafeeds", "")
sys.path.append(folder)
from data_processing.data_processing.utils.utils import download_data_feeds_directory_path, \
    column_mapping_merging_path, merged_data_feed_path, shops_ids_names_path, create_mapping_between_2_columns, \
    get_lines_csv, write_2_file

begin = datetime.datetime.now()


class FilesAggregator:
    def __init__(self, input_directory: str):
        self.input_directory: str = input_directory
        self.mapping_column_names: dict = create_mapping_between_2_columns(column_mapping_merging_path, 0, 1, ";")
        self.shop_id_name_mapping = self.get_mapping_2_columns(shops_ids_names_path, "merchant_name", "id")

    def change_column_names(self, list_files: list):
        with Pool() as p:
            list(tqdm.tqdm(p.imap(self.change_column_name, list_files),
                           total=len(list_files)))

    @staticmethod
    def get_column_2_index(data_path, sep):
        df_s_i_n = pd.read_csv(data_path, sep=sep, low_memory=False)
        columns = df_s_i_n.columns.values
        return {shop: index for index, shop in enumerate(columns)}

    @staticmethod
    def get_mapping_2_columns(data_path, column_1, column_2):
        df_s_i_n = pd.read_csv(data_path, sep=";", low_memory=False)
        column_1 = df_s_i_n[column_1].tolist()
        column_2 = df_s_i_n[column_2].tolist()
        return {one: two for one, two in zip(column_1, column_2)}

    def change_program_id_2_merchant_name(self, csv_file):
        # def program_id_2_merchant_name(merchant_name):
        #    return merchant_name.replace(self.shop_id_name_mapping, self.shop_id_name_mapping[merchant_name])
        df = pd.read_csv(csv_file, sep=",", low_memory=False, encoding="utf-8")
        # todo with multi processing
        merchant_names_frame = df["merchant_name"].tolist()
        # with Pool(processes=16) as p:
        #    merchant_names_frame: list = list(
        #        tqdm.tqdm(p.imap(program_id_2_merchant_name, merchant_names_frame),
        #                  total=len(merchant_names_frame), desc=csv_file+" change_program_id_2_merchant_name"))
        df["merchant_name"].replace(self.shop_id_name_mapping)
        df["merchant_name"] = merchant_names_frame
        df.to_csv(csv_file, sep="\t")

    def change_column_name(self, csv_file, mapping_file):
        dict_mapping_column = self.get_mapping_2_columns(mapping_file, "from", "to")
        sep = ","
        if "ETHLETIC" in csv_file:
            sep = ";"
        if "LOVECO" in csv_file:
            sep = "	"
        if "muso" in csv_file:
            sep = ";"


        df = pd.read_csv(csv_file, sep=sep, low_memory=False)
        df = df.rename(columns=dict_mapping_column)
        df.to_csv(csv_file + "change.csv", sep=",")


def merge_csv(list_files, fieldnames, output_data):
    # todo multiprocessing
    frames = [pd.read_csv(file, sep=",", low_memory=False) for file in list_files]
    columns_frame = pd.DataFrame(columns=column_ord)
    frames.append(columns_frame)
    merged_frames = pd.concat(frames)
    merged_frames.to_csv(output_data, sep=",")


def merging():
    file_aggregator = FilesAggregator(download_data_feeds_directory_path)
    logging.info("Begin merging")
    list_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*.csv"))
    logging.info("Merging - Changing column names: Begin")
    for file in tqdm.tqdm(list_files, total=len(list_files), desc="Aggregating files"):
        print(file)
        file_aggregator.change_column_name(file, column_mapping_merging_path)
    logging.info("Merging - Changing column names: Done")
    logging.info("Merging - Merging : Begin")
    list_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*.csvchange.csv"))
    merge_csv(list_files, column_ord, merged_data_feed_path)
    os.system("rm " + os.path.join(download_data_feeds_directory_path, "*.csvchange.csv"))
    logging.info("Merging - Merging : Done")
    logging.info("Merging - Changing ID to Name: Begin")
    file_aggregator.change_program_id_2_merchant_name(merged_data_feed_path)
    logging.info("Merging - Changing ID to Name: Done")

    df_merged = pd.read_csv(merged_data_feed_path, sep="\t", low_memory=False)
    df_merged.replace(to_replace=mapping_to_utf)
    df_merged = df_merged[column_ord]
    df_merged.to_csv(merged_data_feed_path, sep="\t")

    logging.info("Merging: Done ")
