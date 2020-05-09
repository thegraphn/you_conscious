from collections import defaultdict
from multiprocessing import Pool

import tqdm

from data_processing.data_processing.cleansing_datafeed.size import SizeFinder
from data_processing.data_processing.cleansing_datafeed.size_sorter import SizeSorter
from data_processing.data_processing.cleansing_datafeed.utils import clean_category_sex, clean_size
from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.getHeaders import get_header_index
from data_processing.data_processing.utils.utils import createMappingBetween2Columns, files_mapping_categories_path, \
    mapping_fashionSuitableFor, synonym_female, synonym_male, synonym_euro, get_mapping_column_index, \
    maxNumberFashionSizeColumns, get_lines_csv, write2File, cleansed_categories_data_feed_path


class Cleanser:
    def __init__(self):
        self.input_data_feed: str = file_paths["labeled_data_feed_path"]
        self.feature_mapping = createMappingBetween2Columns(files_mapping_categories_path, 1, 2, ",")
        self.fashionSuitableFor_mapping = createMappingBetween2Columns(mapping_fashionSuitableFor, 2, 6, ";")
        self.categoryName_index = get_header_index("category_name")
        self.fashionSuitableFor_index: int = get_header_index("Fashion:suitable_for")
        self.rrp_price_index: int = get_header_index("rrp_price", file=self.input_data_feed)
        self.delivery_cost_index: int = get_header_index("delivery_cost", file=self.input_data_feed)
        self.search_price_index: int = get_header_index("search_price", file=self.input_data_feed)
        self.merchant_name_index: int = get_header_index("merchant_name", file=self.input_data_feed)
        self.title_index: int = get_header_index("Title", file=self.input_data_feed)
        self.aw_image_url_index: int = get_header_index("aw_image_url", file=self.input_data_feed)
        self.merchant_product_id_index: int = get_header_index("product_merchant_id", file=self.input_data_feed)
        self.colour_index: int = get_header_index("colour", file=self.input_data_feed)

    def article_cleansing(self, article) -> list:
        """
        First cleansing of the category_name
        After we cleanse the merchant_name
        The content in title will also be cleansed. The size, which can be in the title, must be deleted.
        :param article: Article will be cleansed
        :return: article cleansed
        """

        # category_name cleansing
        content_category_name = article[self.categoryName_index]
        for string2find, new_category in self.feature_mapping.items():
            if string2find in content_category_name:
                article[self.categoryName_index] = new_category
        article[self.categoryName_index] = clean_category_sex(article)
        # Change the content within Topman category to man
        if "Topman" in article[self.merchant_name_index]:
            article[self.categoryName_index]: str = article[self.categoryName_index].replace("Damen", "Herren")

        # The content in title in stronger than in fashion_suitable:for and fsf in stronger than category_name
        # Title > fashion_suitable:for > category_name
        for female_token in synonym_female:
            if female_token in article[self.title_index]:
                article[self.categoryName_index]: str = article[self.categoryName_index].replace("Herren", "Damen")
                article[self.fashionSuitableFor_index] = "Damen"
                break
            if female_token in article[self.fashionSuitableFor_index]:
                if "Herren" == article[self.categoryName_index]:
                    article[self.categoryName_index]: str = article[self.categoryName_index].replace("Herren", "Damen")

        for male_token in synonym_male:
            if male_token in article[self.title_index]:
                article[self.categoryName_index]: str = article[self.categoryName_index].replace("Damen", "Herren")
                article[self.fashionSuitableFor_index] = "Herren"
                break
            if male_token in article[self.fashionSuitableFor_index]:
                if "Damen" == article[self.categoryName_index]:
                    article[self.categoryName_index]: str = article[self.categoryName_index].replace("Damen", "Herren")

        # merchant_name cleansing
        article[self.merchant_name_index] = article[self.merchant_name_index].replace(" DE", "")

        # title cleansing
        article = self.cleansing_title(article)

        return article

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

    def cleansing_articles(self, list_vegan_articles):
        with Pool() as p:
            result_renamed = list(tqdm.tqdm(p.imap(self.article_cleansing, list_vegan_articles),
                                            total=len(list_vegan_articles)))
        return result_renamed

    def renamingFashionSuitableFor(self, article) -> list:
        content_category_name = article[self.categoryName_index]
        content_fashion_suitable_for = article[self.fashionSuitableFor_index]
        sex = content_category_name.split(" > ")
        if len(sex) == 0:
            sex = content_category_name.split(">")
            sex = sex[1]
            if content_fashion_suitable_for == "" or " ":
                article[self.fashionSuitableFor_index] = sex
        return article

    def renamingFashionSuitableForColumns(self, list_articles) -> list:
        with Pool() as p:
            result_fashionSuitableFor_renamed = list(tqdm.tqdm(p.imap(self.renamingFashionSuitableFor, list_articles)
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

    def get_article_id(self, article: list) -> str:
        """
        Return an article's ID. An article's id is an element making the article unique. In our case we need to merge
        for articles having the colours in common (different sizes)
            This unique thing is the url of the article.
            For avocado we need to use a different way to get an id. We cannot use the url because they change for each
            size and each colors. We can extract an id from the merchant_product_id
        :param article: article
        :return: identifier: unique string to different articles (e.g. by their colours)
        """
        identifier: str
        if "Avocadostore" in article[self.merchant_name_index]:
            product_merchant_id: str = article[self.merchant_product_id_index]
            splitted_product_merchant_id: list = product_merchant_id.split("-")
            article_part: str = splitted_product_merchant_id[0]
            colour: str = article[self.colour_index]
            identifier = article_part + "-" + colour
        else:
            identifier: str = article[self.aw_image_url_index]

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
        mapping_column_header: dict = get_mapping_column_index(self.input_data_feed, "\t")

        for article in list_art:
            size_content = article[mapping_column_header["Fashion:size"]]
            size_content = clean_size(size_content)
            identifier: str = self.get_article_id(article)
            mapping_identifier_sizes[identifier].append(
                size_content)  # Mapping URL sizes
            mapping_identifier_article[identifier] = article  # Mapping URL article
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
        renamed_category_articles = list(tqdm.tqdm(p.imap(clnsr.article_cleansing, list_articles),
                                                   total=len(list_articles)))  # clnsr.cleansing_articles(list_articles)
        renamed_category_articles = [headers] + renamed_category_articles
        write2File(renamed_category_articles, cleansed_categories_data_feed_path)
        print("Cleansing - Renaming Categories: Done")
        headers = renamed_category_articles[0]
        renamed_category_articles = renamed_category_articles[1:]
        print("Cleansing - Sexes and Prices: Begin")
        cleansed_fashion_suitable_for = list(
            tqdm.tqdm(p.imap(clnsr.renamingFashionSuitableFor, renamed_category_articles)
                      , total=(len(renamed_category_articles))))
        cleansed_prices = p.map(clnsr.cleanPrice,
                                cleansed_fashion_suitable_for)
        print("Cleansing - Sexes and Prices: Done")
        cleansed_articles = [headers] + cleansed_prices
        write2File(cleansed_articles, file_paths["cleansed_sex_data_feed_path"])
