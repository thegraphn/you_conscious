# 9. Load it & harvest your fruits (Inference)
import csv

from farm.infer import Inferencer

texts = []
with open(
        "/home/graphn/repositories/you_conscious/data_processing/data_working_directory/filtered/filtered_only_matching_categories_datafeed.csv",
        "r", encoding="utf-8") as f:
    csv_reader = csv.reader(f, delimiter="\t")
    next(csv_reader)
    for row in csv_reader:
        info_article = " ".join(row[3:])
        texts.append({"text": info_article})

save_dir = "/home/graphn/repositories/you_conscious/dl_xp/trained_model/relevancy"

model = Inferencer.load(save_dir,
batch_size=2
                        gpu=True,
                        )
result = model.inference_from_dicts(dicts=texts)

y_counter = 0
n_counter = 0
for prediction in result:
    p = prediction["predictions"]
    for pp in p:
        p = pp["label"]
        if p == "RELEVANT":
            y_counter += 1
        if p == "NOT_RELEVANT":
            n_counter += 1
            print(prediction)

print(y_counter, n_counter)
