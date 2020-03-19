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


def readDatafeedUrlFile(file):
    '''
    :param file: file containings the mapping of Shops and URLS
    :return: dictionay. key:name of shop, value: url
    '''
    datafeed_url_links = {}

    with open(file) as f:
        csv_reader = csv.reader(f, delimiter=";")
        for row in csv_reader:
            name_shop = row[0]
            url = row[1]
            if name_shop != "Advertiser Name" and url != "URL":
                datafeed_url_links[name_shop] = url
    return datafeed_url_links


def addMerchantName(in_file, name):
    '''
    Only for SORBRAS
    :param in_file: datafeed file
    :param name: name to add into the data feed
    :return: write file with a new column
    '''
    headers = []
    with open(in_file, encoding="utf-8") as in_file:
        with open(path + "datafeeds_preprocessing\downloaded_datafeeds/SORBAS_with_merchant_name.csv", 'w',
                  encoding="utf-8") as o:
            csv_reader = csv.reader(in_file)
            csv_writer = csv.writer(o)
            for row in csv_reader:
                headers = row
                break
            headers = headers + ["merchant_name"]
            csv_writer.writerow(headers)
            for row in csv_reader:
                row = row + [name]
                csv_writer.writerow(row)
    os.system("rm " + in_file)


def downloadDatafeeds(list_tuples_shops_urls):
    with Pool(processes=2)as p:
        list(tqdm.tqdm(p.imap(downloadDatafeed, list_tuples_shops_urls), total=len(list_tuples_shops_urls)))


# todo use ray

def downloadDatafeed(tupel_shop_url):
    """
    :param tupel_shop_url: tupel containing (shop_name,url)
    :return:
    """
    shop_name, link = tupel_shop_url
    shop_name = shop_name.replace(" ", "_")

    if "LOVECO" in shop_name:
        frmt = ".csv"
    else:
        frmt = ".gz"
    path_file = os.path.join(download_data_feeds_directory_path, shop_name + "-" +
                             datetime.datetime.now().strftime("%y-%m-%d") + frmt)
    urllib.request.urlretrieve(link, path_file)


def unzipFiles(list_files):
    with Pool(processes=number_processes)as p:
        list(tqdm.tqdm(p.imap(unzipFile, list_files), total=len(list_files)))


def unzipFile(file):
    '''
    unzip a given file
    :param file: file to unzip
    '''
    if ".csv" in file:
        pass

    if "LOVECO" in file:
        os.system("mv " + file + " " + file[:-2] + "csv")
    if "gz" in file:
        lenght_to_delete = -3
        os.system("gunzip -kc " + str(file) + " > " + str(file[:lenght_to_delete]) + ".csv")


def deleteNonCsvDataFeeds(list_files):
    for file in list_files:
        if file.endswith("gz"):
            os.system("rm " + file)
        else:
            pass


def delete_all_csv_file():
    for file in glob.glob(os.path.join(download_data_feeds_directory_path, "*.csv")):
        os.system("rm " + file)


def dowloading():
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
    list_files_in_download_dir = glob.glob(os.path.join(download_data_feeds_directory_path, "*"))
    deleteNonCsvDataFeeds(list_files_in_download_dir)

# writeLog("download_datafeeds.py : Downloading begin", LOG_FILE)
# dict_url = readDatafeedUrlFile(
#   "/mnt/c/Users/graphn/PycharmProjects/you_conscious/utils/data_dependencies/datafeed-locations.csv")
# writeLog("download_datafeeds.py : Dictionary for the mapping: " + str(dict_url),LOG_FILE)

# writeLog("download_datafeeds.py : Tuppels shop and urls:" + str(tupelShopsUrl),LOG_FILE)
# p = Process(target=giveWork, args=(tupelShopsUrl,"downloadFile"))
# p.start()
# p.join()
# for shop, url in zip(list_shops, list_urls):
#   downloadFile(url, shop)
# list_files = glob.glob(path + "datafeeds_preprocessing/downloaded_datafeeds/*")
# writeLog("download_datafeeds.py : Files in download_datafeeds/ # " +str(len(list_files)) +" :" + str(
# list_files),LOG_FILE)
# len_to_remove = len(path + "datafeeds_preprocessing/")
# writeLog("download_datafeeds.py : Length to be remove from file " + str(len_to_remove),LOG_FILE )
# p = Process(target=giveWork, args=(list_files, "unzip"))
# p.start()
# p.join()
# writeLog("download_datafeeds.py : Unziping of the files done.",LOG_FILE )

# print("Unziping: Done")
# os.system("rm " + path + "datafeeds_preprocessing/downloaded_datafeeds/*.gz")
# writeLog("download_datafeeds.py : This files have been removed: " +path +
# "datafeeds_preprocessing/downloaded_datafeeds/*.gz",LOG_FILE )
# list_files = glob.glob(path + "datafeeds_preprocessing/downloaded_datafeeds/*")
# writeLog("download_datafeeds.py : List of file for adding merchent name # " +str(len(list_files)) +" :" + str(
# list_files),LOG_FILE )
# p = Process(target=giveWork, args=(list_files, "addMerchentName"))
# p.start()
# p.join()
# list_files = glob.glob(path + "datafeeds_preprocessing/downloaded_datafeeds/*")
# writeLog("download_datafeeds.py : Files in downloaded_datafeeds # " +str(len(list_files)) +" :" + str(
# list_files), LOG_FILE)
# end = datetime.datetime.now()
# print("Downloading end: ", end)
# writeLog("download_datafeeds.py : Downloading end",LOG_FILE)
# print("It took ", end - begin, " to run")
# writeLog("download_datafeed.py : download_datafeeds.py took "+ str(end-begin) +"to run.",LOG_FILE)
