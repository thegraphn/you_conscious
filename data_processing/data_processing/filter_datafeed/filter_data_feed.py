import tokenizer
from multiprocessing import Pool
from typing import Union
import numpy as np
from farm.infer import Inferencer
from nltk import word_tokenize
import tqdm

from data_processing.data_processing.filter_datafeed.utils import getFilters
from data_processing.data_processing.utils.columns_order import column_ord, column_index_mapping
from data_processing.data_processing.utils.file_paths import file_paths, done_datafeed
from data_processing.data_processing.utils.getHeaders import get_headers_index
from data_processing.data_processing.utils.utils import filters_black_file_path, get_lines_csv, merged_data_feed_path, \
    write_2_file, filters_white_file_path, get_tokens, get_mapping_column_index

import pandas as pd


class Filter:

    def __init__(self, relevancy_filter: bool):
        self.vegan_black_filters = getFilters(filters_black_file_path)
        self.vegan_black_filters.sort()
        self.vegan_white_filters = getFilters(filters_white_file_path)
        self.vegan_white_filters.sort()
        self.irrelevant_non_matching_category_articles = []
        self.category_name_index = column_index_mapping["category_name"]
        self.merchant_name_index = column_index_mapping["merchant_name"]
        self.column_id_mapping = column_index_mapping

        if relevancy_filter:
            self.save_dir = "/home/graphn/repositories/you_conscious/dl_xp/trained_model/relevancy"
            self.model = Inferencer.load(self.save_dir, gpu=True)
        try:
            pass
            self.label_index_feature_datafeed = get_headers_index("Labels",file_paths["filtered_data_feed_path"])
            self.description_index = get_headers_index("description", file_paths["filtered_data_feed_path"], "\t")

        except ValueError:
            pass

    def is_article_vegan(self, article: list) -> Union[None, list]:
        """
        :param article: Article's line in a list format
        :return: The article's line if it is vegan
        """
        tmp_article = article
        article = " ".join(article)
        article_words: list = []

        for info in tokenizer.tokenize(article):
            _, token, _ = info
            if token is not None:
                article_words.append(token.lower())

        article_words = sorted(set(article_words))
        article_words = list(article_words)

        # todo bag affaire has in common a black filter
        vegan = bool
        # Black Filters
        for filter_veg_black in self.vegan_black_filters:
            filter_veg_black = filter_veg_black.lower()
            filter_veg_black = filter_veg_black.split(" ")
            if len(set(filter_veg_black).intersection(article_words)) == len(filter_veg_black):
                vegan = False
                break
        # White Filters
        for filter_veg_white in self.vegan_white_filters:
            filter_veg_white = filter_veg_white.lower()
            filter_veg_white = filter_veg_white.split(" ")
            if len(set(filter_veg_white).intersection(article_words)) == len(filter_veg_white):
                vegan = True
                break

        if vegan:
            return tmp_article

    def is_article_not_vegan(self, article: list) -> Union[None, list]:
        """
        :param article: Article's line in a list format
        :return: The article's line if it is vegan
        """
        # vegan: bool = bool()
        tmp_article = article
        article = " ".join(article)
        article_words = sorted(set(word_tokenize(article.replace(",", " "))))
        article_words = list(article_words)
        vegan = True
        for filter_veg in self.vegan_black_filters:
            filter_veg = filter_veg.split(" ")
            if len(set(filter_veg).intersection(article_words)) == len(filter_veg):
                vegan = False

                break
        for filter_white in self.vegan_white_filters:
            filter_veg = filter_white.split(" ")
            if len(set(filter_veg).intersection(article_words)) == len(filter_veg):
                vegan = True
                return tmp_article
        if not vegan:
            return tmp_article

    def get_list_vegan_articles(self, list_articles) -> list:
        """
        Iteration over all article in the list and create list of vegan article filtered with the filters
        :param list_articles: list of all articles
        """
        with Pool(processes=16) as p:
            result_vegan = list(tqdm.tqdm(p.imap(self.is_article_vegan, list_articles), total=len(list_articles)))

        return result_vegan

    def remove_article_with_no_label(self, article: list) -> list:
        """
        :param article: Article in a list format
        :return: Return the article if it has a label
        """
        material_index_feature_datafeed = get_headers_index("Material",
                                                            file_paths["featured_affiliateIds_datafeed_path"])

        if article[self.label_index_feature_datafeed] or article[material_index_feature_datafeed] != "":

            return article
        else:
            a = article

            a = a

    def remove_articles_with_no_label(self, list_articles: list) -> list:
        with Pool(processes=8) as p:
            list_articles_with_label = list(tqdm.tqdm(p.imap(self.remove_article_with_no_label, list_articles),
                                                      total=len(list_articles), desc="Deleting article without label"))

        return list_articles_with_label

    def delete_non_matching_category(self, article: list) -> list:
        """
        Does not return an article if Damen or Herren is not in the category_name
        :param article: Article to be processed
        :return: Article if Herren or Damen is in the category_name
        """
        category_name_index = get_headers_index("category_name", file_paths["cleansed_sex_data_feed_path"])

        category_name_content: str = article[category_name_index]
        category_name_content_tokens: list = get_tokens(category_name_content)
        to_return: bool = False

        if "Herren" in category_name_content_tokens:
            to_return = True
        if "Damen" in category_name_content_tokens:
            to_return = True
        if to_return:
            return article
        if not to_return:
            article[self.category_name_index] = "irrelevant"
            print(category_name_content_tokens)
            return article

    def delete_non_matching_categories(self, list_articles: list) -> list:
        with Pool(processes=16) as p:
            deleted_non_matching_categories: list = list(
                tqdm.tqdm(p.imap(self.delete_non_matching_category, list_articles),
                          total=len(list_articles), desc="Deleting non matching categories"))

        return deleted_non_matching_categories

    def delete_not_in_stock_articles(self, list_articles: list) -> list:
        with Pool(processes=16) as p:
            in_stock_articles: list = list(
                tqdm.tqdm(p.imap(self.delete_not_in_stock_article, list_articles),
                          total=len(list_articles), desc="Deleting not in stock articles"))
        list_articles_with_stock = []
        for i, article_stock_status in tqdm.tqdm(enumerate(list_articles), total=len(in_stock_articles)):
            if article_stock_status is not None:
                list_articles_with_stock.append(list_articles[i])
        return list_articles_with_stock

    def delete_not_in_stock_article(self, article: list):
        stock_status_content = article[self.column_id_mapping["stock_status"]]
        quantity_status_content = article[self.column_id_mapping["stock_quantity"]]
        to_return = True

        if "Nicht verfügbar" in stock_status_content:
            to_return = False
        if "out of stock" in stock_status_content:
            to_return = False
        if to_return == True:
            return stock_status_content
        if "0.00" in quantity_status_content:
            to_return = False


def filter_data_feed():
    fltr = Filter(relevancy_filter=False)
    print("Filtering script has begun ")
    print("List filters has been created.")
    print("Filtering: Remove articles not in stock : Begin")
    df = pd.read_csv(merged_data_feed_path, sep="\t", low_memory=False)
    df = df.rename(columns={'shop': 'merchant_name'})
    df = df[~df['stock_status'].isin(["Nicht verfügbar", "out of stock", "0.00", "0"])]
    df = df[~df['stock_quantity'].isin(["Nicht verfügbar", "out of stock", "0.00", "0"])]
    df = df[~df['in_stock'].isin(["Nicht verfügbar", "out of stock", "0.00", "0"])]
    df.to_csv(merged_data_feed_path, sep="\t")
    del df
    print("Filtering: Remove articles not in stock : End")
    list_articles = get_lines_csv(merged_data_feed_path, "\t")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("List of articles has been created")
    print("Filtering - filtering: Begin")
    list_articles = fltr.get_list_vegan_articles(list_articles)
    print("Filtering - filtering: Done")
    list_articles = [headers] + list_articles
    write_2_file(list_articles, file_paths["filtered_data_feed_path"])
    print("Filtering: Done")


def get_articles_with_label():
    fltr = Filter(relevancy_filter=False)
    list_articles = get_lines_csv(file_paths["featured_affiliateIds_datafeed_path"], "\t")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("Filtering - remove articles without label: Begin")
    list_articles_with_label = fltr.remove_articles_with_no_label(list_articles)
    print("Filtering - remove articles without label: End")
    list_articles_with_label = [headers] + list_articles_with_label
    write_2_file(list_articles_with_label, file_paths["labeled_data_feed_path"])
    print("Removed all articles without label")


def delete_non_matching_categories():
    flt = Filter(relevancy_filter=False)
    print("Delete non matching categories : Begin")
    list_articles = get_lines_csv(file_paths["cleansed_sex_data_feed_path"], "\t")
    print(len(list_articles))

    headers = list_articles[0]
    list_articles = list_articles[1:]
    deleted_non_matching_categories_articles = flt.delete_non_matching_categories(
        list_articles)
    deleted_non_matching_categories_articles = [headers] + deleted_non_matching_categories_articles
    write_2_file(deleted_non_matching_categories_articles, done_datafeed,
                 "\t")
    # irrelevant_non_matching_category_articles = [item for item in list_articles if item not in deleted_non_matching_categories_articles]
    # write_2_file(irrelevant_non_matching_category_articles, "irrelevant_articles.csv", "\t")
    # sort dataframe by
    #df = pd.read_csv(done_datafeed, sep="\t", low_memory=False)
    #df.sort_values(by=['aw_deep_link'])
    #df.to_csv(done_datafeed, sep="\t")
    #print(len(df))
    print("Delete non matching categories : Done")
