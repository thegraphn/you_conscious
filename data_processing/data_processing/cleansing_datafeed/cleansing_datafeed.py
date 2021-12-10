import os
import sys

from data_processing.data_processing.merging_datafeeds.size_merger import SizeMerger

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/data_processing/cleansing_datafeed", "")
import logging

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

sys.path.append(folder)
import datetime
from collections import defaultdict
from multiprocessing import Pool

import tqdm
from farm.infer import Inferencer

from data_processing.data_processing.cleansing_datafeed.size_finder import SizeFinder
from data_processing.data_processing.cleansing_datafeed.utils import clean_category_sex
from data_processing.data_processing.filter_datafeed.utils import replace_merchant_names_ean_order
from data_processing.data_processing.utils.columns_order import column_index_mapping
from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.getHeaders import get_headers_index
from data_processing.data_processing.utils.utils import create_mapping_between_2_columns, \
    files_mapping_categories_path, \
    mapping_fashionSuitableFor, synonym_female, synonym_male, synonym_euro, get_lines_csv, write_2_file, get_tokens
import pandas as pd

batch_size = 250


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
        self.category_name_index = self.column_2_id["category_name"]
        self.description_index = self.column_2_id["description"]
        self.fashionSuitableFor_index = self.column_2_id["Fashion:suitable_for"]
        self.rrp_price_index = self.column_2_id["rrp_price"]
        self.keyword_index = self.column_2_id["keyword"]
        self.delivery_cost_index = self.column_2_id["delivery_cost"]
        self.search_price_index = self.column_2_id["search_price"]
        self.merchantName_index = self.column_2_id["merchant_name"]
        self.title_index = self.column_2_id["Title"]
        self.merchant_product_id_index = self.column_2_id["merchant_product_id"]
        self.colour_index = self.column_2_id["colour"]
        self.aw_deep_link_index = self.column_2_id["aw_deep_link"]
        self.item_id_index = self.column_2_id["item_id"]
        self.model_path_categories = "/home/graphn/repository/you_conscious/dl_xp/trained_models/category_distill_v21"
        self.model_path_colors = "/home/graphn/repository/you_conscious/dl_xp/trained_models/color_distil"
        self.model_path_saison = "/home/graphn/repository/you_conscious/dl_xp/trained_models/saison"
        self.model_path_origin = "/home/graphn/repository/you_conscious/dl_xp/trained_models/origin"
        self.model_path_keywords = "/home/graphn/repository/you_conscious/dl_xp/trained_models/keywords"
        self.column_features = ["brand_name",
                                "merchant_name",
                                "Title",
                                "description"]
        self.column_features_keywords = ["Title"]
        self.column_features_origin = ["Title", "description"]
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
        # article = self.cleansing_category_names(article, content_category_tokens)

        # description cleansing
        article[self.description_index] = self.cleansing_description(article[self.description_index])

        # in_stock cleansing
        if article[self.column_2_id["in_stock"]] == "1":
            article[self.column_2_id["in_stock"]] = "Ja"
        if article[self.column_2_id["stock_status"]] == "JA" or article[self.column_2_id
        ["stock_status"]] == "in stock":
            article[self.column_2_id["stock_status"]] = "Verfügbar"
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

    def predict_categories(self, list_articles: list, ) -> list:
        """
        With a farm model we predict the categories of the articles based on relevant columns
        :param list_articles: 
        :return: list_categories with a predicted category_name
        """

        category_predicted_index = get_headers_index("category_predicted")
        list_articles_with_new_categories = []
        list_column_features = self.column_features
        headers = self.columns  # list_articles[0]
        interesting_data = []
        list_index_interesting_data = []
        for i, header in enumerate(headers):
            if header in list_column_features:
                list_index_interesting_data.append(i)
        list_articles = list_articles[1:]  # skip headers
        for article in list_articles:
            article_data = []
            for position in list_index_interesting_data:
                article_data.append(article[position])
            article_data = " [SEP] ".join(article_data)
            interesting_data.append({"text": article_data})

        interesting_data = interesting_data[1:]  # skip headers
        model = Inferencer.load(self.model_path_categories, batch_size=batch_size, gpu=True,
                                task_type="text_classification",
                                disable_tqdm=True, use_fast=True)
        results = model.inference_from_dicts(dicts=interesting_data)
        prediction_position = 0
        for i, predictions in enumerate(results):
            for prediction in predictions["predictions"]:
                prediction_position += 1
                label = prediction["label"]
                list_articles[prediction_position][category_predicted_index] = label
                list_articles_with_new_categories.append(list_articles[prediction_position])
        return list_articles_with_new_categories  # Does not return headers

    def predict_origin(self, list_articles: list, ) -> list:
        """
        With a farm model we predict the categories of the articles based on relevant columns
        :param list_articles:
        :return: list_categories with a predicted category_name
        """

        origin_predicted_index = column_index_mapping["origin_predicted"]
        list_column_features = self.column_features_origin
        headers = self.columns  # list_articles[0]
        interesting_data = []
        list_index_interesting_data = []
        for i, header in enumerate(headers):
            if header in list_column_features:
                list_index_interesting_data.append(i)
        list_articles = list_articles[1:]  # skip headers
        for article in list_articles:
            article_data = []
            for position in list_index_interesting_data:
                article_data.append(article[position])
            article_data = " [SEP] ".join(article_data)
            interesting_data.append({"text": article_data})

        interesting_data = interesting_data[1:]  # skip headers
        model = Inferencer.load(self.model_path_origin, batch_size=batch_size, gpu=True,
                                task_type="text_classification",
                                disable_tqdm=True, use_fast=True)
        results = model.inference_from_dicts(dicts=interesting_data)
        prediction_position = 0
        for i, predictions in enumerate(results):
            for prediction in predictions["predictions"]:
                prediction_position += 1
                label = prediction["label"]
                label = label.replace('"', "")
                label = label.replace("[", "")
                label = label.replace("]", "")
                label = label.replace("'", "")
                label = label.replace(" ", "")
                labels = label.split(",")
                labels = labels[0:3]  # take the first 3 colors

                list_articles[prediction_position][origin_predicted_index] = labels[0]
        return list_articles

    def predict_colors(self, list_articles: list) -> list:
        color_index = get_headers_index("colour")
        colors_normalized_zero_index = get_headers_index("color_normalized_0")
        colors_normalized_one_index = get_headers_index("color_normalized_1")
        colors_normalized_two_index = get_headers_index("color_normalized_2")

        data_to_predict = []
        list_articles_with_new_colors = []
        for article in list_articles:
            if len(article[color_index]) == 0:
                color_text = "NO_COLOR"
            else:
                color_text = article[color_index]
            data_to_predict.append({"text": color_text})

        data_to_predict = data_to_predict[1:]  # skip headers
        model = Inferencer.load(self.model_path_colors, batch_size=batch_size * 2, gpu=True,
                                task_type="text_classification",
                                disable_tqdm=True, use_fast=True)
        results = model.inference_from_dicts(dicts=data_to_predict)
        prediction_position = 0
        for i, predictions in enumerate(results):
            for prediction in predictions["predictions"]:
                prediction_position += 1
                label = prediction["label"]
                label = label.replace('"', "")
                label = label.replace("[", "")
                label = label.replace("]", "")
                label = label.replace("'", "")
                label = label.replace(" ", "")
                labels = label.split(",")
                labels = labels[0:3]  # take the first 3 colors

                list_articles[prediction_position][colors_normalized_zero_index] = labels[0]
                if len(labels) == 2:
                    list_articles[prediction_position][colors_normalized_one_index] = labels[1]
                if len(labels) == 3:
                    list_articles[prediction_position][colors_normalized_two_index] = labels[2]
                list_articles_with_new_colors.append(list_articles[prediction_position])
        return list_articles_with_new_colors

    def predict_saison(self, list_articles: list) -> list:
        saison_index = get_headers_index("saison")
        saison_conf_score_index = get_headers_index("saison_conf_score_index")

        list_articles_with_saison = []
        list_column_features = self.column_features
        headers = self.columns  # list_articles[0]
        interesting_data = []
        list_index_interesting_data = []
        for i, header in enumerate(headers):
            if header in list_column_features:
                list_index_interesting_data.append(i)
        list_articles = list_articles[1:]  # skip headers

        for article in list_articles:
            article_data = []
            for position in list_index_interesting_data:
                article_data.append(article[position])
            article_data = " [SEP] ".join(article_data)

            interesting_data.append({"text": article_data})
        interesting_data = interesting_data[1:]  # skip headers
        model = Inferencer.load(self.model_path_saison, batch_size=batch_size, gpu=True,
                                task_type="text_classification",
                                disable_tqdm=True, use_fast=True)
        results = model.inference_from_dicts(dicts=interesting_data)
        prediction_position = 0
        for i, predictions in enumerate(results):
            for prediction in predictions["predictions"]:
                prediction_position += 1
                label = prediction["label"]
                label = label.replace('"', "")
                label = label.replace("[", "")
                label = label.replace("]", "")
                label = label.replace("'", "")
                label = label.replace(" ", "")
                labels = label.split(",")
                labels = ",".join(labels)
                probability = prediction["probability"]
                list_articles[prediction_position][saison_conf_score_index] = probability
                list_articles[prediction_position][saison_index] = labels
                list_articles_with_saison.append(list_articles[prediction_position])
        return list_articles_with_saison  # Does not return headers

    def predict_keywords(self, list_articles: list) -> list:
        keyword_index = get_headers_index("keywords")
        hard_keywords = ["kunstleder", "lederoptik", "lederimitat"]

        list_column_features = self.column_features_keywords
        headers = self.columns  # list_articles[0]
        list_index_interesting_data = []
        for i, header in enumerate(headers):
            if header in list_column_features:
                list_index_interesting_data.append(i)

        for i, article in enumerate(list_articles):
            for hard_keyword in hard_keywords:
                if hard_keyword in article[self.column_2_id["Title"]].lower():
                    list_articles[i][self.keyword_index] = "Kunstleder"

        return list_articles

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
        list_index_articles_cleansed = []
        list_articles_to_return = []
        articles_index_to_return = []
        merchant_ean_to_clean = ["0Avocadostore", "1Im walking", "2mirapodo", "3OTTO"]
        ean_mapping = defaultdict(list)
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
            list_merchant_names = [merchant["merchant_name"] for merchant in merchants]
            set_merchant_names = set(list_merchant_names)
            if set_merchant_names == {"Le Shop Vegan"}:
                for merchant in merchants:
                    articles_index_to_return.append(merchant["index"])
            if ean != "" or ean != "nan":

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

    def articles_cleansing(self, list_articles):

        x = [self.article_cleansing(article) for article in
             tqdm.tqdm(list_articles, total=len(list_articles), desc="article cleansing")]

        return x


def cleansing():
    cleanser = Cleanser()

    print("Begin cleansing", datetime.datetime.now())
    list_articles = get_lines_csv(cleanser.input_data_feed, "\t")
    print("0", len(list_articles))

    headers = list_articles[0]  # list_articles[0]
    list_articles = list_articles[1:]
    print("Cleansing - Renaming Categories: Begin", datetime.datetime.now())
    list_articles = cleanser.articles_cleansing(list_articles)
    print("1", len(list_articles))
    # renaming article's category and fashion suitable for

    write_2_file(list_articles, "ean.tsv")

    print("Cleansing - Renaming Categories: Done", datetime.datetime.now())

    print("Cleansing - Renaming Categories DL: Begin", datetime.datetime.now())
    list_articles = cleanser.predict_categories([headers] + list_articles)

    print("Cleansing - Renaming Categories DL: Done", datetime.datetime.now())

    print("Cleansing - Renaming Colors DL: Begin", datetime.datetime.now())
    list_articles = cleanser.predict_colors(list_articles)

    print("Cleansing - Renaming Colors DL: Done", datetime.datetime.now())
    print("Cleansing - Adding saison DL: Begin", datetime.datetime.now())
    list_articles = cleanser.predict_saison([headers] + list_articles)
    print("Cleansing - Adding saison DL: Done", datetime.datetime.now())

    print("Cleansing - Adding keywords DL: Begin", datetime.datetime.now())

    list_articles = cleanser.predict_keywords([headers] + list_articles)
    print("Cleansing - Adding keywords DL: Done", datetime.datetime.now())

    print("Cleansing - Adding origin DL: Begin", datetime.datetime.now())
    list_articles = cleanser.predict_origin([headers] + list_articles)
    print("Cleansing - Adding origin DL: Done", datetime.datetime.now())

    print("Cleansing - Sexes and Prices: Begin")
    cleansed_fashion_suitable_for = [cleanser.renaming_fashion_suitable_for(article) for article in
                                     list_articles]  # list(
    write_2_file(cleansed_fashion_suitable_for, "cleansed.tsv")

    cleansed_prices = [cleanser.clean_price(article) for article in
                       cleansed_fashion_suitable_for]
    write_2_file(cleansed_prices, "price.tsv")

    print("Cleansing - Sexes and Prices: Done", datetime.datetime.now())
    cleansed_articles = cleansed_prices
    write_2_file(cleansed_articles, file_paths["cleansed_sex_data_feed_path"])
