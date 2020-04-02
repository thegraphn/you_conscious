from multiprocessing import Pool
from typing import Union

from nltk import word_tokenize
import tqdm

from data_processing.filter_datafeed.utils import getFilters
from data_processing.utils.getHeaders import getHeadersIndex
from data_processing.utils.utils import filters_file_path, getLinesCSV, merged_data_feed_path, filtered_data_feed_path, \
    write2File, features_affiliateId_data_feed_path, labeled_data_feed_path


class Filter:

    def __init__(self):
        self.vegan_filters = getFilters(filters_file_path)
        self.vegan_filters.sort()
        try:
            self.label_index_feature_datafeed = getHeadersIndex("Labels", features_affiliateId_data_feed_path)
            self.material_index_feature_datafeed = getHeadersIndex("Material", features_affiliateId_data_feed_path)
        except:
            pass

    def isArticleVegan(self, article: list) -> Union[None, list]:
        """
        :param article: Article's line in a list format
        :param vegan_filters: List of filter to be apply in oder to know if the article is vegan or not
        :return: The article's line if it is vegan
        """
        vegan: bool = bool
        tmp_article = article
        article = " ".join(article)
        article_words = sorted(set(word_tokenize(article.replace(",", " "))))
        article_words = list(article_words)
        vegan = True
        for filter_veg in self.vegan_filters:
            filter_veg = filter_veg.split(" ")


            if "Fritzi aus Preußen" in article:
                if len(set(filter_veg).intersection(article_words)) == len(filter_veg):
                    vegan = False
                    print(filter_veg)



            if len(set(filter_veg).intersection(article_words)) == len(filter_veg):
                vegan = False
                break
        if vegan:
            return tmp_article

    def getListVeganArticles(self, list_articles):
        """
        Iteration over all article in the list and create list of vegan article filtered with the filters
        :param list_articles: list of all articles
        :param vegan_filters: filtered vegan articles
        """
        with Pool() as p:
            result_vegan = list(tqdm.tqdm(p.imap(self.isArticleVegan, list_articles), total=len(list_articles)))
        return result_vegan

    def removeArticleWithNoLabel(self, article: list) -> list:
        """
        :param article: Article in a list format
        :return: Return the article if it has a label
        """

        if article[self.label_index_feature_datafeed] or article[self.material_index_feature_datafeed] != "":
            return article

    def removeArticlesWithNoLabel(self, list_articles: list) -> list:
        with Pool() as p:
            list_articles_with_label = list(tqdm.tqdm(p.imap(self.removeArticleWithNoLabel, list_articles),
                                                      total=len(list_articles)))

        return list_articles_with_label


def filter_data_feed():
    fltr = Filter()
    print("Filtering script has begun ")
    print("List filters has been created.")
    list_articles = getLinesCSV(merged_data_feed_path, ",")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("List of articles has been created")
    print("Filtering - filtering: Begin")
    list_articles_vegan = fltr.getListVeganArticles(list_articles)
    print("Filtering - filtering: Done")
    list_articles_vegan = [headers] + list_articles_vegan
    write2File(list_articles_vegan, filtered_data_feed_path)
    print("Filtering: Done")


def getArticlesWithLabel():
    fltr = Filter()
    list_articles = getLinesCSV(features_affiliateId_data_feed_path, "\t")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("Filtering - remove articles without label: Begin")
    list_articles_withLabel = fltr.removeArticlesWithNoLabel(list_articles)
    print("Filtering - remove articles without label: End")
    list_articles_withLabel = [headers] + list_articles_withLabel
    write2File(list_articles_withLabel, labeled_data_feed_path)
    print("Removed all articles without label")
