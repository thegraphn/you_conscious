"""
This scripts executes the data processing pipe line.
At the end of this script the used data feed for the web site will have been
generated.
"""

import datetime
from data_processing.add_features.add_features import add_features
from data_processing.cleansing_datafeed.cleansing_datafeed import cleansing
from data_processing.filter_datafeed.filter_data_feed import filter_data_feed, getArticlesWithLabel

if __name__ == '__main__':
    begin = datetime.datetime.now()
    print("Begin data processing", begin)
    filter_data_feed()
    cleansing()
    add_features()
    getArticlesWithLabel()
    end = datetime.datetime.now()
    print("End data processing", end)
    print("It took ", end - begin)
