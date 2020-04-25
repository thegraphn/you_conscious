from data_processing.data_processing.cleansing_datafeed.tmp.size_sorter import SizeSorter

l2=[["XL","M","S","XS"],["34","32","50","10"],["XS","S","M","L","XL","XXL","XXXL","4XL","XXS"],["S",	"M",	"L","XL",	"XXL",	"XXXL",	"4XL",	"5XL",	"6XL",	"7XL"]
]

for size in l2:
    size_sorter = SizeSorter(size)
    print(size_sorter.sort_list())

