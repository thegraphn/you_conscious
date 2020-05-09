import re

from nltk import word_tokenize

from data_processing.data_processing.utils.getHeaders import get_header_index
from data_processing.data_processing.utils.utils import mapping_cleaning_fashionSuitableFor


def clean_size(size):
    '''
    clean size, try to split with different separator.
    delete unnecessary strings etc...
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
    size = size.replace("/", ",")
    size = size.replace(".0", "")  # sometimes there is a 0 after the number
    size = size.split(",")

    size = list(set(size))
    return size


def cleanTitleRow(row):
    """
    delete useless substring from the title content
    :param row:
    :return:
    """
    list_regex = [r"^.*(–\sGr.*\s\d{2}(\/\d{2})?)$", r"^.*(–\sGr(.*)\s([A-Z]{1,2}))$", r"^.*(\d{2})$"]
    for regex in list_regex:
        for i, cell in enumerate(row):
            matches = re.finditer(regex, cell)
            for matchNum, match in enumerate(matches, start=1):
                row[i] = cell.replace((match.group(1)), "")
            row[i] = re.sub(r"Gr\..*", "", row[i])
            row[i] = re.sub(r"Grö.*", "", row[i])
    return row


def clean_category_sex(article: list) -> str:
    categoryName_index = get_header_index("category_name")
    fashionSuitableFor_index = get_header_index("Fashion:suitable_for")
    words_title = word_tokenize(article[get_header_index("Title")])
    cat = article[categoryName_index]
    for word in words_title:
        for k, v in mapping_cleaning_fashionSuitableFor.items():
            if word == k:
                article[categoryName_index] = v
                cat = article[categoryName_index].split(" > ")
                if len(cat) > 1 and len(article) > 20:
                    cat[1] = article[fashionSuitableFor_index]
                    if cat[1] == "" or cat[1] == " ":
                        cat[1] = "Damen"
                    cat = " > ".join(cat)
                    cat = cat.replace("female", "Damen")
                    cat = cat.replace("Female", "Damen")
                    cat = cat.replace("male", "Herren")
                    cat = cat.replace("Male", "Herren")
                    break
            else:
                cat = article[categoryName_index]
    return cat
