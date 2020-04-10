import os

root_folder = os.path.dirname(os.path.realpath(__file__))

root_folder = root_folder.replace(r"\data_processing\utils", "")
root_folder = root_folder.replace(r"data_processing/utils", "")

labeled_data_feed_path = os.path.join(root_folder, "data_processing")
labeled_data_feed_path = os.path.join(labeled_data_feed_path, "data_working_directory")
labeled_data_feed_path = os.path.join(labeled_data_feed_path, "filtered")
labeled_data_feed_path = os.path.join(labeled_data_feed_path, "labeled_data_feed.csv")

filtered_data_feed_path = os.path.join(root_folder, "data_processing")
filtered_data_feed_path = os.path.join(filtered_data_feed_path, "data_working_directory")
filtered_data_feed_path = os.path.join(filtered_data_feed_path, "filtered")
filtered_data_feed_path = os.path.join(filtered_data_feed_path, "filtered_datafeed.csv")

features_affiliateId_data_feed_path = os.path.join(root_folder, "data_processing")
features_affiliateId_data_feed_path = os.path.join(features_affiliateId_data_feed_path, "data_working_directory")
features_affiliateId_data_feed_path = os.path.join(features_affiliateId_data_feed_path, "featured")
features_affiliateId_data_feed_path = os.path.join(features_affiliateId_data_feed_path,
                                                   "featured_affiliateIds_datafeed.csv")

file_paths = {"labeled_data_feed_path": labeled_data_feed_path,
              "filtered_data_feed_path": filtered_data_feed_path,
              "featured_affiliateIds_datafeed_path": features_affiliateId_data_feed_path

              }
