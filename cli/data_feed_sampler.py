from random import shuffle

from data_processing.data_processing.utils.utils import get_lines_csv, write2File

input_data_path: str = input("Input file: Data feed to sample")
input_data = get_lines_csv(file=input_data_path,delimiter="\t")
output_data_path: str = input("Output file: Data feed sampled")

headers = input_data[0]
list_articles = input_data[1:]

id_2_articles: dict = {}
for i, article in enumerate(list_articles):
    id_2_articles[len(id_2_articles)] = article

number_articles = 5000
shuffled_ids = list(id_2_articles.keys())
shuffle(shuffled_ids)
sampled_shuffled_ids = shuffled_ids[0:number_articles]

output_articles = []

for id,article in id_2_articles.items():
    if id in sampled_shuffled_ids:
        output_articles.append(article)


output_data = [headers] + output_articles
write2File(list_articles=output_data, output_file=output_data_path, delimiter="\t")
