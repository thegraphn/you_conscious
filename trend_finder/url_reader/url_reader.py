import urllib

import requests
from bs4 import BeautifulSoup
from lxml import html

class UrlReader:
    def __init__(self, url: str):
        self.url = url
        self.url_content = self.read_url()

    def read_url(self):
        s:str= "Mit einem Frühlingsoutfit mit Midirock beginnt für mich der perfekte Start in die neue Frühling/Sommer Modesaison. Luftig, leicht und einfach elegant flattert mir der beige Rock um die Knie! Währenddessen greife ich in meinem Kleiderschrank und suche nach dem perfekten Gegenstück zu diesem anmutigen Rock. Gefunden habe ich es, wie so oft ganz zufällig! Ich liebe diese spontanen Griffe in den Schrank und die daraus entstehenden Looks."