import re

import tqdm

from data_processing.data_processing.utils.getHeaders import get_headers_index
from data_processing.data_processing.utils.utils import mapping_cleaning_fashionSuitableFor, get_tokens


def clean_size(size) -> list:
    """
    clean size, try to split with different separator.
    delete unnecessary strings etc...
    :param size:
    :return:
    """
    regex = r"(\(\d{2}(\/\d{2})*\))"
    if "(" and ")" in size:
        size = re.sub(regex, "", size)
    if size.isdigit() and len(size) == 4:  # This is socks
        n = 2  # split every 2 character
        size: list = [size[i:i + n] for i in range(0, len(size), n)]
        size = ["-".join(size)]
        return size
    if "er pack" in size:
        size = size.replace(size[0], "")
        size = size.replace("er pack", "")
        return size
    else:
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


def convert_to_utf(list_articles: list) -> list:
    mapping_to_utf = {"&uuml;": "ü",
                      "&ouml;": "ö",
                      "&auml;": "ä",
                      "&szlig;": "ß",
                      "&Auml;": "Ä",
                      "&Uuml;": "Ü",
                      "&Ouml;": "Ö",
                      "&bdquo;": "„",
                      "&quot;": '"',
                      "&rsquo;": "'",

                      }

    headers = list_articles[0]
    list_article_no_header = list_articles[1:]
    for a, article in tqdm.tqdm(enumerate(list_article_no_header), total=len(list_article_no_header),
                                desc="Converting to utf-8"):
        for c, cell in enumerate(article):
            for encoding, utf_ch in mapping_to_utf.items():
                cell = cell.replace(encoding, utf_ch)
                article[c] = cell
        list_article_no_header[a] = article
    return [headers] + list_article_no_header


def clean_title_row(row):
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
    category_name_index = get_headers_index("category_name")
    fashion_suitable_for_index = get_headers_index("Fashion:suitable_for")
    words_title = get_tokens(article[get_headers_index("Title")])
    cat = article[category_name_index]
    for word in words_title:
        for k, v in mapping_cleaning_fashionSuitableFor.items():
            if word == k:
                article[category_name_index] = v
                cat = article[category_name_index].split(" > ")
                if len(cat) > 1 and len(article) > 20:
                    cat[1] = article[fashion_suitable_for_index]
                    if cat[1] == "" or cat[1] == " ":
                        cat[1] = "Damen"
                    cat = " > ".join(cat)
                    cat = cat.replace("female", "Damen")
                    cat = cat.replace("Female", "Damen")
                    cat = cat.replace("male", "Herren")
                    cat = cat.replace("Male", "Herren")
                    break
            else:
                cat = article[category_name_index]
    return cat


def change_chain_characters_to_umlaut(string: str) -> str:
    text = ''
    for zeichen in string:
        if zeichen == u'ä':
            text += '&auml;'
        elif zeichen == u'ö':
            text += '&ouml;'
        elif zeichen == u'ü':
            text += '&uuml;'
        elif zeichen == u'ß':
            text += '&szlig;'
        else:
            text += zeichen
    return text
