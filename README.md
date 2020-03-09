# You Conscious

This repository contains all the scripts in order to process the data showed on youconscious.com

## Tempory solution to get the data feed nice and ready for the web app

### Connect to the yc server

#### Prepare the server to download and merge the data feed files 
`ssh root@54.37.73.34`

got to `cd /home/backend/backend/datafeeds_preprocessing/downloaded_datafeeds/`

delete all the files in `/home/backend/backend/datafeeds_preprocessing/downloaded_datafeeds` : `rm  *`

go to `cd /home/backend/backend/datafeeds_preprocessing/merged_datafeeds/`

elete all the file in `/home/backend/backend/datafeeds_preprocessing/merged_datafeeds/` : `rm *`


#### Download and merge the data feed files

download the files : 

`python3 download_datafeeds.py /home/backend/backend/`

merge the files : 

`python3 merged_datafeeds.py /home/backend/backend/`


Now you have the merged file. You can download it and put into `you_conscious/data_processing/data_working_directory/merged`

e.g.

`scp root@54.37.73.34:/home/backend/backend/datafeeds_preprocessing/merged_datafeeds/merged_datafeeds.zip  /home/conny/repositories/you_conscious/data_processing/data_working_directory/merged`

Please be aware the path might not be 100% the same :) 

#### Run the app on your pc

Now you have the file on your computer you can run  `main.py` 
