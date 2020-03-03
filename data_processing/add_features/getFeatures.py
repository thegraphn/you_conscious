from data_processing.utils.utils import getLinesCSV, features_mapping_path
try:
    features_list = getLinesCSV(features_mapping_path, ";")
    features_list = features_list[1:]
except:
    pass