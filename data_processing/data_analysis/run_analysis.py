import markdown2pdf
import tqdm
from matplotlib import pyplot

from data_processing.data_analysis.data_analysis import DataAnalyser
from data_processing.data_processing.utils.file_paths import file_paths
from data_processing.data_processing.utils.utils import get_mapping_column_index

data_analyser: DataAnalyser = DataAnalyser(file_paths["filtered_only_matching_categories_datafeed"])
headers = get_mapping_column_index(file_paths["filtered_only_matching_categories_datafeed"], "\t")
headers = list(headers.keys())
headers = headers[0:20]
list_stats: list = []

for header in tqdm.tqdm(headers):
    try:
        stats = data_analyser.get_stats(header)
        print(stats)
        list_stats.append(header)
    except:
        stats = None
        print("Header: " + header + " not implemented")

    if stats is not None:
        data_analyser.create_pie_plot(labels=list(stats.keys()), numbers=list(stats.values()), title=header)
        data_analyser.create_simple_chart(labels=list(stats.keys()), numbers=list(stats.values()), title=header)

# create readme
with open("report.md", "w", encoding="utf-8") as o:
    for stat in list_stats:
        o.write("# " + stat)
        o.write("\n")
        o.write("\n")
        path = "/home/graphn/repositories/you_conscious/data_processing/data_analysis/images/" + stat +"_pie.png"
        o.write("!["+stat+"](" + path + ")")
        o.write("\n")
        path = "/home/graphn/repositories/you_conscious/data_processing/data_analysis/images/" + stat + "_bar.png"
        o.write("![" + stat + "](" + path + ")")
        o.write("\n")
markdown2pdf.convert_md_2_pdf(filename="report.md",output="report.pdf")
