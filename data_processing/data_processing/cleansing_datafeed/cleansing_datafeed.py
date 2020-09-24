from collections import defaultdict
from multiprocessing import Pool

import tqdm
from farm.infer import Inferencer

from data_processing.data_processing.cleansing_datafeed.size_finder import SizeFinder
from data_processing.data_processing.cleansing_datafeed.size_sorter import SizeSorter
from data_processing.data_processing.cleansing_datafeed.utils import clean_category_sex, clean_size
from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.getHeaders import getHeadersIndex
from data_processing.data_processing.utils.utils import createMappingBetween2Columns, files_mapping_categories_path, \
    mapping_fashionSuitableFor, synonym_female, synonym_male, synonym_euro, getMappingColumnIndex, \
    maxNumberFashionSizeColumns, get_lines_csv, write2File, cleansed_categories_data_feed_path, get_tokens


class Cleanser:
    def __init__(self):
        self.input_data_feed: str = file_paths["labeled_data_feed_path"]
        self.category_name_cleansing: str = file_paths["category_name_cleansing"]
        self.category_name_cleansing_conditions: list = get_lines_csv(self.category_name_cleansing, ",")[1:]
        self.feature_mapping = createMappingBetween2Columns(files_mapping_categories_path, 1, 2, ",")
        self.fashionSuitableFor_mapping = createMappingBetween2Columns(mapping_fashionSuitableFor, 2, 6, ";")
        self.categoryName_index = getHeadersIndex("category_name")
        self.fashionSuitableFor_index = getHeadersIndex("Fashion:suitable_for")
        self.rrp_price_index = getHeadersIndex("rrp_price", file=self.input_data_feed)
        self.delivery_cost_index = getHeadersIndex("delivery_cost", file=self.input_data_feed)
        self.search_price_index = getHeadersIndex("search_price", file=self.input_data_feed)
        self.merchantName_index = getHeadersIndex("merchant_name", file=self.input_data_feed)
        self.title_index = getHeadersIndex("Title", file=self.input_data_feed)
        self.merchant_product_id_index = getHeadersIndex("merchant_product_id", file=self.input_data_feed)
        self.colour_index = getHeadersIndex("colour", file=self.input_data_feed)
        self.aw_deep_link_index = getHeadersIndex("aw_deep_link",file=self.input_data_feed)
        self.item_id_index = getHeadersIndex("item_id",file=self.input_data_feed)
        self.model_path = "/home/graphn/repositories/you_conscious/dl_xp/trained_models/category"
        self.path_column_features = "/home/graphn/repositories/you_conscious/dl_xp/data/category/column_features.csv"

    # todo refactor !
    def article_cleansing(self, article: list) -> list:
        """
        Cleansing of the category_name, merchant_name, fashion suitable for
        The content in title will also be cleansed. The size, which can be in the title, must be deleted.
        :param article: Article will be cleansed
        :return:
        """

        # category_name cleansing
        content_category_name = article[self.categoryName_index]
        content_category_tokens: list = get_tokens(content_category_name)
        for string2find, new_category in self.feature_mapping.items():
            if string2find in content_category_name:
                article[self.categoryName_index] = new_category
        article[self.categoryName_index] = clean_category_sex(article)

        # Change the content within Topman category to man
        if "Topman" in article[self.merchantName_index]:
            article[self.categoryName_index]: str = article[self.categoryName_index].replace("Damen", "Herren")

        # The content in title is stronger than in fashion_suitable:for and fsf in stronger than category_name
        # Title > fashion_suitable:for > category_name
        title_content: str = article[self.title_index]
        title_tokens: list = get_tokens(title_content)
        fashion_suitable_for_content = article[self.fashionSuitableFor_index]
        fashion_suitable_for_tokens: list = get_tokens(fashion_suitable_for_content)

        for female_token in synonym_female:
            if female_token in title_tokens:
                article[self.categoryName_index]: str = article[self.categoryName_index].replace("Herren", "Damen")
                article[self.fashionSuitableFor_index] = "Damen"
                break
            if female_token in fashion_suitable_for_tokens:
                if "Herren" in article[self.categoryName_index]:
                    article[self.categoryName_index]: str = article[self.categoryName_index].replace("Herren", "Damen")

        for male_token in synonym_male:
            if male_token in title_tokens:
                article[self.categoryName_index]: str = article[self.categoryName_index].replace("Damen", "Herren")
                article[self.fashionSuitableFor_index] = "Herren"
                break
            if male_token in fashion_suitable_for_tokens:
                if "Damen" in article[self.categoryName_index]:
                    article[self.categoryName_index]: str = article[self.categoryName_index].replace("Damen", "Herren")

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

        return article

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
                article[self.categoryName_index] = content_category_content.replace(frm, to)
                break
        return article

    def renaming_fashion_suitable_for(self, article) -> list:
        content_categoryName = article[self.categoryName_index]
        content_fashionSuitableFor = article[self.fashionSuitableFor_index]
        sex = content_categoryName.split(" > ")
        if len(sex) == 0:
            sex = content_categoryName.split(">")
            sex = sex[1]
            if content_fashionSuitableFor == "" or " ":
                article[self.fashionSuitableFor_index] = sex
        return article

    def renamingFashionSuitableForColumns(self, list_articles):
        with Pool() as p:
            result_fashionSuitableFor_renamed = list(tqdm.tqdm(p.imap(self.renaming_fashion_suitable_for, list_articles)
                                                               , total=(len(list_articles))))
        return result_fashionSuitableFor_renamed

    def cleanPrice(self, article: list) -> list:
        """

        :param article:
        :return:
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
        cleaned_prices_articles = p.map(self.cleanPrice, list_articles)
        return cleaned_prices_articles

    def get_article_identifier(self, article: list) -> str:
        """
        Get an article identifier in order to merge articles by their sizes
        :return: identifier
        """

        if "Avocadostore" in article[self.merchantName_index]:
            merchant_product_id = article[self.merchant_product_id_index]
            splited_merchant_product_id_index = merchant_product_id.split("-")
            colour: str = article[self.colour_index]
            product_identifier: str = splited_merchant_product_id_index[0]
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
        mapping_column_header = getMappingColumnIndex(self.input_data_feed, "\t")

        for article in list_art:
            size_content = article[mapping_column_header["Fashion:size"]]
            size_content = clean_size(size_content)
            if "Avocadostore" in article[self.merchantName_index]:
                merchant_product_id = article[self.merchant_product_id_index]
                splited_merchant_product_id_index = merchant_product_id.split("-")
                colour: str = article[self.colour_index]
                product_identifier: str = splited_merchant_product_id_index[0]
                identifier: str = product_identifier + "-" + colour
                mapping_identifier_sizes[identifier].append(
                    size_content)  # Mapping URL sizes
                mapping_identifier_article[identifier] = article  # Mapping URL article

            else:
                mapping_identifier_sizes[article[mapping_column_header["aw_image_url"]]].append(
                    size_content)  # Mapping URL sizes
                mapping_identifier_article[
                    article[mapping_column_header["aw_image_url"]]] = article  # Mapping URL article

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
            list_size = list(set(list_size))  # remove dupiclates
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
        :param list_categories:
        :return: list_categories with a predicted category_name
        """

        list_column_features = get_lines_csv(self.path_column_features, delimiter=";")
        list_column_features = [column[0] for column in list_column_features]
        headers = get_lines_csv(self.input_data_feed, "\t")
        headers = list_articles[0]
        data = []
        interesting_data = []
        list_index_interesting_data = []
        for i, header in enumerate(headers):
            if header in list_column_features:
                list_index_interesting_data.append(i)
        for article in list_articles:
            article_data = []
            for position in list_index_interesting_data:
                article_data.append(article[position])
            article_data = " <SEP> ".join(article_data)

            interesting_data.append({"text": article_data})

        interesting_data = interesting_data[1:]  # skip headers
        model = Inferencer.load(self.model_path, batch_size=12, gpu=True)
        result = model.inference_from_dicts(dicts=interesting_data)
        for prediction, article in zip(result, list_articles):
            label = prediction["predictions"][0]["label"]
            article[self.categoryName_index] = label
        return list_articles

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
        print("Cleansing - Merging by size: Begin")
        list_articles = clnsr.merged_product_by_size(list_articles)
        print("Cleansing - Merging by size: Done")
        headers = list_articles[0]
        list_articles = list_articles[1:]
        print("Cleansing - Renaming Categories: Begin")
        list_articles = clnsr.predict_categories([headers] + list_articles)
        headers = list_articles[0]
        list_articles = list_articles[1:]
        # renaming article's category and fashion suitable for
        renamed_category_articles = list(tqdm.tqdm(p.imap(clnsr.article_cleansing, list_articles),
                                                   total=len(list_articles)))  # clnsr.cleansing_articles(list_articles)
        renamed_category_articles = [headers] + renamed_category_articles
        write2File(renamed_category_articles, cleansed_categories_data_feed_path)
        print("Cleansing - Renaming Categories: Done")
        headers = renamed_category_articles[0]
        renamed_category_articles = renamed_category_articles[1:]
        print("Cleansing - Sexes and Prices: Begin")
        cleansed_fashion_suitable_for = list(
            tqdm.tqdm(p.imap(clnsr.renaming_fashion_suitable_for, renamed_category_articles)
                      , total=(len(
                    renamed_category_articles))))  # clnsr.renamingFashionSuitableForColumns(renamed_category_articles)
        cleansed_prices = p.map(clnsr.cleanPrice,
                                cleansed_fashion_suitable_for)  # clnsr.cleanPrices(cleansed_fashion_suitable_for)
        cleansed_with_item_id = p.map(clnsr.add_item_id,cleansed_prices)
        print("Cleansing - Sexes and Prices: Done")
    cleansed_articles = [headers] + cleansed_with_item_id
    write2File(cleansed_articles, file_paths["cleansed_sex_data_feed_path"])
