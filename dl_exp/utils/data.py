import csv
import re

import tqdm
from nltk import word_tokenize

from data_processing.utils.getHeaders import getHeadersIndex


def pre_procesing_step(text):
    pattern_euros = r'\s(\<number\>\s)?(million(en)? |billion(en)? |bn |bn. )?([eE]uros?|€)'
    pattern_dollars = r'(usd|USD|\$) ?(<number> ?)+(million|billion|bn)\b'
    pattern_rupees = r'\b(Rs|rs)? ?(<number> ?)+(million |billion |bn |m)?(lakh)?(crore|lakh|rupees)'
    regex_money_compiled = re.compile(r'({}|{}|{})'.format(pattern_euros, pattern_dollars, pattern_rupees))
    regex_email_compiled = re.compile(r'\b\S*@\S+\.\S+\b')
    regex_website_compiled = re.compile(r'\b\S*(www\.|https?)\S*\b')
    regex_html_ampersand_compiled = re.compile(r'amp;')
    regex_html_quote_compiled = re.compile(r'#39;|#146;')
    regex_html_dollar_compiled = re.compile(r'#36;')
    regex_html_whitespace_compiled = re.compile(r'nbsp;|<br />')
    regex_remove_chars_compiled = re.compile(r'[\\/;:,.`()#„"‟\'\"@]')
    regex_numbers_compiled = re.compile(r'\d+')
    # regex_whitespaces_compiled = re.compile(r'[\\/!?+\-=\n]')
    regex_multi_whitespace_compiled = re.compile(r'\s+')

    text = text.replace("ü", 'ue')
    text = text.replace("ä", 'ae')
    text = text.replace("ö", 'oe')
    text = text.replace("ß", 'ss')
    text = _remove_non_ascii(text)
    text = regex_email_compiled.sub(' ', text)
    text = regex_website_compiled.sub(' ', text)
    text = regex_html_ampersand_compiled.sub('&', text)
    text = regex_html_dollar_compiled.sub('$', text)
    text = regex_html_quote_compiled.sub("'", text)
    text = regex_html_whitespace_compiled.sub(' ', text)
    text = regex_remove_chars_compiled.sub(' \g<0> ', text)
    text = regex_numbers_compiled.sub(' <number> ', text)
    text = regex_multi_whitespace_compiled.sub(' ', text)
    text = regex_money_compiled.sub(' <money> ', text)
    return text


def _remove_non_ascii(chars: str) -> str:
    """
    Removes all characters which are not part of the ascii set - regardless of encoding
    """
    return "".join(i for i in chars if ord(i) < 128)


def read_data(data_path: str, label_pos: int) -> list:
    """
    Read the data and return the training data [(text,label),...]
    :param data_path:
    :param label_pos:
    :return:
    """
    data: list = []
    num_lines: int = sum(1 for line in open(data_path, encoding="utf-8"))
    with open(data_path, "r", encoding="utf-8") as f:
        csv_reader: csv = csv.reader(f, delimiter="\t")
        for row in tqdm.tqdm(csv_reader, total=num_lines):
            text: str = " ".join(row[0:label_pos])
            text += " " + " ".join(row[label_pos + 1:len(row)])
            text = pre_procesing_step(text)
            text = word_tokenize(text)

            data.append([text, row[label_pos]])
    return data


def createMatrices(training_data: list, label2id: dict, word2id: dict, label_pos: int, text_pos: int) -> list:
    '''
    The model works with integer, therefore we need to convert the strings into integers
    :param text_pos:
    :param word2id:
    :param label2id:
    :param label_pos:
    :param training_data:
    :return: The same structure but with integers instead of strings
    '''
    for data in training_data:

        text = data[text_pos]
        label = data[label_pos]
        data[label_pos] = label2id[label]
        text_temp = []
        for word in text:
            word = word2id.get(word, word2id["UNKNOWN_TOKEN"])
            text_temp.append(word)
        data[text_pos] = text_temp
    return training_data


def create_data_set(file: str) -> list:
    training_data: list = []
    with open(file, "r", encoding="utf-8") as f:
        csv_reader = csv.reader(f, delimiter="\t")
        for row in csv_reader:
            training_data.append([row[getHeadersIndex("category_name")], row[getHeadersIndex("description")]])
    return training_data
