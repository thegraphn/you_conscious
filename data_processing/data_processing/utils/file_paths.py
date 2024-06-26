import os
from datetime import datetime

from data_processing.data_processing.utils.utils import merged_data_feed_path

root_folder = os.path.dirname(os.path.realpath(__file__))

root_folder = root_folder.replace(r"\data_processing\data_processing\utils", "")
root_folder = root_folder.replace(r"data_processing/data_processing/utils", "")

labeled_data_feed_path = os.path.join(root_folder, "data_processing")
labeled_data_feed_path = os.path.join(labeled_data_feed_path, "data_working_directory")
labeled_data_feed_path = os.path.join(labeled_data_feed_path, "filtered")
labeled_data_feed_path = os.path.join(labeled_data_feed_path, "labeled_data_feed.csv")

filtered_data_feed_path = os.path.join(root_folder, "data_processing")
filtered_data_feed_path = os.path.join(filtered_data_feed_path, "data_working_directory")
filtered_data_feed_path = os.path.join(filtered_data_feed_path, "filtered")
filtered_data_feed_path = os.path.join(filtered_data_feed_path, "filtered_datafeed.csv")

done_datafeed = os.path.join(root_folder, "data_processing")
done_datafeed = os.path.join(done_datafeed,
                                                          "data_working_directory")
done_datafeed = os.path.join(done_datafeed, "done_datafeeds")
done_datafeed = os.path.join(done_datafeed,
                                                          datetime.now().strftime("%Y-%m-%d_") +
                                                          "done_datafeed" +

                                                          ".csv")

features_affiliateId_data_feed_path = os.path.join(root_folder, "data_processing")
features_affiliateId_data_feed_path = os.path.join(features_affiliateId_data_feed_path, "data_working_directory")
features_affiliateId_data_feed_path = os.path.join(features_affiliateId_data_feed_path, "featured")
features_affiliateId_data_feed_path = os.path.join(features_affiliateId_data_feed_path,
                                                   "featured_affiliateIds_datafeed.csv")

cleansed_sex_data_feed_path = os.path.join(root_folder, "data_processing")
cleansed_sex_data_feed_path = os.path.join(cleansed_sex_data_feed_path, "data_working_directory")
cleansed_sex_data_feed_path = os.path.join(cleansed_sex_data_feed_path, "cleansed")
cleansed_sex_data_feed_path = os.path.join(cleansed_sex_data_feed_path, "cleansed_sexes_datafeed.csv")

file_datafeed_location = os.path.join(root_folder, "data_processing")
file_datafeed_location = os.path.join(file_datafeed_location, "utils")
file_datafeed_location = os.path.join(file_datafeed_location, "data_dependencies")
file_datafeed_location = os.path.join(file_datafeed_location, "datafeed-locations.csv")

category_name_cleansing = os.path.join(root_folder, "data_processing")
category_name_cleansing = os.path.join(category_name_cleansing, "utils")
category_name_cleansing = os.path.join(category_name_cleansing, "data_dependencies")
category_name_cleansing = os.path.join(category_name_cleansing, "category_name_cleaning.csv")

file_paths = {"labeled_data_feed_path": labeled_data_feed_path,
              "filtered_data_feed_path": filtered_data_feed_path,
              "featured_affiliateIds_datafeed_path": features_affiliateId_data_feed_path,
              "cleansed_sex_data_feed_path": cleansed_sex_data_feed_path,
              "file_datafeed_location": file_datafeed_location,
              "category_name_cleansing": category_name_cleansing,
              "merged_datafeed": "/home/graphn/repositories/you_conscious/data_processing/data_working_directory/merged/merged_datafeeds.csv"

              }
