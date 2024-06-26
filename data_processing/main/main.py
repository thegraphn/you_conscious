"""
This scripts executes the data processing pipe line.
At the end of this script the used data feed for the web site will have been
generated.
"""
import glob
import os
import sys
from multiprocessing import freeze_support

from data_processing.data_processing.merging.merging_datafeeds import merging
from data_processing.data_processing.utils.utils import download_data_feeds_directory_path

folder = os.path.dirname(os.path.realpath(__file__))
folder = folder.replace("/data_processing/main", "")
folder = folder.replace(r"\data_processing\main", "")
sys.path.append(folder)

from data_processing.data_processing.add_features.add_features import add_features
from data_processing.data_processing.cleansing_datafeed.cleansing_datafeed import cleansing
from data_processing.data_processing.download_data_feeds.download_datafeeds import downloading
from data_processing.data_processing.filter_datafeed.filter_data_feed import filter_data_feed, \
    get_articles_with_label, delete_non_matching_categories
import datetime


def main_app():
    begin = datetime.datetime.now()
    print("Begin data processing", begin)
    processes: dict = {"downloading": True,
                       "merging": True,
                       "filtering": True,
                       "adding_features": True,
                       "filtering_without_label": True,
                       "cleansing": True,
                       "filtering_only_matching_category": True,
                       "shut_down": False}

    for process, todo in processes.items():
        print(process, todo)
        if process == "downloading":
            if todo:
                list_downloaded_files = glob.glob(os.path.join(download_data_feeds_directory_path, "*.csv"))
                for file in list_downloaded_files:
                    os.remove(file)
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
                get_articles_with_label()
        if process == "cleansing":
            if todo:
                cleansing()
        if process == "filtering_only_matching_category":
            if todo:
                delete_non_matching_categories()
        if process == "shut_down":
            # os.system("shutdown")
            pass
    end = datetime.datetime.now()
    print("End data processing", end)
    print("It took ", end - begin)


if __name__ == "__main__":
    freeze_support()
    main_app()
