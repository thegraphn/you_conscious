from collections import defaultdict
from multiprocessing import Pool

import tqdm
from farm.infer import Inferencer

from data_processing.data_processing.cleansing_datafeed.size_finder import SizeFinder
from data_processing.data_processing.cleansing_datafeed.size_sorter import SizeSorter
from data_processing.data_processing.cleansing_datafeed.utils import clean_category_sex, clean_size
from data_processing.data_processing.utils.columns_order import column_index_mapping
from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.getHeaders import get_headers_index
from data_processing.data_processing.utils.utils import create_mapping_between_2_columns, \
    files_mapping_categories_path, \
    mapping_fashionSuitableFor, synonym_female, synonym_male, synonym_euro, get_mapping_column_index, \
    maxNumberFashionSizeColumns, get_lines_csv, write_2_file, get_tokens


class Cleanser:
    def __init__(self):
        self.input_data_feed: str = file_paths["labeled_data_feed_path"]
        self.category_name_cleansing: str = file_paths["category_name_cleansing"]
        self.category_name_cleansing_conditions: list = get_lines_csv(self.category_name_cleansing, ",")[1:]
        self.feature_mapping = create_mapping_between_2_columns(files_mapping_categories_path, 1, 2, ",")
        self.fashionSuitableFor_mapping = create_mapping_between_2_columns(mapping_fashionSuitableFor, 2, 6, ";")
        self.category_name_index = get_headers_index("category_name")
        self.description_index = get_headers_index("description")
        self.fashionSuitableFor_index = get_headers_index("Fashion:suitable_for")
        self.rrp_price_index = get_headers_index("rrp_price", file=self.input_data_feed)
        self.delivery_cost_index = get_headers_index("delivery_cost", file=self.input_data_feed)
        self.search_price_index = get_headers_index("search_price", file=self.input_data_feed)
        self.merchantName_index = get_headers_index("merchant_name", file=self.input_data_feed)
        self.title_index = get_headers_index("Title", file=self.input_data_feed)
        self.merchant_product_id_index = get_headers_index("merchant_product_id", file=self.input_data_feed)
        self.colour_index = get_headers_index("colour", file=self.input_data_feed)
        self.aw_deep_link_index = get_headers_index("aw_deep_link", file=self.input_data_feed)
        self.item_id_index = get_headers_index("item_id", file=self.input_data_feed)
        self.model_path_categories = "/home/graphn/repositories/you_conscious/dl_xp/trained_models/category"
        self.model_path_colors = "/home/graphn/repositories/you_conscious/dl_xp/trained_models/color"
        self.model_path_saison = "/home/graphn/repositories/you_conscious/dl_xp/trained_models/saison"
        self.column_features = ["brand",
                                "merchant_name",
                                "Fashion:suitable_for",
                                "Title",
                                "description"]
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
        with Pool() as p:
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
            if article[self.column_id_mapping["merchant_name"]] == "muso koroni" or article[
                self.column_id_mapping["merchant_name"]] == "":

                identifier_column = "aw_deep_link"
            else:
                identifier_column = "aw_image_url"
            size_content = article[mapping_column_header["Fashion:size"]]
            size_content = clean_size(size_content)
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
        for i in range(1, maxNumberFashionSizeColumns):  # Start at one because we already use Fashion:size0
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
            for i in range(maxNumberFashionSizeColumns):
                article.append("")
            list_size = list_size[:maxNumberFashionSizeColumns]
            list_size = list(set(list_size))  # remove duplicates
            size_sorter: SizeSorter = SizeSorter(list_size)
            list_size: list = size_sorter.sorted_sizes
            for i, size in enumerate(list_size):
                article[mapping_header_column_id["Fashion:size" + str(i)]] = size
            list_articles_merged.append(article)

        return [headers] + list_articles_merged

    def predict_categories(self, list_articles: list, ) -> list:
        """
        With a farm model we predict the categories of the articles based on relevant columns
        :param list_articles: 
        :return: list_categories with a predicted category_name
        """

        category_normalized_index = get_headers_index("category_normalized")
        list_articles_with_new_categories = []
        list_column_features = self.column_features
        headers = list_articles[0]
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
        model = Inferencer.load(self.model_path_categories, batch_size=24, gpu=True, task_type="text_classification",
                                disable_tqdm=True, use_fast=True)
        results = model.inference_from_dicts(dicts=interesting_data)
        prediction_position = 0
        for i, predictions in enumerate(results):
            for prediction in predictions["predictions"]:
                prediction_position += 1
                label = prediction["label"]
                list_articles[prediction_position][category_normalized_index] = label
                list_articles_with_new_categories.append(list_articles[prediction_position])
        return list_articles_with_new_categories  # Does not return headers

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
        model = Inferencer.load(self.model_path_colors, batch_size=256, gpu=True, task_type="text_classification",
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
        headers = list_articles[0]
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
        model = Inferencer.load(self.model_path_saison, batch_size=24, gpu=True, task_type="text_classification",
                                disable_tqdm=True, use_fast=True)
        results = model.inference_from_dicts(dicts=interesting_data)
        prediction_position = 0
        for i, predictions in enumerate(results):
            for prediction in predictions["predictions"]:
                prediction_position += 1
                label = prediction["label"]
                probability = prediction["probability"]
                list_articles[prediction_position][saison_conf_score_index] = probability
                list_articles[prediction_position][saison_index] = label
                list_articles_with_saison.append(list_articles[prediction_position])
        return list_articles_with_saison  # Does not return headers

    def add_item_id(self, article: list):
        """
        Generate and add to the item_id column an item_id for every article
        :param article:
        :return: article
        """
        article[self.item_id_index] = self.aw_deep_link_index


def cleansing():
    with Pool() as p:
        clnsr = Cleanser()

        print("Begin cleansing")
        list_articles = get_lines_csv(clnsr.input_data_feed, "\t")
        print("0", len(list_articles))

        print("Cleansing - Merging by size: Begin")
        list_articles = clnsr.merged_product_by_size(list_articles)
        print("00", len(list_articles))

        print("Cleansing - Merging by size: Done")
        headers = list_articles[0]
        list_articles = list_articles[1:]
        print("Cleansing - Renaming Categories: Begin")
        list_articles = list_articles
        list_articles = list(tqdm.tqdm(p.imap(clnsr.article_cleansing, list_articles),
                                       total=len(list_articles)))

        list_articles = list_articles
        print("1", len(list_articles))
        # renaming article's category and fashion suitable for

        list_articles = list(tqdm.tqdm(p.imap(clnsr.article_cleansing, list_articles),
                                       total=len(list_articles)))
        print("2", len(list_articles))

        print("Cleansing - Renaming Categories: Done")

        print("Cleansing - Renaming Categories DL: Begin")
        list_articles = clnsr.predict_categories([headers] + list_articles)

        print("Cleansing - Renaming Categories DL: Done")

        print("Cleansing - Renaming Colors DL: Begin")
        list_articles = clnsr.predict_colors(list_articles)

        print("Cleansing - Renaming Colors DL: Done")
        # write_2_file(list_articles, list_articles)
        print("Cleansing - Adding saison DL: Begin")
        list_articles = clnsr.predict_saison([headers] + list_articles)
        print("Cleansing - Adding saison DL: Done")

        print("Cleansing - Sexes and Prices: Begin")
        cleansed_fashion_suitable_for = list(
            tqdm.tqdm(p.imap(clnsr.renaming_fashion_suitable_for, list_articles),
                      total=(len(list_articles)), desc="Cleansing Fashion Suitable for"))

        cleansed_prices = list(tqdm.tqdm(p.map(clnsr.clean_price,
                                               cleansed_fashion_suitable_for), total=len(cleansed_fashion_suitable_for),
                                         desc="Cleansing Prices"))
        print("Cleansing - Sexes and Prices: Done")
    cleansed_articles = [headers] + cleansed_prices
    write_2_file(cleansed_articles, file_paths["cleansed_sex_data_feed_path"])
