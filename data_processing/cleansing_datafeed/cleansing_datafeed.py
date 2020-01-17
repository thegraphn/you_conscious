from multiprocessing import Pool

import tqdm

from data_processing.cleansing_datafeed.utils import cleanSize
from data_processing.utils.getHeaders import mapping_columnHeader
from data_processing.utils.utils import createMappingBetween2Columns, files_mapping_categories_path, \
    getLinesCSV, filtered_data_feed_path, write2File, \
    mapping_fashionSuitableFor, cleansed_categories_data_feed_path, cleansed_sex_data_feed_path, categoryName_index, \
    fashionSuitableFor_index, rrp_price_index, search_price_index, delivery_cost_index, categoryName_index

global feature_mapping
feature_mapping = createMappingBetween2Columns(files_mapping_categories_path, 1, 2, ";")
feature_mapping = feature_mapping
global fashionSuitableFor_mapping
fashionSuitableFor_mapping = createMappingBetween2Columns(mapping_fashionSuitableFor, 2, 6, ";")
fashionSuitableFor_mapping = fashionSuitableFor_mapping


def renameCategory(article):

    content_category_name = article[categoryName_index]
    for string2find, new_category in feature_mapping.items():
        if string2find in content_category_name:
            article[categoryName_index] = new_category
    return article


def renamingCategories(list_vegan_articles):
    with Pool() as p:
        result_renamed = list(tqdm.tqdm(p.imap(renameCategory, list_vegan_articles), total=len(list_vegan_articles)))
    return result_renamed


def renamingFashionSuitableFor(article):
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
    if article[rrp_price_index] == "0" or article[rrp_price_index] == "0,00" or article[rrp_price_index] == "0.00":
        article[rrp_price_index] = article[search_price_index]
    if article[rrp_price_index] == "":
        article[rrp_price_index] = article[search_price_index]
    if article[delivery_cost_index] == '"0,00 EUR"' or article[delivery_cost_index] == ''"0.00 EUR"'':
        article[delivery_cost_index] == "0"
    return article
    '''
    for columnName in columnNameList:
        index_price = getColumnIndex(csv_file, columnName)
        row[index_price] = row[index_price].replace(".", ",")
        if len(row[index_price]) == 2:
            row[index_price] = row[index_price] + ",00"
        if "," in row[index_price] and len(row[index_price][row[index_price].index(","):]) == 2:
            row[index_price] = row[index_price] + "0"
    if row[index_rppPrice] == "0" or row[index_rppPrice] == "0,00" or row[index_rppPrice] == "0.00":
        row[index_rppPrice] = row[index_searchPrice]
    if row[index_rppPrice] == "":
        row[index_rppPrice] = row[index_searchPrice]
    if row[index_deliveryCost] == '"0,00 EUR"' or row[index_deliveryCost] == ''"0.00 EUR"'':
        row[index_deliveryCost] == "0"
    csv_writer.writerow(row)
    '''


def cleanPrices(list_articles):
    p = Pool()
    cleanedPrices_articles = p.map(cleanPrice, list_articles)
    return cleanedPrices_articles


def mergedProductBySize(list_articles):
    mapping_awImageUrl_sizes = {}
    mapping_article_awImageUrl = {}
    for article in list_articles:
        size_content = article[mapping_columnHeader["Fashion:size"]]
        size_content = cleanSize(size_content)
        mapping_awImageUrl_sizes[article[mapping_columnHeader["aw_image_url"]]] = size_content
        mapping_article_awImageUrl[article] = article[mapping_columnHeader["aw_image_url"]]
    maxNumberFashionSizeColumns = max(len(x) for x in list(mapping_awImageUrl_sizes.values()))
    headers = list_articles[0]
    mapping_article_sizes = {}
    for i in range(maxNumberFashionSizeColumns):
        headers.append("Fashion:size_" + str(i + 1))
    for article1, aw_image_url1 in mapping_article_awImageUrl.items():
        for article2, aw_image_url2 in mapping_article_awImageUrl.items():
            if aw_image_url1 == aw_image_url2:
                mapping_article_sizes[article1] = mapping_awImageUrl_sizes[aw_image_url1]


def cleansing():
    print("Begin cleansing")
    list_articles = getLinesCSV(filtered_data_feed_path, ",")
    print("Cleansing - Merging by size: Begin")
    # todo merged_articles_by_size = mergedProductBySize(list_articles)
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


'''


mergingProductBySizes(path + "datafeeds_preprocessing/filtered_datafeeds/only_featured_articles_pricesCleaned.csv",
                      path + "datafeeds_preprocessing/filtered_datafeeds/only_featured_articles_mergedSizes.csv")
print("Merging Sizes: done")

print("Clean Categories: Start")
cleanCategories(path + "utils/category/categoriesCleaning_mapping.csv",
                path + "datafeeds_preprocessing/filtered_datafeeds/only_featured_articles_mergedSizes.csv",
                path + "datafeeds_preprocessing/filtered_datafeeds/datafeed.csv")
print("Script Adding features: Done", datetime.datetime.now())


    '''
