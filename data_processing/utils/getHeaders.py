from data_processing.utils.utils import getMappingColumnIndex, cleansed_sex_data_feed_path, filtered_data_feed_path

mapping_columnHeader = getMappingColumnIndex(filtered_data_feed_path, ",")
mapping_columnHeader["DUMMY_VALUE"] = 9999
