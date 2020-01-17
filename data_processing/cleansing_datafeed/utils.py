import re
from collections import defaultdict

from data_processing.utils.getHeaders import mapping_columnHeader




def cleanSize(size):
    '''
    clean size, try to split with different separator.
    delete unnessacry strings etc...
    :param size:
    :return:
    '''
    regex = r"(\(\d{2}(\/\d{2})*\))"
    if "(" and ")" in size:
        size = re.sub(regex, "", size)
    size = size.replace("EU", "")
    size = size.replace(" ", "")
    size = size.replace(";", ",")
    size = size.replace("-", ",")
    size = size.replace("|", ",")
    size = size.split(",")
    return size



def cleanTitleRow(row):
    """
    delete useless substring from the title content
    :param row:
    :return:
    """
    list_regex = [r"^.*(–\sGr.*\s\d{2}(\/\d{2})?)$", r"^.*(–\sGr(.*)\s([A-Z]{1,2}))$", r"^.*(\d{2})$"]
    for regex in list_regex:
        for i,cell in enumerate(row):
            matches = re.finditer(regex, cell)
            for matchNum, match in enumerate(matches, start=1):
                row[i] = cell.replace((match.group(1)), "")
            row[i] = re.sub(r"Gr\..*", "", row[i])
            row[i] = re.sub(r"Grö.*", "", row[i])
    return row
