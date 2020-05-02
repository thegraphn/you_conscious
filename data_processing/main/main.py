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

from data_processing.data_processing.add_features.add_features import add_features
from data_processing.data_processing.cleansing_datafeed.cleansing_datafeed import cleansing
from data_processing.data_processing.download_data_feeds.download_datafeeds import downloading
from data_processing.data_processing.filter_datafeed.filter_data_feed import filter_data_feed, getArticlesWithLabel, \
    delete_non_matching_categories
from data_processing.data_processing.merging_datafeeds.merging_datafeeds_old import merging

import datetime


def main_app():
    begin = datetime.datetime.now()
    print("Begin data processing", begin)
    processes: dict = {"downloading": False,
                       "merging": False,
                       "filtering": False,
                       "adding_features": True,
                       "filtering_without_label": True,
                       "cleansing": True,
                       "filtering_only_matching_category": True}

    for process, todo in processes.items():
        print(process, todo)
        if process == "downloading":
            if todo:
                downloading()

        if process == "merging":
            if todo:
                merging()
        if process == "filtering":
            if todo:
                filter_data_feed()
        if process == "adding_features":
            if todo:
                add_features()
        if process == "filtering_without_label":
            if todo:
                getArticlesWithLabel()
        if process == "cleansing":
            if todo:
                cleansing()
        if process == "filtering_only_matching_category":
            if todo:
                delete_non_matching_categories()

    end = datetime.datetime.now()
    print("End data processing", end)
    print("It took ", end - begin)


main_app()
