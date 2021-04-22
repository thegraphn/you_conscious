from data_processing.data_processing.utils.utils import get_lines_csv

list_with = get_lines_csv("/home/graphn/repositories/you_conscious/data_processing/data_working_directory/filtered/with_dl.csv","\t")
list_without = get_lines_csv("/home/graphn/repositories/you_conscious/data_processing/data_working_directory/filtered/without_dl.csv","\t")
print(len(list_with),len(list_without))
for wit,witout in zip(list_with,list_without):
    pass