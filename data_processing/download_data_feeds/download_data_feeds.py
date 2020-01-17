"""
This scripts download the data feed from their url. 
If necessary it unpacks them also.

1. Read the datafeed-locations.csv file
2. Extract the URLS
3. Download the files from theirs URL

"""

def getListURLFromCSV(data_feedfile):
    #todo read file and return list of url
    pass

def downloadDatafeedFromUrl(url):
    #todo download file form url
    pass



list_urls = []
with open(r"C:\aurelien\you_conscious\utils\data_dependencies\datafeed-locations.csv", "r") as f:
    for i,line in enumerate(f):
        splits = line.split(";")
        url_datafeed = splits[1]
        print(url_datafeed)
        list_urls.append(url_datafeed)

for url in list_urls:
    print(url)


for x in range(10):
    for x2 in range(20):
        if x == x2:
            print("x")