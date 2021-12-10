"""Adding feature Class"""
from multiprocessing.pool import Pool
import tqdm


from data_processing.data_processing.utils.columns_order import column_index_mapping
from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.getHeaders import get_headers_index
from data_processing.data_processing.utils.utils import get_lines_csv, \
    get_mapping_column_index, features_mapping_path, \
    affiliate_id_sorbas, \
    features_data_feed_path, write_2_file, affiliate_id_le_shop_vegan


class FeaturesAdder:
    """Add feature Class"""

    def __init__(self):
        self.input_file: str = file_paths["filtered_data_feed_path"]
        self.features_list = get_lines_csv(features_mapping_path, ";")[1:]  # be aware of the header
        self.mapping_column_header = get_mapping_column_index(self.input_file, "\t")
        self.aw_deep_link_index = column_index_mapping["aw_deep_link"]
        self.all_labels_index = get_headers_index("Labels", file=self.input_file)

    def add_features_article(self, article: list) -> list:
        """
        Iterate over "cell" in the article and search possible features.
        Add the features in the given column
        :param article: Article
        :return: Article
        """
        txt_article = " ".join(article).lower()

        for string_2_find_feature_2_write_column_feature in self.features_list:

            string2_find = string_2_find_feature_2_write_column_feature[0].lower()
            feature2_write = string_2_find_feature_2_write_column_feature[1]
            column_feature = string_2_find_feature_2_write_column_feature[2]
            if string2_find in txt_article:
                article[self.mapping_column_header[column_feature]] = feature2_write
                article[self.mapping_column_header["Labels"]] += feature2_write

        return article

    def add_affiliate_id_article(self, article) -> list:
        content_aw_deep_link_index: str = article[self.mapping_column_header["aw_deep_link"]]

        if "https://sorbasshoes.com" in content_aw_deep_link_index:
            link: str = ""
            for i, char in enumerate(content_aw_deep_link_index):
                if char == "?":
                    link = content_aw_deep_link_index[:i] + affiliate_id_sorbas
                    break
            article[self.mapping_column_header["aw_deep_link"]] = link
            return article
        if "le-shop-vegan.de" in content_aw_deep_link_index:
            link = content_aw_deep_link_index + "?sPartner=1207wrt2107"
            article[self.mapping_column_header["aw_deep_link"]] = link

            return article
        return article

    def add_affiliate_id_articles(self, list_articles) -> list:
        with Pool(processes=16) as pool:
            result_add_affiliate_ids: list = list(tqdm.tqdm(pool.imap(
                self.add_affiliate_id_article, list_articles),
                total=len(list_articles)))
        return result_add_affiliate_ids


def add_features():
    ft_adder: FeaturesAdder = FeaturesAdder()

    with Pool(processes=16) as p:
        print("Begin adding features")

        list_articles: list = get_lines_csv(ft_adder.input_file, "\t")
        headers: list = list_articles[0]

        list_articles = list_articles[1:]
        print("Adding Features - add features: Begin")
        list_articles_with_features: list = list(tqdm.tqdm(p.imap(
            ft_adder.add_features_article, list_articles),
            total=len(
                list_articles),
            desc="Adding features"))
        list_articles_with_features: list = [headers] + list_articles_with_features
        print("Adding Features - add features: Done")
    write_2_file(list_articles_with_features, features_data_feed_path)

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
        write_2_file(list_articles_with_affiliate_ids,
                     file_paths["featured_affiliateIds_datafeed_path"])
