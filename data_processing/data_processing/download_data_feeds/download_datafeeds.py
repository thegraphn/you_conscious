######################################################################################
#                                                                                    #
#                                                                                    #
# Download datafeeds from their links. The links are saved into a txt. One per line. #
#                                                                                    #
#                                                                                    #
######################################################################################
import csv
import os
import sys

import tqdm

from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.utils import download_data_feeds_directory_path, \
    createMappingBetween2Columns, change_delimiter_csv

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/download_data_feeds", "")
folder = folder.replace(r"\data_processing\download_data_feeds", "")
sys.path.append(folder)
import glob
import urllib.request
import datetime
from multiprocessing import Pool


class Downloader:

    def __init__(self):
        self.datafeed_infos: list = self.get_datafeed_infos()
        print(self.datafeed_infos)

    @staticmethod
    def get_datafeed_infos() -> list:
        """
        Get the info in order to download the datafeeds properly: URL and csv_file delimiter
        :return: list [Shop_name,URL,delimiter],
                        ....
                        }
        """
        datafeed_info: list = []
        with open(file_paths["file_datafeed_location"], "r", encoding="utf-8") as input_file:
            csv_reader = csv.reader(input_file, delimiter=";")
            next(csv_reader)
            for row in csv_reader:
                datafeed_name: str = row[0]
                datafeed_url: str = row[1]
                datafeed_delimiter: str = row[2]
                datafeed_info.append([datafeed_name, datafeed_url, datafeed_delimiter])
        return datafeed_info

    @staticmethod
    def read_datafeed_url_file(file: str) -> dict:
        """
        :param file: file containing the mapping of Shops and URLS
        :return: dictionary. key:name of shop, value: url
        """
        datafeed_url_links: dict = {}

        with open(file) as f:
            csv_reader = csv.reader(f, delimiter=";")
            for row in csv_reader:
                name_shop: str = row[0]
                url: str = row[1]
                if name_shop != "Advertiser Name" and url != "URL":
                    datafeed_url_links[name_shop] = url
            return datafeed_url_links

    @staticmethod
    def add_merchant_name(in_file: str, name: str):
        """
        Only for SORBRAS
        :param in_file: datafeed file
        :param name: name to add into the data feed
        """
        headers: list = []
        with open(in_file, encoding="utf-8") as file:
            with open(os.path.join(file_paths["file_datafeed_location"],
                                   "datafeeds_preprocessing\downloaded_datafeeds/SORBAS_with_merchant_name.csv"),
                      'w',
                      encoding="utf-8") as o:
                csv_reader: csv.reader = csv.reader(file)
                csv_writer: csv.writer = csv.writer(o)
                for row in csv_reader:
                    headers = row
                    break
                headers = headers + ["merchant_name"]
                csv_writer.writerow(headers)
                for row in csv_reader:
                    row = row + [name]
                    csv_writer.writerow(row)
        os.system("rm " + in_file)

    def download_datafeeds(self, list_tuples_shops_urls: list):
        """
        This function uses Pool and call the sub-function  downloadDatafeed.
        The number of processes is set to 2 because of the internet connection.
        :param list_tuples_shops_urls: List of tuples (shop name, link)
        """
        with Pool(processes=2)as p:
            list(tqdm.tqdm(p.imap(self.download_datafeed, list_tuples_shops_urls), total=len(list_tuples_shops_urls)))

    @staticmethod
    def download_datafeed(tuple_shop_url: tuple):
        """
        Download a data feed. If the file is LOVECO, the extension of the file is immediately changed into csv
        :param tuple_shop_url: tuple containing (shop_name,url)
        """
        shop_name: str = tuple_shop_url[0]
        link: str = tuple_shop_url[1]
        shop_name = shop_name.replace(" ", "_")
        format_file: str = ""
        if "LOVECO" == shop_name:
            format_file = ".csv"
            path_file: str = os.path.join(download_data_feeds_directory_path, shop_name + "-" +
                                          datetime.datetime.now().strftime("%y-%m-%d") + format_file)
            urllib.request.urlretrieve(link, path_file)

        if "SORBAS" == shop_name:
            format_file = ".csv"
            path_file: str = os.path.join(download_data_feeds_directory_path, shop_name + "-" +
                                          datetime.datetime.now().strftime("%y-%m-%d") + format_file)
            urllib.request.urlretrieve(link, path_file)
        if "Uli_Schott" in shop_name:
            format_file = ".csv"
            path_file: str = os.path.join(download_data_feeds_directory_path, shop_name + "-" +
                                          datetime.datetime.now().strftime("%y-%m-%d") + format_file)
            urllib.request.urlretrieve(link, path_file)

        else:
            format_file = ".gz"
            path_file: str = os.path.join(download_data_feeds_directory_path, shop_name + "-" +
                                          datetime.datetime.now().strftime("%y-%m-%d") + format_file)
            urllib.request.urlretrieve(link, path_file)

    def unzip_files(self, list_files: list):
        """
        This function uses Pool and call the sub-function unzipFile
            :param list_files: List of the files to try to unzip
        """
        with Pool(processes=2)as p:
            list(tqdm.tqdm(p.imap(self.unzip_file, list_files), total=len(list_files)))

    @staticmethod
    def unzip_file(file: str):
        """
        Try to unzip a given file. If the datafeed is LOVECO the file is not zipped. It is
        just required to change the file's extension
        :param file: file to unzip
        """
        if ".csv" in file:
            pass
        if "LOVECO" in file:
            pass

        if "gz" in file and not "LOVECO" in file:
            length_to_delete: int = -3
            os.system("gunzip -kc " + str(file) + " > " + str(file[:length_to_delete]) + ".csv")

    @staticmethod
    def delete_non_csv_datafeeds(directory: str):
        """
        Delete all file in a directory except py and csv files
        :param directory: Directory where the files will be deleted
        """
        list_files: list = glob.glob(os.path.join(directory, "*"))
        for file in list_files:
            if not file.endswith("csv") and not file.endswith(".py"):
                os.system("rm " + file)

    def change_delimiters(self, list_files: list):
        with Pool()as p:
            list(tqdm.tqdm(p.imap(self.change_delimiter, list_files), total=len(list_files)))

    def change_delimiter(self, csv_file_path: str):
        """
        Uniform the delimiter in the csv files
        :param csv_file_path: csv file in which the delimiter may change
        :return:
        """
        for info in self.datafeed_infos:
            shop_name: str = info[0].replace(" ", "_")
            _: str = info[1]
            delimiter: str = info[2]
            if shop_name in csv_file_path and delimiter != ",":
                change_delimiter_csv(csv_input=csv_file_path, csv_output=csv_file_path, delimiter_input=delimiter,
                                     delimiter_output=",")


def downloading():
    downloader: Downloader = Downloader()
    downloader.delete_non_csv_datafeeds(download_data_feeds_directory_path)
    print("Downloading - Downloading data feeds: Begin")
    downloader.download_datafeeds(list_tuples_shops_urls=downloader.datafeed_infos)
    print("Downloading - Downloading data feeds: End")
    list_downloaded_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*"))
    print("Downloading - Unzipping data feeds: Begin")
    downloader.unzip_files(list_files=list_downloaded_files)
    print("Downloading - Change csv file delimiter: Begin")
    downloader.change_delimiters(list_files=glob.glob(os.path.join(download_data_feeds_directory_path, "*.csv")))
    print("Downloading - Change csv file delimiter: End")
    print("Downloading - Unzipping data feeds: Begin")
    downloader.delete_non_csv_datafeeds(download_data_feeds_directory_path)
