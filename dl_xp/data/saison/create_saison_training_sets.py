import csv
from random import shuffle

from data_processing.data_processing.utils.utils import get_mapping_column_index

interesting_columns = ["brand",
                       "merchant_name",
                       "Fashion:suitable_for",
                       "Title",
                       "description"]
h = get_mapping_column_index("training_saison.csv", "\t")
print(h)

interesting_data = []

with open("training_saison.csv", encoding="utf-8") as f:
    csv_reader = csv.reader(f, delimiter="\t")
    list_index_interesting_data = []
    for row in csv_reader:
        interesting_data.append(row)


def write_data(data, data_output):
    with open(data_output, "w", encoding="utf-8") as o:
        csv_writer = csv.writer(o, delimiter="\t")
        for element in data:
            csv_writer.writerow(element)


headers = interesting_data[0]
interesting_data = interesting_data[1:]
shuffle(interesting_data)
begin_train = 0
end_train = round(len(interesting_data) * 0.9)
# begin_val = end_train + 1
# end_val = round(len(interesting_data) * 0.8)
begin_test = end_train + 1
end_test = len(interesting_data)

train = interesting_data[begin_train:end_train]
train = [headers] + train
# val = interesting_data[begin_val:end_val]
# val = [headers] + val
test = interesting_data[begin_test:end_test]
test = [headers] + test
write_data(train, "train_saison.tsv")
# write_data(val,"/home/graphn/repositories/you_conscious/dl_xp/data/category/val_category.tsv")
write_data(test, "test_saison.tsv")


