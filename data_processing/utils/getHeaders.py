from data_processing.utils.file_paths import file_paths
from data_processing.utils.utils import getMappingColumnIndex

filtered_data_feed_path = file_paths["filtered_data_feed_path"]


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
    if header == "merchant_name":
        return getMappingColumnIndex(filtered_data_feed_path, "\t")["merchant_name"]
    if header == "aw_deep_link":
        return getMappingColumnIndex(filtered_data_feed_path, "\t")["aw_deep_link"]
    if header == "Title":
        return getMappingColumnIndex(file, "\t")["Title"]
    else:
        print("HEADER NOT IMPLEMENTED")
