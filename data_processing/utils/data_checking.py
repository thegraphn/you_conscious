from collections import Counter


def counter_merchant(file_data:str):
    list_articles = []
    counter = Counter()
    with open(file_data,"r",encoding="utf-8") as f:
        for line in f:
            list_articles.append(line)

