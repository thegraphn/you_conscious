import csv
import glob
import os
import datetime
import sys

from data_processing.utils.utils import download_data_feeds_path, column_mapping_merging_path

begin = datetime.datetime.now()
print("Merging script: Started ", begin)
enc = "utf-8"
LOG_FILE = path+"datafeeds_preprocessing/log_file.log"

def changeProgrammId2MerchentName(csv_file,shop_id_name_mapping_csv,):
    shopId2Name = {}
    with open(shop_id_name_mapping_csv,encoding="utf-8-sig") as f:
        csv_reader_mapping = csv.reader(f,delimiter = ";")
        for row in csv_reader_mapping:
            shopId2Name[row[0]] = row[1]
    with open(csv_file,encoding="utf-8") as csv_input:
        csv_reader = csv.reader(csv_input,delimiter =",",quotechar = '"')
        pos_merchent_id = 0
        pos_merchant_name = 0
        for row in csv_reader:
            for i in range(len(row)):
                if "merchant_id" == row[i]:
                    pos_merchent_id = i
                if "merchant_name" == row[i]:
                    pos_merchant_name = i
            break

    with open(csv_file,encoding=enc) as input:
        csv_reader2 = csv.reader(input, delimiter=",", quotechar='"')
        with open(csv_file + "shopId2Name.csv",'a',encoding="utf-8") as o:
            csv_writer = csv.writer(o, delimiter=",", quotechar='"')
            c = 0
            for row in csv_reader2:
                if c==0:
                    for i in range(len(row)):
                        for key,value in shopId2Name.items():
                            if key == row[i]:
                                row[pos_merchant_name] = value
                csv_writer.writerow(row)


    print("id ",pos_merchent_id)
    print("name ",pos_merchant_name)

def changeColumnName(csv_file,mapping_file):
    dict_mapping_column = {}
    with open(mapping_file,encoding="utf-8-sig") as mapping_csv:
        csv_reader = csv.reader(mapping_csv,delimiter = ";")
        for row in csv_reader:
            dict_mapping_column[row[0]] = row[1]
    with open(csv_file,encoding=enc) as csv_to_rename:
        csv_reader = csv.reader(csv_to_rename,delimiter = ",",quotechar = '"')
        with open(csv_file+"change.csv",'w') as output_csv:
            c = True
            csv_writer = csv.writer(output_csv,delimiter = ",",quotechar = '"')
            for row in csv_reader:
                if c == True:
                    for key,value in dict_mapping_column.items():
                        for i in range(len(row)):
                            if key == row[i]:
                                row[i] = value
                    csv_writer.writerow(row)
                else:
                    csv_writer.writerow(row)

def mergeCSV(list_files,fieldnames,output_data):
    fieldnames = list(fieldnames)
    with open(output_data, 'a',encoding=enc) as output_csvfile:
        writer = csv.DictWriter(output_csvfile, fieldnames=fieldnames,delimiter=",",quotechar='"')
        csv_writer = csv.writer(output_csvfile,delimiter =",",quotechar='"')
        csv_writer.writerow(fieldnames)
        for filename in list_files:
            with open(filename, "r", newline="") as f_in:
                reader = csv.DictReader(f_in,delimiter=",",quotechar='"')  # Uses the field names in this file
                for line in reader:
                    try:
                        writer.writerow(line)
                    except:
                        pass

def getColumNames(file):
    '''
    :param file: csv file where the column has to be read
    :return: list of column name
    '''
    c = 1
    list_column_names = []
    with open(file,encoding=enc) as f:
        csvreader = csv.reader(f, delimiter=",")
        for row in csvreader:
            if c==1:
                list_column_names = row
            c+=1
            if c>1:
                break
    return list_column_names

def getNewColumnNames(file):
    '''
    :param file: csv file where the new column for the feature are
    :return: list of the new column
    '''
    set_column_names = set()
    with open(file,encoding=enc) as f:
        csv_reader = csv.reader(f,delimiter = ";")
        c = 0
        for row in csv_reader:
            if c>0:
                set_column_names.add(row[2])
            c+=1
    set_column_names = list(set_column_names)
    return set_column_names


list_files = glob.glob(os.path.join(download_data_feeds_path,"*.csv"))

set_col = set()
for file in list_files:
    changeColumnName(file,column_mapping_merging_path)

list_files = glob.glob(os.path.join(download_data_feeds_path,"*.csvchange.csv"))

for file in list_files:
    for name in getColumNames(file):
        set_col.add(name)
set_col = list(set_col)
newColumnNames = getNewColumnNames(path+"utils/features/features.csv") + set_col
print("Changing column names: Done")


list_files = glob.glob(path+"datafeeds_preprocessing/downloaded_datafeeds/*.csvchange.csv")
mergeCSV(list_files,newColumnNames,path+"datafeeds_preprocessing/merged_datafeeds/merged_datafeeds.csv")
os.system("rm "+path+"datafeeds_preprocessing/downloaded_datafeeds/*.csvchange.csv")
print("Merging: Done")

changeProgrammId2MerchentName(path+"datafeeds_preprocessing/merged_datafeeds/merged_datafeeds.csv",path+"utils/shop_ids/shops-ids-names.csv")
print("Changing ID to Name: Done")

os.system("rm "+path+"datafeeds_preprocessing/merged_datafeeds/merged_datafeeds.csv")
os.system("mv "+path+"datafeeds_preprocessing/merged_datafeeds/merged_datafeeds.csvshopId2Name.csv "+path+"datafeeds_preprocessing/merged_datafeeds/merged_datafeeds.csv")
print("Merging script: Done ", datetime.datetime.now())
end = datetime.datetime.now()
