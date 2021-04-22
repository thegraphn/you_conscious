from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.utils import get_mapping_column_index

filtered_data_feed_path = file_paths["filtered_data_feed_path"]


def get_headers_index(header, file=filtered_data_feed_path, sep="\t"):
    if header == "category_name":
        return get_mapping_column_index(filtered_data_feed_path, sep)["category_name"]
    if header == "Labels":
        print(get_mapping_column_index(file, sep))
        return get_mapping_column_index(file, sep)["Labels"]
    if header == "Material":
        return get_mapping_column_index(file, sep)["Material"]
    if header == "search_price":
        return get_mapping_column_index(file, sep)["search_price"]
    if header == "rrp_price":
        return get_mapping_column_index(file, sep)["rrp_price"]
    if header == "delivery_cost":
        return get_mapping_column_index(file, sep)["delivery_cost"]
    if header == "Title":
        return get_mapping_column_index(file, sep)["Title"]
    if header == "Fashion:suitable_for":
        return get_mapping_column_index(filtered_data_feed_path, sep)["Fashion:suitable_for"]
    if header == "merchant_name":
        x = get_mapping_column_index(filtered_data_feed_path, sep)
        return get_mapping_column_index(filtered_data_feed_path, sep)[header]
    if header == "aw_deep_link":
        return get_mapping_column_index(filtered_data_feed_path, sep)["aw_deep_link"]
    if header == "Title":
        return get_mapping_column_index(file, sep)["Title"]
    if header == "description":
        return get_mapping_column_index(file, sep)["description"]
    if header == "merchant_product_id":
        return get_mapping_column_index(file, sep)["merchant_product_id"]
    if header == "colour":
        return get_mapping_column_index(file, sep)["colour"]
    if header == "aw_deep_link":
        return get_mapping_column_index(file, sep)["aw_deep_link"]
    if header == "item_id":
        return get_mapping_column_index(file, sep)["item_id"]
    if header == "category_normalized":
        return get_mapping_column_index(file, sep)["category_normalized"]
    if header == "color_normalized":
        return get_mapping_column_index(file, sep)["color_normalized"]
    if header == "label_0":
        return get_mapping_column_index(file, sep)["label_0"]
    if header == "label_1":
        return get_mapping_column_index(file, sep)["label_1"]
    if header == "label_2":
        return get_mapping_column_index(file, sep)["label_2"]
    if header == "label_3":
        return get_mapping_column_index(file, sep)["label_3"]
    if header == "color_normalized_0":
        return get_mapping_column_index(file,sep)["color_normalized_0"]
    if header == "color_normalized_1":
        return get_mapping_column_index(file,sep)["color_normalized_1"]
    if header == "color_normalized_2":
        return get_mapping_column_index(file,sep)["color_normalized_2"]
    if header =="saison":
        return get_mapping_column_index(file,sep)["saison"]
    if header =="saison_conf_score_index":
        return get_mapping_column_index(file,sep)["saison_conf_score_index"]
    else:
        print("HEADER NOT IMPLEMENTED", header)
        return get_mapping_column_index(file, sep)[header]
