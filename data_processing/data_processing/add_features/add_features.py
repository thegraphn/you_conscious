import re
from multiprocessing.pool import Pool
import tqdm

from data_processing.data_processing.utils.columns_order import column_index_mapping
from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.utils import get_lines_csv, get_mapping_column_index, features_mapping_path, \
    affiliateId, \
    features_data_feed_path, write_2_file


class FeaturesAdder:
    def __init__(self):
        self.input_file: str = file_paths["filtered_data_feed_path"]
        self.features_list = get_lines_csv(features_mapping_path, ";")[1:]  # be aware of the header
        self.mapping_columnHeader = get_mapping_column_index(self.input_file, "\t")
        self.awDeepLink_index = column_index_mapping["aw_deep_link"]
        self.label_zero_index = column_index_mapping["label_0"]
        self.label_one_index = column_index_mapping["label_1"]
        self.label_two_index = column_index_mapping["label_2"]
        self.label_three_index = column_index_mapping["label_3"]

    def add_features_article(self, article: list) -> list:
        """
        Iterate over "cell" in the article and search possible features.
        Add the features in the given column
        :param article: Article
        :return: Article
        """
        txt_article = " ".join(article)
        list_label_features = set()
        for string2Find_feature2Write_columnFeature in self.features_list:
            string2_find = string2Find_feature2Write_columnFeature[0]
            feature2_write = string2Find_feature2Write_columnFeature[1]
            column_feature = string2Find_feature2Write_columnFeature[2]

            if column_feature == "Labels":
                if string2_find in txt_article:
                    article[self.mapping_columnHeader[column_feature]] += feature2_write
                    list_label_features.add(feature2_write)
            if column_feature != "Labels":
                if string2_find in txt_article:
                    article[self.mapping_columnHeader[column_feature]] = feature2_write
                elif re.match(string2_find, txt_article) is not None:
                    article[self.mapping_columnHeader[column_feature]] = feature2_write
        list_label_features = list(list_label_features)

        if len(list_label_features) > 0:
            if len(list_label_features) > 0:
                article[self.label_zero_index] = list_label_features[0]
            if len(list_label_features) > 1:
                article[self.label_one_index] = list_label_features[1]
            if len(list_label_features) > 2:
                article[self.label_two_index] = list_label_features[2]
            if len(list_label_features) > 3:
                article[self.label_three_index] = list_label_features[3]
        return article

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
        with Pool(processes=16) as p:
            result_add_affiliate_ids: list = list(tqdm.tqdm(p.imap(self.add_affiliate_id_article, list_articles),
                                                            total=len(list_articles)))
        return result_add_affiliate_ids


def add_features():
    ft_adder: FeaturesAdder = FeaturesAdder()

    with Pool(processes=16) as p:
        print("Begin adding features")

        list_articles: list = get_lines_csv(ft_adder.input_file, "\t")
        headers: list = list_articles[0]

        list_articles = list_articles[1:]
        list_articles = list_articles
        print("Adding Features - add features: Begin")
        list_articles_with_features: list = list(tqdm.tqdm(p.imap(ft_adder.add_features_article, list_articles),
                                                           total=len(
                                                               list_articles), desc="Adding features"))
        list_articles_with_features: list = [headers] + list_articles_with_features
        write_2_file(list_articles_with_features, features_data_feed_path)
        print("Adding Features - add features: Done")

    with Pool(processes=16) as p:
        list_articles: list = get_lines_csv(features_data_feed_path, "\t")
        headers: list = list_articles[0]
        list_articles: list = list_articles[1:]
        print("Adding Features - add affiliate ids: Begin")

        list_articles_with_affiliate_ids: list = list(
            tqdm.tqdm(p.imap(ft_adder.add_affiliate_id_article, list_articles),
                      total=len(
                          list_articles), desc="Adding affiliate ids"))
        print("Adding Features - add affiliate ids: Done")
        list_articles_with_affiliate_ids: list = [headers] + list_articles_with_affiliate_ids
        write_2_file(list_articles_with_affiliate_ids, file_paths["featured_affiliateIds_datafeed_path"])
