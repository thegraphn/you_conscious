# You Conscious

This repository contains all the scripts in order to process the data showed on youconscious.com

## Tempory solution to get the data feed nice and ready for the web app

### Connect to the yc server

#### Prepare the server to download and merge the data feed files 
`ssh root@54.37.73.34`

  Go to `cd /home/backend/backend/datafeeds_preprocessing/downloaded_datafeeds/`
  Delete all the files in `/home/backend/backend/datafeeds_preprocessing/downloaded_datafeeds` : `rm  *`
  Go to `cd /home/backend/backend/datafeeds_preprocessing/merged_datafeeds/`
  Delete all the file in `/home/backend/backend/datafeeds_preprocessing/merged_datafeeds/` : `rm *`


#### Download and merge the data feed files

Download the files : 

`python3 download_datafeeds.py /home/backend/backend/`

Merge the files : 

`python3 merged_datafeeds.py /home/backend/backend/`

#### Download merged_datafeeds.zip

Now the merged_datafeeds.csv file is ready on the server. You can download it and put into your local directory `you_conscious/data_processing/data_working_directory/merged`

e.g.

`scp root@54.37.73.34:/home/backend/backend/datafeeds_preprocessing/merged_datafeeds/merged_datafeeds.zip  /home/conny/repositories/you_conscious/data_processing/data_working_directory/merged`

Please be aware the path might not be 100% the same :) 

#### Run the app on your pc

Now you have the file on your computer you can run  `main.py` 
