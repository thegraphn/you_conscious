import os
import sys

import tqdm

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/data_processing/cleansing_datafeed", "")
print("+++++",folder)
sys.path.append(folder)
import datetime
from collections import defaultdict
from multiprocessing import Pool
from data_processing.data_processing.utils.merchant_ean_ranking import ranking_merchant_ean
from data_processing.data_processing.filter_datafeed.utils import replace_merchant_names_ean_order

from data_processing.data_processing.cleansing_datafeed.config import merchant_to_identifier

import pandas as pd
from data_processing.data_processing.utils import file_paths
from data_processing.data_processing.utils.utils import create_mapping_between_2_columns, \
    files_mapping_categories_path, \
    mapping_fashionSuitableFor, synonym_female, synonym_male, synonym_euro, get_mapping_column_index, \
    MAX_NUM_FASHION_SIZE_COLUMNS, get_lines_csv, write_2_file, get_tokens
from data_processing.data_processing.utils.getHeaders import get_headers_index
from data_processing.data_processing.utils.columns_order import column_index_mapping
from data_processing.data_processing.cleansing_datafeed.utils import clean_category_sex, clean_size, \
    check_if_relevant_ean_merchant_is_present, sort_ean_merchant
from data_processing.data_processing.cleansing_datafeed.size_finder import SizeFinder
from data_processing.data_processing.cleansing_datafeed.size_sorter import SizeSorter
class Cleanser:
    def __init__(self):
        self.input_data_feed: str = file_paths["labeled_data_feed_path"]
        self.category_name_cleansing: str = file_paths["category_name_cleansing"]
        self.category_name_cleansing_conditions: list = get_lines_csv(self.category_name_cleansing, ",")[1:]
        self.data = pd.read_csv(self.input_data_feed, low_memory=False, sep="\t")
        self.columns = list(self.data.columns)
        self.column_2_id = {column: i for i, column in enumerate(self.columns)}
        self.feature_mapping = create_mapping_between_2_columns(files_mapping_categories_path, 1, 2, ",")
        self.fashionSuitableFor_mapping = create_mapping_between_2_columns(mapping_fashionSuitableFor, 2, 6, ";")
        self.category_name_index = get_headers_index("category_name")
        self.description_index = get_headers_index("description")
        self.fashionSuitableFor_index = get_headers_index("Fashion:suitable_for")
        self.rrp_price_index = get_headers_index("rrp_price", file=self.input_data_feed)
        self.keyword_index = get_headers_index("keyword", file=self.input_data_feed)

        self.delivery_cost_index = get_headers_index("delivery_cost", file=self.input_data_feed)
        self.search_price_index = get_headers_index("search_price", file=self.input_data_feed)
        self.merchantName_index = self.column_2_id[
            "merchant_name"]  # get_headers_index("merchant_name", file=self.input_data_feed)
        self.title_index = get_headers_index("Title", file=self.input_data_feed)
        self.merchant_product_id_index = get_headers_index("merchant_product_id", file=self.input_data_feed)
        self.colour_index = get_headers_index("colour", file=self.input_data_feed)
        self.aw_deep_link_index = get_headers_index("aw_deep_link", file=self.input_data_feed)
        self.item_id_index = get_headers_index("item_id", file=self.input_data_feed)
        self.model_path_categories = "/home/graphn/repositories/you_conscious/dl_xp/trained_models/category_experiment_2021_04_03"
        self.model_path_colors = "/home/graphn/repositories/you_conscious/dl_xp/trained_models/color"
        self.model_path_saison = "/home/graphn/repositories/you_conscious/dl_xp/trained_models/saison"
        self.model_path_origin = "/home/graphn/repositories/you_conscious/dl_xp/trained_models/origin"
        self.model_path_keywords = "/home/graphn/repositories/you_conscious/dl_xp/trained_models/keywords"
        self.column_features = ["brand",
                                "merchant_name",
                                "Fashion:suitable_for",
                                "Title",
                                "description"]
        self.column_features_keywords = ["Title"]
        self.column_features_origin = ["Title", "description"]
        self.column_id_mapping = column_index_mapping
        self.unwanted_replacement_string = {"<div>": "", "<ul>": "", "<li>": "|", "<span>": "", "</span>": "",
                                            "<br>": "|", "</li>": "", "</ul>": "", "</div>": "",
                                            "&lt;/div&gt;": "", "&lt;div&gt;": "", "&lt;ul&gt;": "", "&lt;li&gt;": "",
                                            "&lt;span&gt;": "", "&lt;/span&gt;": "", "&lt;br&gt;": "",
                                            "&lt;/li&gt;": "", "&lt;/ul&gt;": ""
                                            }

    def article_cleansing(self, article: list) -> list:
        """
        Cleansing of the category_name, merchant_name, fashion suitable for
        The content in title will also be cleansed. The size, which can be in the title, must be deleted.
        :param article: Article will be cleansed
        :return:
        """

        # category_name cleansing
        content_category_name = article[self.category_name_index]
        content_category_tokens: list = get_tokens(content_category_name)
        for string2find, new_category in self.feature_mapping.items():
            if string2find in content_category_name:
                article[self.category_name_index] = new_category
        article[self.category_name_index] = clean_category_sex(article)

        # Change the content within Topman category to man
        if "Topman" in article[self.merchantName_index] or "Uli Schott":
            article[self.category_name_index]: str = article[self.category_name_index].replace("Damen", "Herren")

        # The content in title is stronger than in fashion_suitable:for and fsf in stronger than category_name
        # Title > fashion_suitable:for > category_name
        title_content: str = article[self.title_index]
        title_tokens: list = get_tokens(title_content)
        fashion_suitable_for_content = article[self.fashionSuitableFor_index]
        fashion_suitable_for_tokens: list = get_tokens(fashion_suitable_for_content)

        for female_token in synonym_female:
            if female_token in title_tokens:
                article[self.category_name_index]: str = article[self.category_name_index].replace("Herren", "Damen")
                article[self.fashionSuitableFor_index] = "Damen"
                break
            if female_token in fashion_suitable_for_tokens:
                if "Herren" in article[self.category_name_index]:
                    article[self.category_name_index]: str = article[self.category_name_index].replace("Herren",
                                                                                                       "Damen")

        for male_token in synonym_male:
            if male_token in title_tokens:
                article[self.category_name_index]: str = article[self.category_name_index].replace("Damen", "Herren")
                article[self.fashionSuitableFor_index] = "Herren"
                break
            if male_token in fashion_suitable_for_tokens:
                if "Damen" in article[self.category_name_index]:
                    article[self.category_name_index]: str = article[self.category_name_index].replace("Damen",
                                                                                                       "Herren")

        # Clean fashion_suitable_:for
        if "Female" == article[self.fashionSuitableFor_index]:
            article[self.fashionSuitableFor_index] = "Damen"
        if "Male" == article[self.fashionSuitableFor_index]:
            article[self.fashionSuitableFor_index] = "Herren"
        # merchant_name cleansing
        article[self.merchantName_index] = article[self.merchantName_index].replace(" DE", "")

        # title cleansing
        article = self.cleansing_title(article)

        # category name cleansing
        article = self.cleansing_category_names(article, content_category_tokens)

        # description cleansing
        article[self.description_index] = self.cleansing_description(article[self.description_index])

        # in_stock cleansing
        if article[self.column_id_mapping["in_stock"]] == "1":
            article[self.column_id_mapping["in_stock"]] = "Ja"
        if article[self.column_id_mapping["stock_status"]] == "JA" or article[self.column_id_mapping
        ["stock_status"]] == "in stock":
            article[self.column_id_mapping["stock_status"]] = "Verfügbar"
        return article

    def cleansing_description(self, description: str) -> str:
        """
        Cleanse a description
        :param description:
        :return:
        """
        for string_to_find, replacement in self.unwanted_replacement_string.items():
            description = description.replace(string_to_find, replacement)
        return description

    def cleansing_articles(self, list_vegan_articles):
        with Pool(16) as p:
            result_renamed = list(tqdm.tqdm(p.imap(self.article_cleansing, list_vegan_articles),
                                            total=len(list_vegan_articles)))
        return result_renamed

    def cleansing_title(self, article) -> list:
        """
        Remove the size in the title string
        :param article:
        :return: cleansed title
        """
        title_content: str = article[self.title_index]
        size_finder: SizeFinder = SizeFinder(str_used=title_content)
        size_position = size_finder.delete_size()
        article[self.title_index] = size_position
        return article

    def cleansing_category_names(self, article: list, content_category_tokens: list) -> list:
        for condition in self.category_name_cleansing_conditions:
            frm = condition[0]
            from_category_name_condition = condition[1]
            to = condition[2]
            if frm in content_category_tokens and from_category_name_condition in content_category_tokens:
                content_category_content: str = " ".join(content_category_tokens)
                content_category_content = content_category_content.replace(frm, "")
                content_category_content = content_category_content.replace("&", "")
                article[self.category_name_index] = content_category_content.replace(frm, to)
                break
        return article

    def renaming_fashion_suitable_for(self, article) -> list:
        content_category_name = article[self.category_name_index]
        content_fashion_suitable_for = article[self.fashionSuitableFor_index]
        sex = content_category_name.split(" > ")
        if len(sex) == 0:
            sex = content_category_name.split(">")
            sex = sex[1]
            if content_fashion_suitable_for == "" or " ":
                article[self.fashionSuitableFor_index] = sex
        return article

    def renaming_fashion_suitable_for_columns(self, list_articles):
        with Pool() as p:
            result_fashion_suitable_for_renamed = list(tqdm.tqdm(p.imap(self.renaming_fashion_suitable_for,
                                                                        list_articles),
                                                                 total=(len(list_articles))))
        return result_fashion_suitable_for_renamed

    def clean_price(self, article: list) -> list:
        """

        :param article:
        :return: article
        """

        if article[self.rrp_price_index] == "0" or article[self.rrp_price_index] == "0,00" \
                or article[self.rrp_price_index] == "0.00":
            article[self.rrp_price_index] = article[self.search_price_index]
        if article[self.rrp_price_index] == "" or len(article[self.rrp_price_index]) == 0 or article[
            self.rrp_price_index] == "0.00 €" \
                or article[self.rrp_price_index] == "0.00":
            article[self.rrp_price_index] = article[self.search_price_index]
        if article[self.delivery_cost_index] == '"0,00 EUR"' or article[self.delivery_cost_index] == ''"0.00 EUR"'':
            article[self.delivery_cost_index] = "0"
        for euro_token in synonym_euro:
            if euro_token in article[self.search_price_index]:
                article[self.search_price_index]: str = article[self.search_price_index].replace(euro_token, "")
            if euro_token in article[self.rrp_price_index]:
                article[self.rrp_price_index]: str = article[self.rrp_price_index].replace(euro_token, "")
            if euro_token in article[self.delivery_cost_index]:
                article[self.delivery_cost_index]: str = article[self.delivery_cost_index].replace(euro_token, "")
        article[self.search_price_index]: str = article[self.search_price_index].replace(".", ",")
        article[self.rrp_price_index]: str = article[self.rrp_price_index].replace(".", ",")
        article[self.delivery_cost_index]: str = article[self.delivery_cost_index].replace(".", ",")
        return article

    def clean_prices(self, list_articles):
        p = Pool()
        cleaned_prices_articles = p.map(self.clean_price, list_articles)
        return cleaned_prices_articles

    def get_article_identifier(self, article: list) -> str:
        """
        Get an article identifier in order to merge articles by their sizes
        :return: identifier
        """

        if "Avocadostore" in article[self.merchantName_index]:
            merchant_product_id = article[self.merchant_product_id_index]
            split_merchant_product_id_index = merchant_product_id.split("-")
            colour: str = article[self.colour_index]
            product_identifier: str = split_merchant_product_id_index[0]
            identifier: str = product_identifier + "-" + colour
        else:
            identifier: str = "aw_image_url"
        return identifier

    def merged_product_by_size(self, input_list_articles):
        """
        Merge product by size, based on "unique" the aw_image_url.
        :param input_list_articles: List of all articles with "duplicates" by size
        :return: list_articles_merged
        """
        headers = input_list_articles[0]
        list_art = input_list_articles[1:]
        list_articles_merged = []
        mapping_identifier_sizes = defaultdict(list)
        mapping_identifier_article = {}
        mapping_column_header = get_mapping_column_index(self.input_data_feed, "\t")

        for article in list_art:

            identifier_column = merchant_to_identifier.get("EMPTY", article[self.column_id_mapping["merchant_name"]])

            size_content = article[mapping_column_header["Fashion:size"]]
            size_content = clean_size(size_content)
            stock_content = article[mapping_column_header["stock_status"]]

            if "Avocadostore" in article[self.merchantName_index]:
                merchant_product_id = article[self.merchant_product_id_index]
                split_merchant_product_id_index = merchant_product_id.split("-")
                colour: str = article[self.colour_index]
                product_identifier: str = split_merchant_product_id_index[0]
                identifier: str = product_identifier + "-" + colour
                mapping_identifier_sizes[identifier].append(
                    size_content)  # Mapping URL sizes
                mapping_identifier_article[identifier] = article  # Mapping URL article

            else:
                mapping_identifier_sizes[article[mapping_column_header[identifier_column]]].append(
                    size_content)  # Mapping URL sizes
                mapping_identifier_article[
                    article[mapping_column_header[identifier_column]]] = article  # Mapping URL article

        # Add the sizes columns to the headers
        headers = [header.replace("Fashion:size", "Fashion:size0") for header in headers]
        for i in range(1, MAX_NUM_FASHION_SIZE_COLUMNS):  # Start at one because we already use Fashion:size0
            headers.append("Fashion:size" + str(i))

        mapping_header_column_id = {header: columnId for columnId, header in enumerate(headers)}
        # Put the size into the size column
        for url, sizes in mapping_identifier_sizes.items():
            list_size: list = []
            for lt in sizes:
                for size in lt:
                    list_size.append(size)
            article = mapping_identifier_article[url]
            # Append empty rows for the new sizes column
            for i in range(MAX_NUM_FASHION_SIZE_COLUMNS):
                article.append("")
            list_size = list_size[:MAX_NUM_FASHION_SIZE_COLUMNS]
            list_size = list(set(list_size))  # remove duplicates
            size_sorter: SizeSorter = SizeSorter(list_size)
            list_size: list = size_sorter.sorted_sizes
            for i, size in enumerate(list_size):
                article[mapping_header_column_id["Fashion:size" + str(i)]] = size
            list_articles_merged.append(article)

        return [headers] + list_articles_merged



    def add_item_id(self, article: list):
        """
        Generate and add to the item_id column an item_id for every article
        :param article:
        :return: article
        """
        article[self.item_id_index] = self.aw_deep_link_index

    def ean_cleanser(self, list_articles: list) -> list:
        """

        :param list_articles:
        :return:
        """
        # if list only avocado store keep all
        list_clean_ean_articles = []
        list_index_articles_cleansed = []
        list_articles_to_return = []
        articles_index_to_return = []
        merchant_ean_to_clean = ["0Avocadostore", "1Im walking", "2mirapodo", "3OTTO"]
        ean_mapping = defaultdict(list)
        ean_relevant_merchant = ranking_merchant_ean.keys()
        ean_index = get_headers_index("ean", self.input_data_feed)
        merchant_name_index = self.merchantName_index
        for a, article in enumerate(list_articles):
            ean = article[ean_index]
            merchant_name = article[self.merchantName_index]
            if merchant_name == "ETHLETIC":
                if ean.endswith(".0"):
                    ean = ean[:-2]
            ean_mapping[ean].append({"merchant_name": replace_merchant_names_ean_order(article[merchant_name_index]),
                                     "index": a})
            list_index_articles_cleansed.append(a)

        for ean, merchants in ean_mapping.items():
            ean_cleansed = False
            if ean == str(889556801404):
                print("xx", merchants)
            length_merchant_names = len(merchants)
            list_merchant_names = [merchant["merchant_name"] for merchant in merchants]
            set_merchant_names = set(list_merchant_names)
            # print(list_merchant_names)

            if ean != "":
                if len(set(list_merchant_names).intersection(merchant_ean_to_clean)) > 0:
                    if "0Avocadostore" in list_merchant_names:
                        if len(set_merchant_names) == 1:
                            for merchant in merchants:
                                articles_index_to_return.append(merchant["index"])
                        else:
                            for merchant in merchants:
                                if merchant["merchant_name"] == "0Avocadostore":
                                    articles_index_to_return.append(merchant["index"])



                    else:
                        ordered_merchants = []
                        ord_merchants = {}
                        ordered_merchants = [merchant["merchant_name"] + "-" + str(merchant["index"]) for merchant in
                                             merchants]
                        merchant_to_return = ordered_merchants[0]
                        index_to_return = merchant_to_return.split("-")[-1]
                        index_to_return = int(index_to_return)
                        articles_index_to_return.append(index_to_return)

                else:  # length of merchant should be one
                    articles_index_to_return.append(merchants[0]["index"])


            else:
                for merchant in merchants:
                    articles_index_to_return.append(merchant["index"])
        for article_index in articles_index_to_return:
            if type(article_index) == int:
                list_articles_to_return.append(list_articles[article_index])

        return list_articles_to_return

if __name__ == '__main__':
    p = Pool()
    cleanser = Cleanser()
    print("Begin cleansing", datetime.datetime.now())
    list_articles = get_lines_csv(cleanser.input_data_feed, "\t")
    print("0", len(list_articles))

    print("Cleansing - Merging by size: Begin", datetime.datetime.now())
    list_articles = cleanser.merged_product_by_size(list_articles)
    print("00", len(list_articles))

    print("Cleansing - Merging by size: Done", datetime.datetime.now())
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("Cleansing - Renaming Categories: Begin", datetime.datetime.now())
    list_articles = list_articles
    list_articles = list(tqdm.tqdm(p.imap(cleanser.article_cleansing, list_articles),
                                   total=len(list_articles)))

    list_articles = list_articles
    print("1", len(list_articles))
    # renaming article's category and fashion suitable for

    list_articles = list(tqdm.tqdm(p.imap(cleanser.article_cleansing, list_articles),
                                   total=len(list_articles)))
    list_articles = cleanser.ean_cleanser(list_articles)