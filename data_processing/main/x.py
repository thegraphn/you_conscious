from data_processing.utils.utils import changeDelimiterCsv, cleansed_sex_data_feed_path

changeDelimiterCsv(csv_input=cleansed_sex_data_feed_path,
                   csv_output=r"\\NAS232723\home\YouConscious\YouConscious\it\data_checking\data_feed.csv", delimiter_input="\t", delimiter_output=";")