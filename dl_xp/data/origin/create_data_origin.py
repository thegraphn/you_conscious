"""

{"version": "v2.0", "data":

"""
import json
from random import shuffle

import pandas as pd
import csv
import re

column_ord: list = [
    'id',
    'item_id',
    'plus_sizes',
    'label_all_together',
    'featured',
    'Labels',
    'label_1',
    'label_2',
    'label_3',
    'label_4',
    'label_5',
    'label_6',
    'label_7',
    'label_8',
    'label_9',
    'label_10',
    'label_11',
    'label_12',
    'label_13',
    'label_14',
    'label_15',
    'label_16',
    'label_17',
    'label_18',
    'label_19',
    'verified',
    'Material',
    'Hergestellt in',
    'search_price',
    'rrp_price',
    'delivery_cost',
    'merchant_name',
    'category_name',
    'category_predicted',
    'saison',
    'saison_conf_score_index',
    'Fashion:suitable_for',
    'Title',
    'description',
    'brand',
    'origin_predicted',
    'payment_methods',
    'custom_8',
    'custom_6',
    'base_price_text',
    'saving',
    'currency',
    'ean',
    'valid_to',
    'custom_3',
    'language',
    'base_price_amount',
    'model_number',
    'image_large_url',
    'merchant_product_id',
    'custom_2',
    'ship_to',
    'Fashion:size',
    'rating',
    'product_type',
    'material',
    'warranty',
    'Fashion:pattern',
    'large_image',
    'stock_status',
    'store_price',
    'valid_from',
    'product_id',
    'isbn',
    'brand_name',
    'savings_percent',
    'stock_quantity',
    'mpn',
    'Fashion:material',
    'terms_of_contract',
    'specifications',
    'merchant_product_second_category',
    'web_offer',
    'data_feed_id',
    'colour',
    'color_normalized_0',
    'color_normalized_1',
    'color_normalized_2',
    'in_stock',
    'parent_product_id',
    'alternate_image_four',
    'promotional_text',
    'brand_id',
    'alternate_image_three',
    'custom_7',
    'european_article_number',
    'dimensions',
    'Fashion:swatch',
    'pre_order',
    'merchant_thumb_url',
    'keywords',
    'delivery_time',
    'last_updated',
    'merchant_category_id',
    'basket_link',
    'category_id',
    'condition',
    'aw_image_url',
    'aw_deep_link',
    'custom_5',
    'merchant_deep_link',
    '\ufeffid',
    'custom_1',
    'short_description',
    'merchant_image_url',
    'alternate_image',
    'aw_thumb_url',
    'merchant_product_third_category',
    'merchant_id',
    'seals',
    'alternate_image_two',
    'delivery_restrictions',
    'base_price',
    'gender',
    'custom_4',
    'commission_group',
    'description2',
    'aw_product_id',
    'custom_9',
    'size_stock_amount',
    'average_rating',
    'Fashion:category',
    'product_model',
    'number_available',
    'reviews',
    'delivery_weight',
    'is_for_sale', 'upc',
    'size_stock_status',
    'product_GTIN',
    'ext_size',
    'Versandkosten Sofortüberweisung',
    'Währung',
    'Versandkosten Lastschrift',
    'Hersteller Artikelnummer HAN',
    'ext_pzn',
    'Anbieter Artikelnummer AAN',
    'Preis (Netto)',
    'Versandkosten PayPal',
    'ext_europäische Artikelnummer EAN',
    'ext_Hersteller Artikelnummer HAN',
    'ext_Versandkosten Sofortüberweisung',
    'ext_Produktkategorie ID', 'ext_Währung'
                               'europäische Artikelnummer EAN',
    'Versandkosten Vorkasse',
    'Vorschaubild-URL',
    'Produktbeschreibung lang',
    'Versandkosten Rechnung',
    'Versandkosten Kreditkarte',
    'Versandkosten Nachnahme',
    'ext_ppu',
    'ext_mpnr',
    'Hersteller',
    'Vorschaubild-URL',
    'merchant_image_url',
    '',
    'europäische Artikelnummer EAN'
    'ext_Grundpreiseinheit',
    'ext_Grundpreis',
    'europäische Artikelnummer EAN',
    'ext_Grundpreiseinheit',
    'ext_Währung',
    'additional_image_link.1',
    'additional_image_link.2'

]

column_index_mapping = {column_name: index for index, column_name in enumerate(column_ord)}


def write_data(data, data_output):
    with open(data_output, "w", encoding="utf-8") as o:
        csv_writer = csv.writer(o, delimiter="\t")
        for element in data:
            csv_writer.writerow(element)
label_set = set()
data_path = "/home/graphn/repositories/you_conscious/data_processing/data_working_directory/filtered/2020-12-09_filtered_only_matching_categories_datafeed.csv"
interesting_data = []
with open(data_path, "r", encoding="utf-8") as f:
    csv_reader = csv.reader(f, delimiter="\t")
    for i, row in enumerate(csv_reader):
        paragraphs = []
        title = row[column_index_mapping["Title"]]
        description = row[column_index_mapping["description"]]
        origin = row[column_index_mapping["Hergestellt in"]]
        context = title + " [SEP] " + description
        regex = origin
        if origin in context and origin!="":
            regex = regex

            test_str = context

            matches = re.finditer(regex, test_str, re.MULTILINE)

            for matchNum, match in enumerate(matches, start=1):


                interesting_data.append([context,origin])
                label_set.add(origin)

shuffle(interesting_data)
begin_train = 0
end_train = round(len(interesting_data) * 0.9)
# begin_val = end_train + 1
# end_val = round(len(interesting_data) * 0.8)
begin_test = end_train + 1
end_test = len(interesting_data)

headers = ["text", "label"]

train = interesting_data[begin_train:end_train]
train = [headers] + train
# val = interesting_data[begin_val:end_val]
# val = [headers] + val
test = interesting_data[begin_test:end_test]
test = [headers] + test
write_data(train, "/home/graphn/repositories/you_conscious/dl_xp/data/origin/train_origin.tsv")
# write_data(val,"/home/graphn/repositories/you_conscious/dl_xp/data/category/val_category.tsv")
write_data(test, "/home/graphn/repositories/you_conscious/dl_xp/data/origin/test_origin.tsv")
label_set = sorted(list(label_set))
for label in label_set:
    print(label)
