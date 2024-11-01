import os
import requests
from collect_links import CollectLinks

class Crawling:

    def __init__(self, n_threads = 4, google = True, naver = True, no_gui = False, limit = 10) :
        self.n_treads = n_threads
        self.google = google
        self.naver = naver
        self.no_gui = no_gui
        self.limit = limit