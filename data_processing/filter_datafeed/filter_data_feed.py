from multiprocessing import Pool

from nltk import word_tokenize
import tqdm

from data_processing.filter_datafeed.utils import getFilters
from data_processing.utils.utils import filters_file_path, getLinesCSV, merged_data_feed_path, filtered_data_feed_path, \
    write2File,  features_affiliateId_data_feed_path, labeled_data_feed_path, \
    number_processes, label_features_affiliateId_data_feed_path_index, \
    material_features_affiliateId_data_feed_path_index

global vegan_filters
vegan_filters = getFilters(filters_file_path)
vegan_filters.sort()


def isArticleVegan(article):
    """
    :param article: Article's line in a list format
    :param vegan_filters: List of filter to be apply in oder to know if the article is vegan or not
    :return: The article's line if it is vegan
    """
    tmp_article = article
    article = " ".join(article)
    article_words = sorted(set(word_tokenize(article.replace(",", " "))))
    article_words = list(article_words)
    vegan = True
    for filter_veg in vegan_filters:
        filter_veg = filter_veg.split(" ")
        if len(set(filter_veg).intersection(article_words)) == len(filter_veg):
            vegan = False
            break
    if vegan:
        return tmp_article


def getListVeganArticles(list_articles):
    """
    Iteration over all article in the list and create list of vegan article filtered with the filters
    :param list_articles: list of all articles
    :param vegan_filters: filtered vegan articles
    :return:
    """

    with Pool(10) as p:
        result_vegan = list(tqdm.tqdm(p.imap(isArticleVegan, list_articles), total=len(list_articles)))
    return result_vegan


def removeArticleWithNoLabel(article):
    """
    :param article: Article in a list format
    :return: Return the article if it has a label
    """
    if article[label_features_affiliateId_data_feed_path_index] or article[material_features_affiliateId_data_feed_path_index] != "":
        return article


def removeArticlesWithNoLabel(list_articles):
    with Pool(10) as p:
        list_articles_with_label = list(tqdm.tqdm(p.imap(removeArticleWithNoLabel, list_articles),
                                                  total=len(list_articles)))

    return list_articles_with_label


def filter_data_feed():
    print("Filtering script has begun ")
    print("List filters has been created.")
    list_articles = getLinesCSV(merged_data_feed_path, ",")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("List of articles has been created")
    print("Filtering - filtering: Begin")
    list_articles_vegan = getListVeganArticles(list_articles)
    print("Filtering - filtering: Done")
    list_articles_vegan = [headers] + list_articles_vegan
    write2File(list_articles_vegan, filtered_data_feed_path)
    print("Filtering: Done")


def getArticlesWithLabel():
    list_articles = getLinesCSV(features_affiliateId_data_feed_path, ",")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("Filtering - remove articles without label: Begin")
    list_articles_withLabel = removeArticlesWithNoLabel(list_articles)
    print("Filtering - remove articles without label: End")
    list_articles_withLabel = [headers] + list_articles_withLabel
    write2File(list_articles_withLabel, labeled_data_feed_path)
    print("Removed all articles without label")


if __name__ == '__main__':
    filter_data_feed()
