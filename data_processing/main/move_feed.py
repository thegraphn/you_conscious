import base64
from email.mime.text import MIMEText

from data_processing.utils.utils import changeDelimiterCsv, cleansed_sex_data_feed_path

csv_input: str = cleansed_sex_data_feed_path
csv_output: str = r"\\NAS232723\home\YouConscious\YouConscious\it\data_checking\data_feed.csv"

changeDelimiterCsv(csv_input=csv_input,
                   csv_output=csv_output,
                   delimiter_input="\t",
                   delimiter_output=";")
