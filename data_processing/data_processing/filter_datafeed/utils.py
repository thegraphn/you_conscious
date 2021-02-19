import os


def getFilters(filter_file):
    """
    :param filter_file: Wher the filter are stored
    :return: list of filters
    """
    filters = []
    with open(filter_file, "r", encoding="utf-8") as f:
        for line in f:
            filters.append(line.replace("\n", ""))

    return filters


def replace_merchant_names_ean_order(merchant_name):
    if merchant_name == "Avocadostore":
        return "0" + merchant_name
    if merchant_name == "Im walking":
        return "1" + merchant_name
    if merchant_name == "mirapodo":
        return "2" + merchant_name
    if merchant_name == "OTTO":
        return "3" + merchant_name
    else:
        return merchant_name
