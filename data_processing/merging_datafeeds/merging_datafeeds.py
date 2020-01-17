import glob
import os,sys

folder = os.path.dirname(os.path.realpath(__file__))


print(folder.replace(r"/data_processing/merging_datafeeds", ""))
sys.path.append(folder.replace(r"/data_processing/merging_datafeeds", ""))

list_datafeed_paths = glob.glob(r"data_processing\data_working_directory\downloads\downloaded_datafeeds\.*")

print(list_datafeed_paths)