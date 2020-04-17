from collections import defaultdict
from multiprocessing import Pool

import tqdm

from data_processing.cleansing_datafeed.utils import cleanSize, clean_category_sex
from data_processing.utils.file_paths import file_paths
from data_processing.utils.getHeaders import getHeadersIndex
from data_processing.utils.utils import createMappingBetween2Columns, files_mapping_categories_path, \
    getLinesCSV, write2File, \
    mapping_fashionSuitableFor, cleansed_categories_data_feed_path, \
    maxNumberFashionSizeColumns, getMappingColumnIndex, \
    synonym_female, synonym_euro, synonym_male


class Cleanser:
    def __init__(self):
        self.input_data_feed: str = file_paths["labeled_data_feed_path"]
        self.feature_mapping = createMappingBetween2Columns(files_mapping_categories_path, 1, 2, ";")
        self.fashionSuitableFor_mapping = createMappingBetween2Columns(mapping_fashionSuitableFor, 2, 6, ";")
        self.categoryName_index = getHeadersIndex("category_name")
        self.fashionSuitableFor_index = getHeadersIndex("Fashion:suitable_for")
        self.rrp_price_index = getHeadersIndex("rrp_price", file=self.input_data_feed)
        self.delivery_cost_index = getHeadersIndex("delivery_cost", file=self.input_data_feed)
        self.search_price_index = getHeadersIndex("search_price", file=self.input_data_feed)
        self.merchantName_index = getHeadersIndex("merchant_name", file=self.input_data_feed)
        self.title_index = getHeadersIndex("Title",file=self.input_data_feed)

    def article_cleansing(self, article):
        """
        First cleansing of the category_name
        After we cleanse the merchant_name
        :param article: Article will be cleansed
        :return:
        """

        # category_name cleansing
        content_category_name = article[self.categoryName_index]
        for string2find, new_category in self.feature_mapping.items():
            if string2find in content_category_name:
                article[self.categoryName_index] = new_category
        article[self.categoryName_index] = clean_category_sex(article)
        # Change the content within Topman category to man
        if "Topman" in article[self.merchantName_index]:
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
        article[self.merchantName_index] = article[self.merchantName_index].replace(" DE","")

        return article

    def cleansing_articles(self, list_vegan_articles):
        with Pool() as p:
            result_renamed = list(tqdm.tqdm(p.imap(self.article_cleansing, list_vegan_articles),
                                            total=len(list_vegan_articles)))
        return result_renamed

    def renamingFashionSuitableFor(self, article):
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

    def cleanPrices(self, list_articles):
        p = Pool()
        cleanedPrices_articles = p.map(self.cleanPrice, list_articles)
        return cleanedPrices_articles

    def mergedProductBySize(self, input_list_articles):
        """
        :param input_list_articles: List of all articles with "duplicates" by size
        :return: list_articles_merged
        """
        headers = input_list_articles[0]
        list_art = input_list_articles[1:]
        list_articles_merged = []
        mapping_awImageUrl_sizes = defaultdict(list)
        mapping_awImageUrl_article = {}
        mapping_columnHeader = getMappingColumnIndex(self.input_data_feed, "\t")

        for article in list_art:
            size_content = article[mapping_columnHeader["Fashion:size"]]
            size_content = cleanSize(size_content)
            mapping_awImageUrl_sizes[article[mapping_columnHeader["aw_image_url"]]].append(
                size_content)  # Mapping URL sizes
            mapping_awImageUrl_article[article[mapping_columnHeader["aw_image_url"]]] = article  # Mapping URL article
        # Add the sizes columns to the headers
        headers = [header.replace("Fashion:size", "Fashion:size0") for header in headers]
        for i in range(1, maxNumberFashionSizeColumns):  # Start at one because we already use Fashion:size0
            headers.append("Fashion:size" + str(i))

        mapping_header_columnId = {header: columnId for columnId, header in enumerate(headers)}
        # Put the size into the size column
        for url, sizes in mapping_awImageUrl_sizes.items():
            list_size = []
            for lt in sizes:
                for size in lt:
                    list_size.append(size)
            article = mapping_awImageUrl_article[url]
            # Append empty rows for the new sizes column
            for i in range(maxNumberFashionSizeColumns):
                article.append("")
            list_size = list_size[:maxNumberFashionSizeColumns]
            for i, size in enumerate(list_size):
                article[mapping_header_columnId["Fashion:size" + str(i)]] = size
            list_articles_merged.append(article)

        return [headers] + list_articles_merged


def cleansing():
    with Pool() as p:
        clnsr = Cleanser()
        print("Begin cleansing")
        list_articles = getLinesCSV(clnsr.input_data_feed, "\t")
        print("Cleansing - Merging by size: Begin")
        list_articles = clnsr.mergedProductBySize(list_articles)
        print("Cleansing - Merging by size: Done")
        headers = list_articles[0]
        list_articles = list_articles[1:]
        print("Cleansing - Renaming Categories: Begin")
        renamed_category_articles = list(tqdm.tqdm(p.imap(clnsr.article_cleansing, list_articles),
                                            total=len(list_articles)))#clnsr.cleansing_articles(list_articles)
        renamed_category_articles = [headers] + renamed_category_articles
        write2File(renamed_category_articles, cleansed_categories_data_feed_path)
        print("Cleansing - Renaming Categories: Done")
        headers = renamed_category_articles[0]
        renamed_category_articles = renamed_category_articles[1:]
        print("Cleansing - Sexes and Prices: Begin")
        cleansed_fashion_suitable_for = list(tqdm.tqdm(p.imap(clnsr.renamingFashionSuitableFor, renamed_category_articles)
                                                               , total=(len(renamed_category_articles))))#clnsr.renamingFashionSuitableForColumns(renamed_category_articles)
        cleansed_prices = p.map(clnsr.cleanPrice, cleansed_fashion_suitable_for)#clnsr.cleanPrices(cleansed_fashion_suitable_for)
        print("Cleansing - Sexes and Prices: Done")
        cleansed_articles = [headers] + cleansed_prices
        write2File(cleansed_articles, file_paths["cleansed_sex_data_feed_path"])

# print(cleanPrice(getLinesCSV(filtered_data_feed_path, "\t")[1]))
# print(renameCategory(getLinesCSV(filtered_data_feed_path, "\t")[1]))
