from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.utils import changeDelimiterCsv

csv_input: str = file_paths["filtered_only_matching_categories_datafeed"]
csv_output: str = r"\\NAS232723\home\YouConscious\YouConscious\it\data_checking\data_feed_lol.csv"

changeDelimiterCsv(csv_input=csv_input,
                   csv_output=csv_output,
                   delimiter_input="\t",
                   delimiter_output=";")
