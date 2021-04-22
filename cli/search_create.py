from data_processing.data_processing.utils.utils import get_lines_csv, merged_data_feed_path, write_2_file
from tqdm import tqdm

search_term = "Bag Affair"
list_articles = get_lines_csv(merged_data_feed_path, ",")
found_articles = []
for article in tqdm(list_articles, total=len(list_articles)):
    txt = " ".join(article)
    if search_term in txt:
        found_articles.append(article)

write_2_file(found_articles, "bag_affair.csv")
