from data_processing.data_processing.cleansing_datafeed.size_sorter import SizeSorter

l2 = [["XL", "M", "S", "XS"], ["34", "32", "50", "10"], ["XS", "S", "M", "L", "XL", "XXL", "XXXL", "4XL", "XXS"],
      ["S", "M", "L", "XL", "XXL", "XXXL", "4XL", "5XL", "6XL", "7XL"], ["XL-XXL", "S-M", "M-L", "XS-S"],["one_size"],
      ["UK 28S","UK 30S","UK 32S","UK 34S","UK 28R","UK 30R","UK 32R","UK 34R","UK 36R","UK 38R","UK 30L","UK 32L","UK 34L"
          ,"UK 36L","UK 38L"],
      ["36.0"   , "36.0 "  , "36.0 "  ,"37.0" ,"38.0"  ,"39.0"  ,"40.0" ,"50.0"]
      ]

for size in l2:
    size_sorter = SizeSorter(size)
    sl = size_sorter.sort_list()
    print(size,sl, size_sorter.sorting_type)
