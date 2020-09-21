import tokenizer

from data_processing.data_processing.filter_datafeed.filter_data_feed import Filter
from data_processing.data_processing.utils.utils import get_lines_csv

fltr = Filter()
list_articles = get_lines_csv(
    "/home/graphn/repositories/you_conscious/data_processing/data_working_directory/download/Avocadostore-20-06-09.csv",
    ",")
list_articles_bag_affair:list=[]

for article in list_articles:
    if "Bag Affair" in article:
        list_articles_bag_affair.append(article)

for article in list_articles_bag_affair:
    tmp_article = article
    article = " ".join(article)
    article_words: list = []

    for info in tokenizer.tokenize(article):
        _, token, _ = info
        if token is not None:
            article_words.append(token)

    #article_words = sorted(set(word_tokenize(article.replace(",", " "))))
    article_words = sorted(set(article_words))
    article_words = list(article_words)
    vegan = True
    for filter_veg in fltr.vegan_black_filters:
        filter_veg = filter_veg.split(" ")
        if len(set(filter_veg).intersection(article_words)) == len(filter_veg):
            vegan = False
            break
    if vegan:
        pass
