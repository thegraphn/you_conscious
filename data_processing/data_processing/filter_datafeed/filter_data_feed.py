import tokenizer
from multiprocessing import Pool
from typing import Union

from farm.infer import Inferencer
from nltk import word_tokenize
import tqdm

from data_processing.data_processing.filter_datafeed.utils import getFilters
from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.getHeaders import getHeadersIndex
from data_processing.data_processing.utils.utils import filters_black_file_path, get_lines_csv, merged_data_feed_path, \
    write2File, filters_white_file_path


class Filter:

    def __init__(self):
        self.vegan_black_filters = getFilters(filters_black_file_path)
        self.vegan_black_filters.sort()
        self.vegan_white_filters = getFilters(filters_white_file_path)
        self.vegan_white_filters.sort()
        self.save_dir = "/home/graphn/repositories/you_conscious/dl_xp/trained_model/relevancy"

        self.model = Inferencer.load(self.save_dir, gpu=True, )
        try:

            self.label_index_feature_datafeed = getHeadersIndex("Labels",
                                                                file_paths["featured_affiliateIds_datafeed_path"])
            self.description_index = getHeadersIndex("description", merged_data_feed_path)

            self.merchant_name_index = getHeadersIndex("merchant_name", merged_data_feed_path)

        except:
            pass

    def is_article_vegan(self, article: list) -> Union[None, list]:
        """
        :param article: Article's line in a list format
        :param vegan_filters: List of filter to be apply in oder to know if the article is vegan or not
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
        vegan = bool

        """
        # White Filters
        for filter_veg in self.vegan_white_filters:
            filter_veg = filter_veg.split(" ")
            if len(set(filter_veg).intersection(article_words)) == len(filter_veg):
                vegan = True
                break
        if vegan:
            return tmp_article
        """
        # Black Filters
        for filter_veg in self.vegan_black_filters:
            filter_veg = filter_veg.split(" ")
            if len(set(filter_veg).intersection(article_words)) == len(filter_veg):
                vegan = False
                break
        if vegan:
            return tmp_article

    def is_article_not_vegan(self, article: list) -> Union[None, list]:
        """
        :param article: Article's line in a list format
        :param vegan_filters: List of filter to be apply in oder to know if the article is vegan or not
        :return: The article's line if it is vegan
        """
        vegan: bool = bool()
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

    def get_list_vegan_articles(self, list_articles):
        """
        Iteration over all article in the list and create list of vegan article filtered with the filters
        :param list_articles: list of all articles
        :param vegan_filters: filtered vegan articles
        """
        # with Pool(processes=8) as p:
        #   result_vegan = list(tqdm.tqdm(p.imap(self.is_article_vegan, list_articles), total=len(list_articles)))

        texts = []
        result_vegan = []
        for article in list_articles:
            texts.append({"text": " ".join(article)})
        texts = texts[0:100]
        n = 10
        texts_chunks = [texts[i * n:(i + 1) * n] for i in range((len(texts) + n - 1) // n)]
        results = []
        for text_chunk in texts_chunks:
            result = self.model.inference_from_dicts(dicts=text_chunk)
            results.append(result)
        for result in results:
            for i, prediction in enumerate(result):
                p = prediction["predictions"]
                for pp in p:

                    predicted_label = pp["label"]
                    if predicted_label == "RELEVANT":
                        result_vegan.append(list_articles[i])

        return result_vegan

    def remove_article_with_no_label(self, article: list) -> list:
        """
        :param article: Article in a list format
        :return: Return the article if it has a label
        """
        material_index_feature_datafeed = getHeadersIndex("Material",
                                                          file_paths["featured_affiliateIds_datafeed_path"])
        if article[self.label_index_feature_datafeed] or article[material_index_feature_datafeed] != "":
            return article

    def remove_articles_with_no_label(self, list_articles: list) -> list:
        with Pool(processes=8) as p:
            list_articles_with_label = list(tqdm.tqdm(p.imap(self.remove_article_with_no_label, list_articles),
                                                      total=len(list_articles)))

        return list_articles_with_label

    def delete_non_matching_category(self, article):
        """
        Does not return an article if Damen or Herren is not in the category_name
        :param article: Article to be processed
        :return: Article if Herren or Damen is in the category_name
        """
        category_name_index = getHeadersIndex("category_name", file_paths["cleansed_sex_data_feed_path"])

        category_name_content: str = article[category_name_index]
        category_name_content_tokens: list = word_tokenize(category_name_content)
        to_return: bool = False

        if "Herren" in category_name_content_tokens:
            to_return = True
        if "Damen" in category_name_content_tokens:
            to_return = True
        if to_return:
            return article

    def delete_non_matching_categories(self, list_articles: list) -> list:
        with Pool(processes=8) as p:
            deleted_non_matching_categories: list = list(
                tqdm.tqdm(p.imap(self.delete_non_matching_category, list_articles),
                          total=len(list_articles)))

        return deleted_non_matching_categories


def filter_data_feed():
    fltr = Filter()
    print("Filtering script has begun ")
    print("List filters has been created.")
    list_articles = get_lines_csv(merged_data_feed_path, ",")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("List of articles has been created")
    print("Filtering - filtering: Begin")
    list_articles_vegan = fltr.get_list_vegan_articles(list_articles)

    print("Filtering - filtering: Done")
    list_articles_vegan = [headers] + list_articles_vegan
    write2File(list_articles_vegan, file_paths["filtered_data_feed_path"])
    print("Filtering: Done")


def getArticlesWithLabel():
    fltr = Filter()
    list_articles = get_lines_csv(file_paths["featured_affiliateIds_datafeed_path"], "\t")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("Filtering - remove articles without label: Begin")
    list_articles_with_label = fltr.remove_articles_with_no_label(list_articles)
    print("Filtering - remove articles without label: End")
    list_articles_with_label = [headers] + list_articles_with_label
    write2File(list_articles_with_label, file_paths["labeled_data_feed_path"])
    print("Removed all articles without label")


def delete_non_matching_categories():
    flt = Filter()
    print("Delete non matching categories : Begin")
    list_articles = get_lines_csv(file_paths["cleansed_sex_data_feed_path"], "\t")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    deleted_non_matching_categories_articles = flt.delete_non_matching_categories(
        list_articles)
    list_articles = [headers] + deleted_non_matching_categories_articles
    write2File(list_articles, file_paths["filtered_only_matching_categories_datafeed"])
    print("Delete non matching categories : Done")
