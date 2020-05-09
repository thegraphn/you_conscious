from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.utils import get_mapping_column_index

filtered_data_feed_path = file_paths["filtered_data_feed_path"]


def get_header_index(header, file=filtered_data_feed_path) -> int:
    if header == "category_name":
        return get_mapping_column_index(filtered_data_feed_path, "\t")["category_name"]
    if header == "Labels":
        return get_mapping_column_index(file, "\t")["Labels"]
    if header == "Material":
        return get_mapping_column_index(file, "\t")["Material"]
    if header == "search_price":
        return get_mapping_column_index(file, "\t")["search_price"]
    if header == "rrp_price":
        return get_mapping_column_index(file, "\t")["rrp_price"]
    if header == "delivery_cost":
        return get_mapping_column_index(file, "\t")["delivery_cost"]
    if header == "Title":
        return get_mapping_column_index(file, "\t")["Title"]
    if header == "Fashion:suitable_for":
        return get_mapping_column_index(filtered_data_feed_path, "\t")["Fashion:suitable_for"]
    if header == "merchant_name":
        return get_mapping_column_index(filtered_data_feed_path, "\t")["merchant_name"]
    if header == "aw_deep_link":
        return get_mapping_column_index(filtered_data_feed_path, "\t")["aw_deep_link"]
    if header == "Title":
        return get_mapping_column_index(file, "\t")["Title"]
    if header == "description":
        return get_mapping_column_index(file, "\t")["description"]
    if header == "product_merchant_id":
        return get_mapping_column_index(file, "\t")["merchant_product_id"]
    if header == "aw_image_url":
        return get_mapping_column_index(file, "\t")["aw_image_url"]
    if header == "colour":
        return get_mapping_column_index(file, "\t")["colour"]
    else:
        raise Exception(header, " not implemented")
