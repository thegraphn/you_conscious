from data_processing.data_processing.cleansing_datafeed.cleansing_datafeed import Cleanser
from data_processing.data_processing.filter_datafeed.filter_data_feed import Filter
from data_processing.utils.file_paths import file_paths
from data_processing.utils.getHeaders import getHeadersIndex
from data_processing.utils.utils import get_lines_csv
from trend_finder.url_reader.url_reader import UrlReader

url_reader = UrlReader(
    url="https://www.kleidermaedchen.de/2020/04/matt-and-nat-quena-rucksack-fruehlingsoutfit-midirock/")
fltr = Filter()
list_articles = get_lines_csv(file_paths["filtered_data_feed_path"], "\t")
list_articles = list_articles[100:300]
list_description: list = []
description_index: int = getHeadersIndex(header="description", file=file_paths["filtered_data_feed_path"])
for article in list_articles:
    list_description.append(article[description_index])
    print(article[description_index])
