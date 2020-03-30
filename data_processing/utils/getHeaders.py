from data_processing.utils.utils import getMappingColumnIndex, cleansed_sex_data_feed_path, filtered_data_feed_path, \
    features_affiliateId_data_feed_path
import os

if os.path.exists(filtered_data_feed_path):
    mapping_columnHeader = getMappingColumnIndex(filtered_data_feed_path, "\t")
    mapping_columnHeader["DUMMY_VALUE"] = 9999
else:
    mapping_columnHeader = None


def getHeadersIndex(header, file=filtered_data_feed_path):
    if header == "category_name":
        return getMappingColumnIndex(filtered_data_feed_path, "\t")["category_name"]
    if header == "Labels":
        return getMappingColumnIndex(file, "\t")["Labels"]
    if header == "Material":
        return getMappingColumnIndex(file, "\t")["Material"]
    if header == "search_price":
        return getMappingColumnIndex(file, "\t")["search_price"]
    if header == "rrp_price":
        return getMappingColumnIndex(file, "\t")["rrp_price"]
    if header == "delivery_cost":
        return getMappingColumnIndex(file, "\t")["delivery_cost"]
    if header == "Title":
        return getMappingColumnIndex(file, "\t")["Title"]
    if header == "Fashion:suitable_for":
        return getMappingColumnIndex(filtered_data_feed_path, "\t")["Fashion:suitable_for"]
    if header =="merchant_name":
        return getMappingColumnIndex(filtered_data_feed_path, "\t")["merchant_name"]
    else:
        print("HEADER NOT IMPLEMENTED")