import itertools

import pandas as pd
from itertools import compress, product, permutations
from tqdm import tqdm

file = "/home/graphn/repositories/you_conscious/data_processing/data_working_directory/filtered/2020-10-21_filtered_only_matching_categories_datafeed.csv"
df = pd.read_csv(file, sep="\t")
price_to_find = 185.15
percentage = 0
list_prices_title = []
for index, row in df.iterrows():
    merchant_name = row["delivery_cost"]
    search_price = row['search_price'].replace(",", ".")
    title = row['Fashion:suitable_for']
    if float(search_price) <= price_to_find:
        if merchant_name == "asos":
            list_prices_title.append([float(search_price), title])


def get_combinations(items):
    s = list(items)  # allows duplicate elements
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1))


list_prices = [element[0] for element in list_prices_title]
list_prices = list(set(list_prices))
print(list_prices)
print(len(list_prices))
list_prices = list_prices[100:150]
comb = []
for i, combo in enumerate(get_combinations(list_prices), 1):
    if len(combo)<4:
        print('combo #{}: {}'.format(i, combo))
        print(i,len(list_prices))
        comb.append(combo)
for i, comb in tqdm(enumerate(comb), total=len(comb)):
    if sum(comb) == price_to_find:
        print("FOUND ", list_prices_title[i])
