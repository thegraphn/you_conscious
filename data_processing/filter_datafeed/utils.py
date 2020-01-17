import os



def getFilters(filter_file):
    '''
    :param filter_file: Wher the filter are stored
    :return: list of filters
    '''
    filters = []
    with open(filter_file, "r", encoding="utf-8") as f:
        for line in f:
            filters.append(line.replace("\n", ""))

    return filters
