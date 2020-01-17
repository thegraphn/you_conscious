import re
from multiprocessing.pool import Pool
import tqdm
from data_processing.add_features.getFeatures import features_list
from data_processing.utils.getHeaders import mapping_columnHeader
from data_processing.utils.utils import getLinesCSV, cleansed_sex_data_feed_path, \
    getMappingColumnIndex, write2File, features_data_feed_path, awDeepLink_index, affiliateId, \
    features_affiliateId_data_feed_path


def addFeaturesArticle(article):
    '''
    article_string = " ".join(article)
    for string2Find_feature2Write_columnFeature in features_list:
        string2Find = string2Find_feature2Write_columnFeature[0]
        feature2Write = string2Find_feature2Write_columnFeature[1]
        columnFeature = string2Find_feature2Write_columnFeature[2]
        if re.match(string2Find, article_string) is not None:
            article[mapping_columnHeader[columnFeature]] = feature2Write
            break
        elif string2Find in article_string:
            article[mapping_columnHeader[columnFeature]] = feature2Write
            break
    return article
    '''
    #todo elif first with set inters and then regex

    for cell in article:
        for string2Find_feature2Write_columnFeature in features_list:
            string2Find = string2Find_feature2Write_columnFeature[0]
            feature2Write = string2Find_feature2Write_columnFeature[1]
            columnFeature = string2Find_feature2Write_columnFeature[2]
            if re.match(string2Find, cell) is not None:
                article[mapping_columnHeader[columnFeature]] = feature2Write
                break
            elif string2Find in cell:
                article[mapping_columnHeader[columnFeature]] = feature2Write
                break
    return article


def addFeaturesArticles(list_articles):
    with Pool() as p:
        result_featuredArticles = list(tqdm.tqdm(p.imap(addFeaturesArticle, list_articles),
                                                 total=len(list_articles)))
    return result_featuredArticles


def addAffiliateIdArticle(article):
    content_awDeepLink_index = article[awDeepLink_index]
    if "https://sorbasshoes.com" in content_awDeepLink_index:
        for i, char in enumerate(content_awDeepLink_index):
            if char == "?":
                link = content_awDeepLink_index[:i] + affiliateId
                break
        article[awDeepLink_index] = link
    return article


def addAffiliateIdArticles(list_articles):
    with Pool() as p:
        result_addAffiliateIds = list(tqdm.tqdm(p.imap(addAffiliateIdArticle, list_articles),
                                                total=len(list_articles)))
    return result_addAffiliateIds


def add_features():
    print("Begin adding features")
    list_articles = getLinesCSV(cleansed_sex_data_feed_path, ",")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("Adding Features - add features: Begin")
    list_articles_with_features = addFeaturesArticles(list_articles)
    list_articles_with_features = [headers] + list_articles_with_features
    write2File(list_articles_with_features, features_data_feed_path)
    print("Adding Features - add features: Done")
    list_articles = getLinesCSV(features_data_feed_path, ",")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("Adding Features - add affiliate ids: Begin")
    list_articles_with_affiliateIds = addAffiliateIdArticles(list_articles)
    print("Adding Features - add affiliate ids: Done")
    list_articles_with_affiliateIds = [headers] + list_articles_with_affiliateIds
    write2File(list_articles_with_affiliateIds, features_affiliateId_data_feed_path)
