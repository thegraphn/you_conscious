from data_processing.data_processing.cleansing_datafeed.cleansing_datafeed import Cleanser

clnsr = Cleanser()
list_articles = [""]
print(clnsr.predict_categories(list_articles))