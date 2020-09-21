from data_processing.add_features.add_features import featuresAdder
from data_processing.cleansing_datafeed.cleansing_datafeed import Cleanser
from data_processing.filter_datafeed.filter_data_feed import Filter


class Article(list):
    def __init__(self, headers: dict):
        super().__init__()
        self.headers = headers
        self.filter = Filter()
        self.cleanser = Cleanser()
        self.featurer = featuresAdder()