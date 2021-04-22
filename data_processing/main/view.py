import PySimpleGUI as sg

from data_processing.add_features.add_features import add_features
from data_processing.cleansing_datafeed.cleansing_datafeed import cleansing
from data_processing.download_data_feeds.download_datafeeds import downloading
from data_processing.filter_datafeed.filter_data_feed import filter_data_feed, getArticlesWithLabel
from data_processing.main.main import main_app
from data_processing.data_processing.merging_datafeeds import merging

sg.theme('DarkAmber')  # Keep things interesting for your users


layout = [ [sg.Text('Enter the function you want to run or  all if you wanna run the all badass pipepline.'),
            sg.Button("all"),
            sg.Button("Download"),
            sg.Button("Merged"),
            sg.Button("Filter"),
            sg.Button("Clean"),
            sg.Button("Feature"),
            sg.Button("Filter Feature"),],
           [sg.OK()] ]

window = sg.Window('Data processing badass App', layout)
event, values = window.read()
if event == "all":
    main_app()

if event == "Download":
    downloading()
if event == "Merged":
    merging()
if event == "Filter":
    filter_data_feed()
if event == "Clean":
    cleansing()
if event == "Feature":
    add_features()
if event == "Filter Feature":
    getArticlesWithLabel()

