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

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/download_data_feeds", "")
folder = folder.replace(r"\data_processing\download_data_feeds", "")
sys.path.append(folder)
import glob
import urllib.request
import datetime
from multiprocessing import Process, Pool
from data_processing.utils.utils import download_data_feeds_directory_path, createMappingBetween2Columns, \
    file_url_shop_path, \
    number_processes

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
    :return: write file with a new column
    '''
    headers = []
    with open(in_file, encoding="utf-8") as in_file:
        with open(os.path.join(path, "datafeeds_preprocessing\downloaded_datafeeds/SORBAS_with_merchant_name.csv"), 'w',
                  encoding="utf-8") as o:
            csv_reader = csv.reader(in_file)
            csv_writer = csv.writer(o)
            for row in csv_reader:
                headers = row
                break
            headers: list = headers + ["merchant_name"]
            csv_writer.writerow(headers)
            for row in csv_reader:
                row: list = row + [name]
                csv_writer.writerow(row)
    os.system("rm " + in_file)


def downloadDatafeeds(list_tuples_shops_urls: list):
    """
    This function uses Pool and call the sub-function in order to do the task download data feed
    :param list_tuples_shops_urls:
    :return:
    """
    with Pool(processes=2)as p:
        list(tqdm.tqdm(p.imap(downloadDatafeed, list_tuples_shops_urls), total=len(list_tuples_shops_urls)))


def downloadDatafeed(tuple_shop_url: tuple):
    """
    :param tuple_shop_url: tupel containing (shop_name,url)
    :return:
    """
    shop_name, link = tuple_shop_url
    shop_name = shop_name.replace(" ", "_")
    if "LOVECO" in shop_name:
        format_file: str = ".csv"
    else:
        format_file: str = ".gz"
    path_file: str = os.path.join(download_data_feeds_directory_path, shop_name + "-" +
                                  datetime.datetime.now().strftime("%y-%m-%d") + format_file)
    urllib.request.urlretrieve(link, path_file)


def unzipFiles(list_files: list):
    """
     This function uses Pool and call the sub-function in order to do the task unzipFile
    :param list_files: List of the file to try to unzip
    """

    with Pool(processes=number_processes)as p:
        list(tqdm.tqdm(p.imap(unzipFile, list_files), total=len(list_files)))


def unzipFile(file: str):
    """
    unzip a given file
    :param file: file to unzip
    """
    if ".csv" in file:
        pass
    if "LOVECO" in file:
        os.system("mv " + file + " " + file[:-3] + "csv")
    if "gz" in file:
        length_to_delete = -3
        os.system("gunzip -kc " + str(file) + " > " + str(file[:length_to_delete]) + ".csv")


def delete_non_csv_datafeeds(directory: str):
    list_files: list = glob.glob(os.path.join(directory, "*"))
    for file in list_files:
        if not file.endswith("csv") and not file.endswith(".py"):
            os.system("rm " + file)
        else:
            pass


def delete_all_csv_file():
    for file in glob.glob(os.path.join(download_data_feeds_directory_path, "*.csv")):
        os.system("rm " + file)


def downloading():
    delete_all_csv_file()
    mapping_url_shop = createMappingBetween2Columns(file_url_shop_path, 0, 1, ";")
    list_tpl_shops_urls = [(shop, url) for shop, url in mapping_url_shop.items()]
    list_tpl_shops_urls = list_tpl_shops_urls[1:]  # remove the headers
    print("Downloading - Downloading data feeds: Begin")
    downloadDatafeeds(list_tpl_shops_urls)
    print("Downloading - Downloading data feeds: End")
    list_downloaded_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*"))
    print("Downloading - Unzipping data feeds: Begin")
    unzipFiles(list_downloaded_files)
    print("Downloading - Unzipping data feeds: Begin")
    delete_non_csv_datafeeds(download_data_feeds_directory_path)
