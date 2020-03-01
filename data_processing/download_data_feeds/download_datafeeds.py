######################################################################################
#                                                                                    #
#                                                                                    #
# Download datafeeds from their links. The links are saved into a txt. One per line. #
#                                                                                    #
#                                                                                    #
######################################################################################
import csv
import os
import glob
import sys
import urllib.request
import datetime
from multiprocessing import Process
import sys

# pathname = "/Users/ConnyContini/Downloads/backend_backup_2019-2-28/backend/"
# pathname = "/home/thegraphn/repositories/YC/backend"
path = r"C:\Users\graphn\PycharmProjects\you_conscious\data_processing\data_working_directory\download"
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
        csvreader = csv.reader(f, delimiter=";")
        for row in csvreader:
            name_shop = row[0]
            url = row[1]
            if name_shop != "Advertiser Name" and url != "URL":
                datafeed_url_links[name_shop] = url
    return datafeed_url_links


def addMerchentName(inFile, name):
    '''
    Only for SORBRAS
    :param file: datafeed file
    :param name: name to add into the datafeed
    :return: write file with a new column
    '''
    headers = []
    with open(inFile, encoding="utf-8") as in_file:
        with open(path + "datafeeds_preprocessing/downloaded_datafeeds/SORBAS_with_merchant_name.csv", 'w',
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
    os.system("rm " + inFile)


def downloadFile(link, shop_name):
    '''
    download a datafeed
    :param link: link of the datafeed
    :param shop_name: name of the datafeed
    :return:
    '''
    shop_name = shop_name.replace(" ", "_")
    if "affili.net" in link or ".csv" in link:
        frmt = ".csv"
    else:
        frmt = ".gz"

    urllib.request.urlretrieve(link,
                               r"C:\\Users\\graphn\\PycharmProjects\\you_conscious\\data_processing\\data_working_directory\\download\\"
                               + shop_name + "-" + datetime.datetime.now().strftime("%y-%m-%d") + frmt)


def giveWork(inpt, function_name):
    '''
    Send work to the according function
    :param tupel: tupel containing lists
    :param function_name: the name of function which needs to be run
    :return:
    '''
    if function_name == "downloadFile":
        for shop, url in inpt:
            print(url)
            downloadFile(url, shop)
    if function_name == "unzip":
        for file in inpt:
            unzip(file)
    if function_name == "addMerchentName":
        for file in inpt:
            if "SORBAS" in file:
                addMerchentName(file, "SORBAS")


def unzip(file):
    '''
    unzip a given file
    :param file: file to unzip
    '''
    if ".csv" in file:
        lenght_to_delete = -7
    if ".gz" in file:
        lenght_to_delete = -3
        os.system("gunzip -kc " + str(file) + " > " + str(file[:lenght_to_delete]) + ".csv")
    if "LOVECO" in file:
        os.system("mv " + file + " " + file[:-2] + "csv")


if __name__ == '__main__':
    # writeLog("download_datafeeds.py : Downloading begin", LOG_FILE)
    dict_url = readDatafeedUrlFile(
        r"C:\Users\graphn\PycharmProjects\you_conscious\utils\data_dependencies\datafeed-locations.csv")
    # writeLog("download_datafeeds.py : Dictionary for the mapping: " + str(dict_url),LOG_FILE)
    list_shops = list(dict_url.keys())
    # writeLog("download_datafeeds.py : List shops: #" +str(len(list_shops))+" "+ str(list_shops),LOG_FILE)
    list_urls = list(dict_url.values())
    # writeLog("download_datafeeds.py : List urls: #" + str(len(list_urls))+" "+ str(list_urls),LOG_FILE)
    tupelShopsUrl = zip(list_shops, list_urls)
    # writeLog("download_datafeeds.py : Tuppels shop and urls:" + str(tupelShopsUrl),LOG_FILE)
    # p = Process(target=giveWork, args=(tupelShopsUrl,"downloadFile"))
    # p.start()
    # p.join()
    for shop, url in zip(list_shops, list_urls):
        downloadFile(url, shop)
    list_files = glob.glob(path + "datafeeds_preprocessing/downloaded_datafeeds/*")
    # writeLog("download_datafeeds.py : Files in download_datafeeds/ # " +str(len(list_files)) +" :" + str(
    # list_files),LOG_FILE)
    len_to_remove = len(path + "datafeeds_preprocessing/")
    # writeLog("download_datafeeds.py : Length to be remove from file " + str(len_to_remove),LOG_FILE )
    p = Process(target=giveWork, args=(list_files, "unzip"))
    p.start()
    p.join()
    # writeLog("download_datafeeds.py : Unziping of the files done.",LOG_FILE )
    print("Unziping: Done")
    os.system("rm " + path + "datafeeds_preprocessing/downloaded_datafeeds/*.gz")
    # writeLog("download_datafeeds.py : This files have been removed: " +path +
    # "datafeeds_preprocessing/downloaded_datafeeds/*.gz",LOG_FILE )
    list_files = glob.glob(path + "datafeeds_preprocessing/downloaded_datafeeds/*")
    # writeLog("download_datafeeds.py : List of file for adding merchent name # " +str(len(list_files)) +" :" + str(
    # list_files),LOG_FILE )
    p = Process(target=giveWork, args=(list_files, "addMerchentName"))
    p.start()
    p.join()
    list_files = glob.glob(path + "datafeeds_preprocessing/downloaded_datafeeds/*")
    # writeLog("download_datafeeds.py : Files in downloaded_datafeeds # " +str(len(list_files)) +" :" + str(
    # list_files), LOG_FILE)
    end = datetime.datetime.now()
    print("Downloading end: ", end)
    # writeLog("download_datafeeds.py : Downloading end",LOG_FILE)
    print("It took ", end - begin, " to run")
    # writeLog("download_datafeed.py : download_datafeeds.py took "+ str(end-begin) +"to run.",LOG_FILE)
