from data_processing.data_processing.filter_datafeed.filter_data_feed import Filter
from data_processing.data_processing.utils.utils import get_lines_csv, merged_data_feed_path

fltr = Filter(relevancy_filter=False)

list_articles = get_lines_csv(merged_data_feed_path, ",")
headers = list_articles[0]
list_articles = list_articles[1:]
x = []
print("List of articles has been created")
print("Filtering - filtering: Begin")
for article in list_articles:
    x.append(fltr.is_article_vegan(article))
print(len(list_articles), len(x))
