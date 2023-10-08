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
import pandas as pd
import tqdm
import glob
import urllib.request
import datetime
from multiprocessing import Pool
import logging

from data_processing.data_processing.config import loveco
from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.utils import download_data_feeds_directory_path, \
    change_delimiter_csv, rename_column, run_multi_processing_job

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/download_data_feeds", "")
folder = folder.replace(r"\data_processing\download_data_feeds", "")
sys.path.append(folder)


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


class Downloader:

    def __init__(self, download_dir_path: str):
        self.datafeed_info: list = self.get_datafeed_info()
        self.download_dir_path = download_dir_path

    @staticmethod
    def get_datafeed_info() -> list:
        """
        Get the info in order to download the datafeeds properly: URL and csv_file delimiter
        :return: list [Shop_name,URL,delimiter],
                        ....
                        }
        """

        df = pd.read_csv(file_paths["file_datafeed_location"], sep=";")
        datafeed_names = df["Advertiser Name"].tolist()
        datafeed_urls = df["URL"].tolist()
        datafeed_delimiters = df["file_delimiter"].tolist()
        datafeed_info = [[dn, du, dd] for dn, du, dd in zip(datafeed_names, datafeed_urls, datafeed_delimiters)]

        return datafeed_info

    @staticmethod
    def read_datafeed_url_file(file: str) -> dict:
        """
        not in used
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
    def add_merchant_name(in_file: str):
        """
        :param in_file: datafeed file
        :param merchant_name: name to add into the data feed
        """

        if "LOVECO" in in_file:
            df = pd.read_csv(in_file, sep=loveco["sep"])
            df["merchant_name"] = loveco["merchant_name"]

        if "JW_PEI" in in_file:
            sep = ","
            df = pd.read_csv(in_file, sep=sep)
            df.insert(0, "vegan", "Vegan", True)
        if "Uli_Schott" in in_file:
            sep = ","
            merchant_name = "Uli Schott - The unknown brand"
            df = pd.read_csv(in_file, sep=sep)
            df.insert(0, "merchant_name", "Uli Schott - The unknown brand", True)
            df["merchant_name"] = merchant_name
        if "Le_Shop_Vegan" in in_file:
            merchant_name = "Le Shop Vegan"
            sep = ","
            df = pd.read_csv(in_file, sep=sep)
            df.insert(0, "merchant_name", merchant_name, True)
            df["merchant_name"] = merchant_name

        if "muso_koroni" in in_file:
            merchant_name = "muso koroni"
            sep = ";"
            df = pd.read_csv(in_file, sep=sep)
            df.insert(0, "merchant_name", merchant_name, True)

        if "ETHLETIC" in in_file:
            merchant_name = "ETHLETIC"
            sep = ";"
            df = pd.read_csv(in_file, sep=sep)
            df.insert(0, "merchant_name", merchant_name, True)
            df["merchant_name"] = merchant_name
        if "SORBAS" in in_file:
            merchant_name = "SORBAS"
            sep = ","
            df = pd.read_csv(in_file, sep=sep)
            df.insert(0, "merchant_name", merchant_name, True)
            df["merchant_name"] = merchant_name
        if "recolution" in in_file:
            merchant_name = "recolution"
            sep = ","
            df = pd.read_csv(in_file, sep=sep, quotechar='"')
            df.insert(0, "merchant_name", merchant_name, True)
        if "LOVECO" in in_file:
            df = pd.read_csv(in_file, sep=",")
            merchant_name = "LOVECO - Fair & Vegan Fashion and Shoes"
            df["merchant_name"] = merchant_name
        if "JW_PEI" in in_file:
            df = pd.read_csv(in_file, sep=",")
            merchant_name = "JW PEI DE"
            df["merchant_name"] = merchant_name

        return df




    def download_datafeeds(self, list_tuples_shops_urls: list):
        """
        This function uses Pool and call the sub-function  downloadDatafeed.
        The number of processes is set to 2 because of the internet connection.
        :param list_tuples_shops_urls: List of tuples (shop name, link)
        """
        for element in tqdm.tqdm(list_tuples_shops_urls,total=len(list_tuples_shops_urls),desc="Downloading Datafeeds"):
            try:
                self.download_datafeed(element)
            except:
                logging.error(str(element) + " did not work")

    def download_datafeed(self, tuple_shop_url: tuple):
        """
        Download a data feed. If the file is LOVECO, the extension of the file is immediately changed into csv
        :param tuple_shop_url: tuple containing (shop_name,url)
        """
        shop_name: str = tuple_shop_url[0]
        link: str = tuple_shop_url[1]
        shop_name = shop_name.replace(" ", "_")
        already_csv_files = ["LOVECO", "SORBAS", "Le_Shop_Vegan", "Uli_Schott", "muso_koroni", "ETHLETIC", "recolution"]
        if shop_name =="Le_Shop_Vegan":
            x = 0
        try:
            if shop_name in already_csv_files:
                format_file = ".csv"

                path_file: str = os.path.join(self.download_dir_path, shop_name + "-" +
                                              datetime.datetime.now().strftime("%y-%m-%d") + format_file)
                urllib.request.urlretrieve(link, path_file)



            else:
                format_file = ".gz"
                path_file: str = os.path.join(self.download_dir_path, shop_name + "-" +
                                              datetime.datetime.now().strftime("%y-%m-%d") + format_file)
                urllib.request.urlretrieve(link, path_file)

        except ValueError:
            logging.error(" did not worked"+ str(shop_name)+ str(link))

    def unzip_files(self, list_files: list):
        """
        This function uses Pool and call the sub-function unzipFile
            :param list_files: List of the files to try to unzip
        """
        with Pool(processes=2) as p:
            list(tqdm.tqdm(p.imap(self.unzip_file, list_files), total=len(list_files)))

    @staticmethod
    def unzip_file(file: str):
        """
        Try to unzip a given file. If the datafeed is LOVECO the file is not zipped. It is
        just required to change the file's extension
        :param file: file to unzip
        """
        if ".csv" in file:
            logging.info(str(file) + "is ending with .csv")
        if "Le_Shop_Vegan" in file:
            return 1
        if "LOVECO" in file:
            return 1
        if "SORBAS" in file:
            return 1
        if "muso_koroni" in file:
            return 1
        if "Uli_Schott" in file:
            return 1
        if "ETHLETIC" in file:
            os.rename(file, file[:-3] + ".csv")
            return 1
        if "Nordgreen" in file:
            os.rename(file, file[:-3] + ".csv")
            return 1

        if "gz" in file:
            length_to_delete: int = -3
            os.system("gunzip -kc " + str(file) + " > " + str(file[:length_to_delete]) + ".csv")

    def delete_non_csv_datafeeds(self):
        """
        Delete all file in a directory except py and csv files
        :param directory: Directory where the files will be deleted
        """
        list_files: list = glob.glob(os.path.join(self.download_dir_path, "*"))
        for file in list_files:
            if not file.endswith("csv") and not file.endswith(".py"):
                os.system("rm " + file)

    def change_delimiters(self, list_files: list):
        with Pool() as p:
            list(tqdm.tqdm(p.imap(self.change_delimiter, list_files), total=len(list_files)))

    def change_delimiter(self, csv_file_path: str):
        """
        Uniform the delimiter in the csv files
        :param csv_file_path: csv file in which the delimiter may change
        :return:
        """
        if "SORBAS" in csv_file_path:
            return 1
        for info in self.datafeed_info:
            shop_name: str = info[0].replace(" ", "_")
            _: str = info[1]
            delimiter: str = info[2]
            if shop_name in csv_file_path and delimiter != ",":
                change_delimiter_csv(csv_input=csv_file_path, csv_output=csv_file_path, delimiter_input=delimiter,
                                     delimiter_output=",")


def downloading():
    downloader: Downloader = Downloader(download_data_feeds_directory_path)
    downloader.delete_non_csv_datafeeds()
    logging.info("Downloading - Downloading data feeds: Begin")
    downloader.download_datafeeds(list_tuples_shops_urls=downloader.datafeed_info)
    logging.info("Downloading - Downloading data feeds: End")
    list_downloaded_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*"))  # it works
    logging.info("Downloading - Unzipping data feeds: Begin")
    downloader.unzip_files(list_files=list_downloaded_files)
    logging.info("Downloading - Change csv file delimiter: Begin")
    downloader.change_delimiters(list_files=glob.glob(os.path.join(download_data_feeds_directory_path, "*.csv")))
    logging.info("Downloading - Change csv file delimiter: End")
    logging.info("Downloading - Unzipping data feeds: Begin")
    downloader.delete_non_csv_datafeeds()  # does not work
    merchant_names_to_add = [ "SORBAS.csv", "ETHLETIC.csv", "recolution.csv", "LOVECO.csv",
                             "JW_PEI.csv", "Uli_Sc.csv"
                             ]#"*muso_koroni*.csv","*Le_Shop_Vegan*.csv"
    # merchant_names_to_add = ["*Le_Shop_Vegan*.csv"]
    list_file_merchant_name_to_add = []
    list_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*.csv"))
    for file in list_files:
        for merchant_name in merchant_names_to_add:
            if merchant_name in file:
                list_file_merchant_name_to_add.append(file)

    list_df = run_multi_processing_job(function_name=downloader.add_merchant_name,
                                       nbr_process=16,
                                       list_to_process=list_file_merchant_name_to_add,
                                       message="Adding merchant names")
    for file, df in zip(list_file_merchant_name_to_add, list_df):
        df.to_csv(file, sep=",")

    if os.path.exists(os.path.join(download_data_feeds_directory_path,
                                   "JW_PEI" + datetime.datetime.now().strftime("%y-%m-%d") + ".csv")) == 1:
        jw_pei_csv_path: str = glob.glob(os.path.join(download_data_feeds_directory_path, "*JW_PEI*.csv"))[0]

        rename_column(jw_pei_csv_path, ",", "category_name", "Fashion:suitable_for")
