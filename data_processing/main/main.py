"""
This scripts executes the data processing pipe line.
At the end of this script the used data feed for the web site will have been
generated.
"""
import os
import sys
folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/main", "")
folder = folder.replace(r"\data_processing\main", "")
sys.path.append(folder)

from data_processing.utils.utils import merged_data_feed_path, features_data_feed_path, \
    cleansed_categories_data_feed_path, write2File, getLinesCSV
import datetime
from data_processing.add_features.add_features import add_features, featuresAdder
from data_processing.cleansing_datafeed.cleansing_datafeed import cleansing, Cleanser
from data_processing.download_data_feeds.download_datafeeds import downloading
from data_processing.filter_datafeed.filter_data_feed import filter_data_feed, getArticlesWithLabel, \
    delete_non_matching_categories, Filter
from data_processing.merging_datafeeds.merging_datafeeds_old import merging
from data_processing.utils import file_paths


def main_app():
    begin = datetime.datetime.now()
    print("Begin data processing", begin)
    download = False

    if download:
        downloading()
    if not download:
        #merging()
        #filter_data_feed()
        #add_features()
        #getArticlesWithLabel()
        cleansing()
        delete_non_matching_categories()
    end = datetime.datetime.now()
    print("End data processing", end)
    print("It took ", end - begin)


main_app()
