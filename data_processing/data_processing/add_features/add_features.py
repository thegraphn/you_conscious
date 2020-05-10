import re
from multiprocessing.pool import Pool
import tqdm

from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.getHeaders import getHeadersIndex
from data_processing.data_processing.utils.utils import get_lines_csv, getMappingColumnIndex, features_mapping_path, affiliateId, \
    features_data_feed_path, write2File


class FeaturesAdder:
    def __init__(self):
        self.input_file: str = file_paths["filtered_data_feed_path"]
        self.features_list = get_lines_csv(features_mapping_path, ";")[1:]#be aware of the header
        self.mapping_columnHeader = getMappingColumnIndex(self.input_file, "\t")
        self.awDeepLink_index = getHeadersIndex("aw_deep_link", file=self.input_file)

    def  add_features_article(self, article) -> list:
        """
        Iterate over "cell" in the article and search possible features.
        Add the features in the given column
        :param article: Article
        :return: Article
        """
        for cell in article:
            for string2Find_feature2Write_columnFeature in self.features_list:
                string2_find = string2Find_feature2Write_columnFeature[0]
                feature2_write = string2Find_feature2Write_columnFeature[1]
                column_feature = string2Find_feature2Write_columnFeature[2]
                if re.match(string2_find, cell) is not None:
                    article[self.mapping_columnHeader[column_feature]] = feature2_write
                    break
                elif string2_find in cell:
                    article[self.mapping_columnHeader[column_feature]] = feature2_write
                    break
        return article

    def add_features_articles(self, list_articles) -> list:
        with Pool() as p:
            result_featured_articles: list = list(tqdm.tqdm(p.imap(self.add_features_article, list_articles),
                                                            total=len(list_articles)))
        return result_featured_articles

    def add_affiliate_id_article(self, article) -> list:
        content_aw_deep_link_index: str = article[self.awDeepLink_index]
        link: str = ""
        if "https://sorbasshoes.com" in content_aw_deep_link_index:
            for i, char in enumerate(content_aw_deep_link_index):
                if char == "?":
                    link = content_aw_deep_link_index[:i] + affiliateId
                    break
            article[self.awDeepLink_index] = link
        return article

    def add_affiliate_id_articles(self, list_articles) -> list:
        with Pool() as p:
            result_add_affiliate_ids: list = list(tqdm.tqdm(p.imap(self.add_affiliate_id_article, list_articles),
                                                            total=len(list_articles)))
        return result_add_affiliate_ids


def add_features():
    with Pool() as p:
        ft_adder: FeaturesAdder = FeaturesAdder()
        print("Begin adding features")

        list_articles: list = get_lines_csv(ft_adder.input_file, "\t")
        headers: list = list_articles[0]

        list_articles = list_articles[1:]
        print("Adding Features - add features: Begin")
        list_articles_with_features: list = list(tqdm.tqdm(p.imap(ft_adder.add_features_article, list_articles),
                                                           total=len(
                                                               list_articles)))  # ft_adder.addFeaturesArticles(list_articles)
        list_articles_with_features: list = [headers] + list_articles_with_features
        write2File(list_articles_with_features, features_data_feed_path)
        print("Adding Features - add features: Done")

        list_articles: list = get_lines_csv(features_data_feed_path, "\t")
        headers: list = list_articles[0]
        list_articles: list = list_articles[1:]
        print("Adding Features - add affiliate ids: Begin")
        list_articles_with_affiliate_ids: list = list(
            tqdm.tqdm(p.imap(ft_adder.add_affiliate_id_article, list_articles),
                      total=len(
                          list_articles)))
        print("Adding Features - add affiliate ids: Done")
        list_articles_with_affiliate_ids: list = [headers] + list_articles_with_affiliate_ids
        write2File(list_articles_with_affiliate_ids, file_paths["featured_affiliateIds_datafeed_path"])
