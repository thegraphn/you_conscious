import csv
from random import shuffle

from data_processing.data_processing.utils.utils import getMappingColumnIndex

interesting_columns = [
                       "merchant_name",
                       "Fashion:suitable_for",
                       "Title",
                       "description",
                       "brand"
                       ]
h = getMappingColumnIndex("/home/graphn/repositories/you_conscious/dl_xp/data_processing/datafeed.csv",";")
print(h)
label_pos = h["category_name"]

label_pos = label_pos
interesting_data = []
label_set = set()
with open("datafeed.csv", encoding="utf-8") as f:
    csv_reader = csv.reader(f, delimiter=";")
    list_index_interesting_data = []
    for row in csv_reader:
        for i, column_header in enumerate(row):
            if column_header in interesting_columns:
                list_index_interesting_data.append(i)
        break
    for row in csv_reader:
        article_data = []
        for position in list_index_interesting_data:
            article_data.append(row[position])
        article_data = " <SEP> ".join(article_data)
        article_data = [article_data] + [row[label_pos]]
        label_set.add(row[label_pos])
        interesting_data.append(article_data)


def write_data(data, data_output):
    with open(data_output, "w", encoding="utf-8") as o:
        csv_writer = csv.writer(o, delimiter="\t")
        for element in data:
            csv_writer.writerow(element)


shuffle(interesting_data)
begin_train = 0
end_train = round(len(interesting_data) * 0.9)
#begin_val = end_train + 1
#end_val = round(len(interesting_data) * 0.8)
begin_test = end_train + 1
end_test = len(interesting_data)

headers = ["text", "label"]

train = interesting_data[begin_train:end_train]
train = [headers] + train
#val = interesting_data[begin_val:end_val]
#val = [headers] + val
test = interesting_data[begin_test:end_test]
test = [headers] + test
write_data(train, "/home/graphn/repositories/you_conscious/dl_xp/data/category/train_category.tsv")
# write_data(val,"/home/graphn/repositories/you_conscious/dl_xp/data/category/val_category.tsv")
write_data(test, "/home/graphn/repositories/you_conscious/dl_xp/data/category/test_category.tsv")

for label in label_set:
    print(label)
