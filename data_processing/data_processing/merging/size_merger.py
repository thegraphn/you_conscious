from collections import defaultdict
from data_processing.data_processing.cleansing_datafeed.size_sorter import SizeSorter
from data_processing.data_processing.cleansing_datafeed.utils import clean_size
from data_processing.data_processing.utils.utils import get_mapping_column_index, MAX_NUM_FASHION_SIZE_COLUMNS
from data_processing.data_processing.cleansing_datafeed.config import merchant_to_identifier


class SizeMerger:
    def __init__(self, data_frame_path: str):
        self.data_frame_path = data_frame_path
        self.column_index = get_mapping_column_index(self.data_frame_path, "\t")

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
        mapping_column_header = {h: i for i, h in enumerate(headers)}
        print(mapping_column_header["merchant_name"])
        for article in list_art:
            merchant_name = article[self.column_index["merchant_name"]]
            identifier_column = merchant_to_identifier[merchant_name]
            size_content = article[self.column_index["Fashion:size"]]
            size_content = clean_size(size_content)
            stock_content = article[self.column_index["stock_status"]]

            if "Avocadostore" in article[self.column_index["merchant_name"]]:
                merchant_product_id = article[self.column_index["merchant_product_id"]]
                split_merchant_product_id_index = merchant_product_id.split("-")
                colour: str = article[self.column_index["colour"]]
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
