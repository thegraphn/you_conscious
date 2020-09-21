from collections import Counter

from data_processing.data_processing.utils.utils import get_lines_csv

list_articles = get_lines_csv(file="/home/graphn/repositories/you_conscious/data_processing/utils/ref.csv",
                              delimiter="\t")
list_occ_merchent = []
for article in list_articles:
    list_occ_merchent.append(article[8])

occ_merchent = {}
for merchent in list_occ_merchent:
    if merchent not in occ_merchent:
        occ_merchent[merchent] = 1
    else:
        occ_merchent[merchent] += 1

list_articles_new = get_lines_csv(
    file="/home/graphn/repositories/you_conscious/data_processing/data_working_directory/filtered/filtered_only_matching_categories_datafeed.csv",
    delimiter="\t")

list_occ_merchent_mew = []
for article in list_articles_new:
    list_occ_merchent_mew.append(article[8])

occ_merchent_new = {}
for merchent in list_occ_merchent_mew:
    if merchent not in occ_merchent_new:
        occ_merchent_new[merchent] = 1
    else:
        occ_merchent_new[merchent] += 1

for merchent, occ in occ_merchent.items():
    print(merchent, "before", occ, "new", occ_merchent_new[merchent], "ratio",
          ((occ_merchent_new[merchent] / occ) * 100))
print(occ_merchent)
print(occ_merchent_new)
