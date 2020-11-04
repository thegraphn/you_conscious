import tokenizer
from multiprocessing import Pool
from typing import Union

from farm.infer import Inferencer
from nltk import word_tokenize
import tqdm

from data_processing.data_processing.filter_datafeed.utils import getFilters
from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.getHeaders import get_headers_index
from data_processing.data_processing.utils.utils import filters_black_file_path, get_lines_csv, merged_data_feed_path, \
    write_2_file, filters_white_file_path, get_tokens, get_mapping_column_index


class Filter:

    def __init__(self, relevancy_filter: bool):
        self.vegan_black_filters = getFilters(filters_black_file_path)
        self.vegan_black_filters.sort()
        self.vegan_white_filters = getFilters(filters_white_file_path)
        self.vegan_white_filters.sort()

        self.merchant_name_index = get_mapping_column_index(merged_data_feed_path, "\t")["merchant_name"]

        if relevancy_filter:
            self.save_dir = "/home/graphn/repositories/you_conscious/dl_xp/trained_model/relevancy"
            self.model = Inferencer.load(self.save_dir, gpu=True)
        try:

            self.label_index_feature_datafeed = get_headers_index("Labels",
                                                                  file_paths["merged_datafeed"])
            self.description_index = get_headers_index("description", merged_data_feed_path, "\t")

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
                article_words.append(token)

        article_words = sorted(set(article_words))
        article_words = list(article_words)

        # todo bag affaire has in common a black filter
        vegan = bool
        # Black Filters
        for filter_veg in self.vegan_black_filters:
            filter_veg = filter_veg.split(" ")
            if len(set(filter_veg).intersection(article_words)) == len(filter_veg):
                vegan = False
                break
        # White Filters
        for filter_veg in self.vegan_white_filters:
            filter_veg_list = filter_veg.split(" ")
            if len(set(filter_veg_list).intersection(article_words)) == len(filter_veg_list):
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

    def remove_articles_with_no_label(self, list_articles: list) -> list:
        with Pool(processes=8) as p:
            list_articles_with_label = list(tqdm.tqdm(p.imap(self.remove_article_with_no_label, list_articles),
                                                      total=len(list_articles), desc="Deleting article without label"))

        return list_articles_with_label

    @staticmethod
    def delete_non_matching_category(article: list) -> list:
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
        else:
            print(article)

    def delete_non_matching_categories(self, list_articles: list) -> list:
        with Pool(processes=16) as p:
            deleted_non_matching_categories: list = list(
                tqdm.tqdm(p.imap(self.delete_non_matching_category, list_articles),
                          total=len(list_articles), desc="Deleting non matching categories"))

        return deleted_non_matching_categories


def filter_data_feed():
    fltr = Filter(relevancy_filter=False)
    print("Filtering script has begun ")
    print("List filters has been created.")
    list_articles = get_lines_csv(merged_data_feed_path, "\t")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("List of articles has been created")
    print("Filtering - filtering: Begin")
    list_articles_vegan = fltr.get_list_vegan_articles(list_articles)

    print("Filtering - filtering: Done")
    list_articles_vegan = [headers] + list_articles_vegan
    write_2_file(list_articles_vegan, file_paths["filtered_data_feed_path"])
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
    write_2_file(deleted_non_matching_categories_articles, file_paths["filtered_only_matching_categories_datafeed"],
                 "\t")
    print(len(deleted_non_matching_categories_articles))
    list_articles = get_lines_csv(file_paths["filtered_only_matching_categories_datafeed"], "\t")
    print(len(list_articles))
    print("Delete non matching categories : Done")
