import re
from multiprocessing.pool import Pool
import tqdm

from data_processing.utils.getHeaders import getHeadersIndex
from data_processing.utils.utils import getLinesCSV, cleansed_sex_data_feed_path, \
    getMappingColumnIndex, write2File, features_data_feed_path,  affiliateId, \
    features_affiliateId_data_feed_path, number_processes, features_mapping_path, filtered_data_feed_path


class featuresAdder:
    def __init__(self):
        self.features_list = getLinesCSV(features_mapping_path, ";")[1:]
        self.mapping_columnHeader = getMappingColumnIndex(filtered_data_feed_path,"\t")
        self.awDeepLink_index = getHeadersIndex("aw_deep_link")
    def addFeaturesArticle(self, article):
        """
        Iterate over "cell" in the article and search possible features.
        Add the features in the given column
        :param article: Article
        :return: Article
        """
        for cell in article:
            for string2Find_feature2Write_columnFeature in self.features_list:
                string2Find = string2Find_feature2Write_columnFeature[0]
                feature2Write = string2Find_feature2Write_columnFeature[1]
                columnFeature = string2Find_feature2Write_columnFeature[2]
                if re.match(string2Find, cell) is not None:
                    article[self.mapping_columnHeader[columnFeature]] = feature2Write
                    break
                elif string2Find in cell:
                    article[self.mapping_columnHeader[columnFeature]] = feature2Write
                    break
        return article

    def addFeaturesArticles(self, list_articles):
        with Pool() as p:
            result_featuredArticles = list(tqdm.tqdm(p.imap(self.addFeaturesArticle, list_articles),
                                                     total=len(list_articles)))
        return result_featuredArticles

    def addAffiliateIdArticle(self, article):
        content_awDeepLink_index = article[self.awDeepLink_index]
        if "https://sorbasshoes.com" in content_awDeepLink_index:
            for i, char in enumerate(content_awDeepLink_index):
                if char == "?":
                    link = content_awDeepLink_index[:i] + affiliateId
                    break
            article[self.awDeepLink_index] = link
        return article

    def addAffiliateIdArticles(self, list_articles):
        with Pool() as p:
            result_addAffiliateIds = list(tqdm.tqdm(p.imap(self.addAffiliateIdArticle, list_articles),
                                                    total=len(list_articles)))
        return result_addAffiliateIds


def add_features():
    ft_adder = featuresAdder()
    print("Begin adding features")
    list_articles = getLinesCSV(cleansed_sex_data_feed_path, "\t")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("Adding Features - add features: Begin")
    list_articles_with_features = ft_adder.addFeaturesArticles(list_articles)
    list_articles_with_features = [headers] + list_articles_with_features
    write2File(list_articles_with_features, features_data_feed_path)
    print("Adding Features - add features: Done")
    list_articles = getLinesCSV(features_data_feed_path, "\t")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("Adding Features - add affiliate ids: Begin")
    list_articles_with_affiliateIds = ft_adder.addAffiliateIdArticles(list_articles)
    print("Adding Features - add affiliate ids: Done")
    list_articles_with_affiliateIds = [headers] + list_articles_with_affiliateIds
    write2File(list_articles_with_affiliateIds, features_affiliateId_data_feed_path)
