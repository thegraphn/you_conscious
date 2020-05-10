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

from data_processing.data_processing.utils.utils import download_data_feeds_directory_path, createMappingBetween2Columns, \
    file_url_shop_path

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/download_data_feeds", "")
folder = folder.replace(r"\data_processing\download_data_feeds", "")
sys.path.append(folder)
import glob
import urllib.request
import datetime
from multiprocessing import Pool

path = "/mnt/c/Users/graphn/PycharmProjects/you_conscious/data_processing/data_working_directory/download"
# path = sys.argv[1]
begin = datetime.datetime.now()
print("Downloading begin: ", begin)


def readDatafeedUrlFile(file: str) -> dict:
    '''
    :param file: file containing the mapping of Shops and URLS
    :return: dictionary. key:name of shop, value: url
    '''
    datafeed_url_links: dict = {}

    with open(file) as f:
        csv_reader = csv.reader(f, delimiter=";")
        for row in csv_reader:
            name_shop: str = row[0]
            url: str = row[1]
            if name_shop != "Advertiser Name" and url != "URL":
                datafeed_url_links[name_shop] = url
    return datafeed_url_links


def addMerchantName(in_file: str, name: str):
    '''
    Only for SORBRAS
    :param in_file: datafeed file
    :param name: name to add into the data feed
    '''
    headers: list = []
    with open(in_file, encoding="utf-8") as file:
        with open(os.path.join(path, "datafeeds_preprocessing\downloaded_datafeeds/SORBAS_with_merchant_name.csv"), 'w',
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


def downloadDatafeeds(list_tuples_shops_urls: list):
    """
    This function uses Pool and call the sub-function  downloadDatafeed.
    The number of processes is set to 2 because of the internet connection.
    :param list_tuples_shops_urls: List of tuples (shop name, link)
    """
    with Pool(processes=2)as p:
        list(tqdm.tqdm(p.imap(downloadDatafeed, list_tuples_shops_urls), total=len(list_tuples_shops_urls)))


def downloadDatafeed(tuple_shop_url: tuple):
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
    else:
        format_file = ".gz"
        path_file: str = os.path.join(download_data_feeds_directory_path, shop_name + "-" +
                                      datetime.datetime.now().strftime("%y-%m-%d") + format_file)
        urllib.request.urlretrieve(link, path_file)



def unzip_files(list_files: list):
    """
     This function uses Pool and call the sub-function unzipFile
    :param list_files: List of the files to try to unzip
    """

    with Pool(processes=2)as p:
        list(tqdm.tqdm(p.imap(unzipFile, list_files), total=len(list_files)))


def unzipFile(file: str):
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


def delete_non_csv_datafeeds(directory: str):
    """
    Delete all file in a directory except py and csv files
    :param directory: Directory where the files will be deleted
    """
    list_files: list = glob.glob(os.path.join(directory, "*"))
    for file in list_files:
        if not file.endswith("csv") and not file.endswith(".py"):
            os.system("rm " + file)


def delete_all_csv_file(directory: str = download_data_feeds_directory_path):
    """
    Delete all csv files in a given directory
    :param directory: Directory where the csv files are
    """
    for file in glob.glob(os.path.join(directory, "*.csv")):
        os.system("rm " + file)


def downloading():
    delete_all_csv_file()
    mapping_url_shop = createMappingBetween2Columns(file_url_shop_path, 0, 1, ";")
    list_tpl_shops_urls = [(shop, url) for shop, url in mapping_url_shop.items()]
    print(list_tpl_shops_urls)
    list_tpl_shops_urls = list_tpl_shops_urls[1:]  # remove the headers
    print("Downloading - Downloading data feeds: Begin")
    downloadDatafeeds(list_tpl_shops_urls)
    print("Downloading - Downloading data feeds: End")
    list_downloaded_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*"))
    print("Downloading - Unzipping data feeds: Begin")
    unzip_files(list_downloaded_files)
    print("Downloading - Unzipping data feeds: Begin")
    delete_non_csv_datafeeds(download_data_feeds_directory_path)
