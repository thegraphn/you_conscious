from collections import defaultdict
from multiprocessing import Pool

import tqdm
from nltk import word_tokenize

from data_processing.cleansing_datafeed.utils import cleanSize
from data_processing.utils.getHeaders import mapping_columnHeader, getHeadersIndex
from data_processing.utils.utils import createMappingBetween2Columns, files_mapping_categories_path, \
    getLinesCSV, filtered_data_feed_path, write2File, \
    mapping_fashionSuitableFor, cleansed_categories_data_feed_path, cleansed_sex_data_feed_path, \
    fashionSuitableFor_index, \
    maxNumberFashionSizeColumns, getMappingColumnIndex, mapping_cleaning_fashionSuitableFor, title_index, merchantName, \
    synonym_female, synonym_euro, labeled_data_feed_path

global feature_mapping
feature_mapping = createMappingBetween2Columns(files_mapping_categories_path, 1, 2, ";")
feature_mapping = feature_mapping
global fashionSuitableFor_mapping
fashionSuitableFor_mapping = createMappingBetween2Columns(mapping_fashionSuitableFor, 2, 6, ";")
fashionSuitableFor_mapping = fashionSuitableFor_mapping


def renameCategory(article):
    categoryName_index = getHeadersIndex("category_name")
    content_category_name = article[categoryName_index]
    for string2find, new_category in feature_mapping.items():
        if string2find in content_category_name:
            article[categoryName_index] = new_category
    #sexe = article[fashionSuitableFor_index]
    words_title = word_tokenize(article[title_index])
    cat = article[categoryName_index]
    for word in words_title:
        for k, v in mapping_cleaning_fashionSuitableFor.items():
            if word == k:
                article[categoryName_index] = v
                cat = article[categoryName_index].split(" > ")
                if len(cat) > 1 and len(article) > 20:
                    cat[1] = article[fashionSuitableFor_index]
                    if cat[1] == "" or cat[1] == " ":
                        cat[1] = "Damen"
                    cat = " > ".join(cat)
                    cat = cat.replace("female", "Damen")
                    cat = cat.replace("Female", "Damen")
                    cat = cat.replace("male", "Herren")
                    cat = cat.replace("Male", "Herren")
                    break
            else:
                cat = article[categoryName_index]
    article[categoryName_index] = cat
    # Change the content within Topman category to man
    if "Topman" in article[merchantName]:
        article[categoryName_index]: str = article[categoryName_index].replace("Damen", "Herren")
    for female_token in synonym_female:
        # todo fsf
        if female_token in article[fashionSuitableFor_index]:
            if "Herren" in article[categoryName_index]:
                article[categoryName_index]: str = article[categoryName_index].replace("Herren", "Damen")
    return article


def renamingCategories(list_vegan_articles):
    with Pool() as p:
        result_renamed = list(tqdm.tqdm(p.imap(renameCategory, list_vegan_articles), total=len(list_vegan_articles)))
    return result_renamed


def renamingFashionSuitableFor(article):
    categoryName_index = getHeadersIndex("category_name")
    content_categoryName = article[categoryName_index]
    content_fashionSuitableFor = article[fashionSuitableFor_index]
    sex = content_categoryName.split(" > ")
    if len(sex) == 0:
        sex = content_categoryName.split(">")
        sex = sex[1]
        if content_fashionSuitableFor == "" or " ":
            article[fashionSuitableFor_index] = sex
    return article


def renamingFashionSuitableForColumns(list_articles):
    with Pool() as p:
        result_fashionSuitableFor_renamed = list(tqdm.tqdm(p.imap(renamingFashionSuitableFor, list_articles)
                                                           , total=(len(list_articles))))
    return result_fashionSuitableFor_renamed


def cleanPrice(article):
    # todo
    rrp_price_index =getHeadersIndex("rrp_price", file=cleansed_categories_data_feed_path)
    delivery_cost_index = getHeadersIndex("delivery_cost", file=cleansed_categories_data_feed_path)
    search_price_index = getHeadersIndex("search_price", file=cleansed_categories_data_feed_path)
    if article[rrp_price_index] == "0" or article[rrp_price_index] == "0,00" or article[rrp_price_index] == "0.00":
        article[rrp_price_index] = article[search_price_index]
    if article[rrp_price_index] == "" or len(article[rrp_price_index]) == 0:
        article[rrp_price_index] = article[search_price_index]
    if article[delivery_cost_index] == '"0,00 EUR"' or article[delivery_cost_index] == ''"0.00 EUR"'':
        article[delivery_cost_index] = "0"
    for euro_token in synonym_euro:
        if euro_token in article[search_price_index]:
            article[search_price_index]: str = article[search_price_index].replace(euro_token, "")
        if euro_token in article[rrp_price_index]:
            article[rrp_price_index]: str = article[rrp_price_index].replace(euro_token, "")
        if euro_token in article[delivery_cost_index]:
            article[delivery_cost_index]: str = article[delivery_cost_index].replace(euro_token, "")
    article[search_price_index]: str = article[search_price_index].replace(".", ",")
    article[rrp_price_index]: str = article[rrp_price_index].replace(".", ",")
    article[delivery_cost_index]: str = article[delivery_cost_index].replace(".", ",")
    return article


def cleanPrices(list_articles):
    p = Pool()
    cleanedPrices_articles = p.map(cleanPrice, list_articles)
    return cleanedPrices_articles


def mergedProductBySize(input_list_articles):
    """
    :param input_list_articles: List of all articles with "duplicates" by size
    :return: list_articles_merged
    """
    headers = input_list_articles[0]
    list_art = input_list_articles[1:]
    list_articles_merged = []
    mapping_awImageUrl_sizes = defaultdict(list)
    mapping_awImageUrl_article = {}
    mapping_columnHeader = getMappingColumnIndex(filtered_data_feed_path, "\t")

    for article in list_art:
        size_content = article[mapping_columnHeader["Fashion:size"]]
        size_content = cleanSize(size_content)
        mapping_awImageUrl_sizes[article[mapping_columnHeader["aw_image_url"]]].append(
            size_content)  # Mapping URL sizes
        mapping_awImageUrl_article[article[mapping_columnHeader["aw_image_url"]]] = article  # Mapping URL article
    mapping_article_sizes = {}
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
    print("Begin cleansing")
    list_articles = getLinesCSV(filtered_data_feed_path, "\t")
    print("Cleansing - Merging by size: Begin")
    list_articles = mergedProductBySize(list_articles)
    print("Cleansing - Merging by size: Done")
    headers = list_articles[0]
    list_articles = list_articles[1:]
    print("Cleansing - Renaming Categories: Begin")
    renamed_category_articles = renamingCategories(list_articles)
    renamed_category_articles = [headers] + renamed_category_articles
    write2File(renamed_category_articles, cleansed_categories_data_feed_path)
    print("Cleansing - Renaming Categories: Done")
    headers = renamed_category_articles[0]
    renamed_category_articles = renamed_category_articles[1:]
    print("Cleansing - Sexes and Prices: Begin")
    cleansed_fashion_suitable_for = renamingFashionSuitableForColumns(renamed_category_articles)
    cleansed_prices = cleanPrices(cleansed_fashion_suitable_for)
    print("Cleansing - Sexes and Prices: Done")
    cleansed_articles = [headers] + cleansed_prices
    write2File(cleansed_articles, cleansed_sex_data_feed_path)


#print(cleanPrice(getLinesCSV(filtered_data_feed_path, "\t")[1]))
#print(renameCategory(getLinesCSV(filtered_data_feed_path, "\t")[1]))