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

from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.utils import download_data_feeds_directory_path, \
    change_delimiter_csv, rename_column

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/download_data_feeds", "")
folder = folder.replace(r"\data_processing\download_data_feeds", "")
sys.path.append(folder)
import glob
import urllib.request
import datetime
from multiprocessing import Pool
import pandas as pd


class Downloader:

    def __init__(self):
        self.datafeed_info: list = self.get_datafeed_info()

    @staticmethod
    def get_datafeed_info() -> list:
        """
        Get the info in order to download the datafeeds properly: URL and csv_file delimiter
        :return: list [Shop_name,URL,delimiter],
                        ....
                        }
        """
        # datafeed_info: list = []
        # with open(file_paths["file_datafeed_location"], "r", encoding="utf-8") as input_file:
        #   csv_reader = csv.reader(input_file, delimiter=";")
        #  next(csv_reader)
        # for row in csv_reader:
        #    datafeed_name: str = row[0]
        #   datafeed_url: str = row[1]
        #  datafeed_delimiter: str = row[2]
        # datafeed_info.append([datafeed_name, datafeed_url, datafeed_delimiter])

        df = pd.read_csv(file_paths["file_datafeed_location"], sep=";")
        datafeed_names = df["Advertiser Name"].tolist()
        datafeed_urls = df["URL"].tolist()
        datafeed_delimiters = df["file_delimiter"].tolist()
        datafeed_info = [[dn, du, dd] for dn, du, dd in zip(datafeed_names, datafeed_urls, datafeed_delimiters)]

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
    def add_merchant_name(in_file: str):
        """
        :param in_file: datafeed file
        :param merchant_name: name to add into the data feed
        """

        if "LOVECO" in in_file:
            sep = ","
            df = pd.read_csv(in_file, sep=sep)
            merchant_name = "LOVECO - Fair & Vegan Fashion and Shoes"
            df["merchant_name"] = merchant_name

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
            df = pd.read_csv(in_file,sep=",")
            merchant_name = "LOVECO - Fair & Vegan Fashion and Shoes"
            df["merchant_name"] = merchant_name
        if "JW_PEI" in in_file:
            df = pd.read_csv(in_file, sep=",")
            merchant_name = "JW PEI DE"
            df["merchant_name"] = merchant_name

        return df

    def add_merchant_names(self, list_file_paths: list):
        """
        :param list_file_paths:
        :return:
        """
        print("1", list_file_paths)
        with Pool()as p:
            list_df = list(tqdm.tqdm(p.imap(self.add_merchant_name, list_file_paths), total=len(list_file_paths)))
        for file, df in zip(list_file_paths, list_df):
            print(df.head())
            df.to_csv(file, sep=",")

    def download_datafeeds(self, list_tuples_shops_urls: list):
        """
        This function uses Pool and call the sub-function  downloadDatafeed.
        The number of processes is set to 2 because of the internet connection.
        :param list_tuples_shops_urls: List of tuples (shop name, link)
        """
        for element in list_tuples_shops_urls:
            try:
                self.download_datafeed(element)
            except:
                print(element, " did not work")

    @staticmethod
    def download_datafeed(tuple_shop_url: tuple):
        """
        Download a data feed. If the file is LOVECO, the extension of the file is immediately changed into csv
        :param tuple_shop_url: tuple containing (shop_name,url)
        """
        shop_name: str = tuple_shop_url[0]
        link: str = tuple_shop_url[1]
        shop_name = shop_name.replace(" ", "_")
        already_csv_files = ["LOVECO", "SORBAS", "Le_Shop_Vegan", "Uli_Schott", "muso_koroni", "ETHLETIC", "recolution"]
        try:
            if shop_name in already_csv_files:
                format_file = ".csv"
                path_file: str = os.path.join(download_data_feeds_directory_path, shop_name + "-" +
                                              datetime.datetime.now().strftime("%y-%m-%d") + format_file)
                urllib.request.urlretrieve(link, path_file)



            else:
                format_file = ".gz"
                path_file: str = os.path.join(download_data_feeds_directory_path, shop_name + "-" +
                                              datetime.datetime.now().strftime("%y-%m-%d") + format_file)
                urllib.request.urlretrieve(link, path_file)

        except ValueError:
            print(" did not worked", shop_name, link)

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
            return 1
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
        # if "recolution" in file:
        # os.rename(file[:-3],file[:-3]+".csv")
        if "gz" in file:
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
    downloader: Downloader = Downloader()
    downloader.delete_non_csv_datafeeds(download_data_feeds_directory_path)
    print("Downloading - Downloading data feeds: Begin")
    downloader.download_datafeeds(list_tuples_shops_urls=downloader.datafeed_info)
    print("Downloading - Downloading data feeds: End")
    list_downloaded_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*"))  # it works
    print("Downloading - Unzipping data feeds: Begin")
    downloader.unzip_files(list_files=list_downloaded_files)
    print("Downloading - Change csv file delimiter: Begin")
    downloader.change_delimiters(list_files=glob.glob(os.path.join(download_data_feeds_directory_path, "*.csv")))
    print("Downloading - Change csv file delimiter: End")
    print("Downloading - Unzipping data feeds: Begin")
    downloader.delete_non_csv_datafeeds(download_data_feeds_directory_path)  # does not work
    merchant_names_to_add = ["*muso_koroni*.csv", "*SORBAS*.csv", "*ETHLETIC*.csv", "*recolution*.csv", "*LOVECO*.csv",
                             "*JW_PEI*.csv", "*Uli_Sc*.csv", "*Le_Shop_Vegan*.csv"
                             ]
    # merchant_names_to_add = ["*Le_Shop_Vegan*.csv"]
    list_file_merchant_name_to_add = [glob.glob(os.path.join(download_data_feeds_directory_path, shop))[0]
                                      for shop in merchant_names_to_add]

    downloader.add_merchant_names(list_file_merchant_name_to_add)

    if os.path.exists(os.path.join(download_data_feeds_directory_path,
                                   "JW_PEI" + datetime.datetime.now().strftime("%y-%m-%d") + ".csv")) == 1:
        jw_pei_csv_path: str = glob.glob(os.path.join(download_data_feeds_directory_path, "*JW_PEI*.csv"))[0]

        rename_column(jw_pei_csv_path, ",", "category_name", "Fashion:suitable_for")
