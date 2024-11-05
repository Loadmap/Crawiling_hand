import os
import requests
from collect_links import CollectLinks

class Crawling:

    def __init__(self, n_threads = 4, google = True, naver = True, no_gui = False, save_path = 'download', limit = 10) :
        self.n_treads = n_threads
        self.google = google
        self.naver = naver
        self.no_gui = no_gui
        self.limit = limit
        self.collect_links = CollectLinks
        self.browser_data, self.browser_keys = CollectLinks.read_json_browser()

        os.makedirs(f'./{save_path}', exist_ok = True)

    @staticmethod
    def make_dir(name):
        path = os.path.join(os.getcwd(), name)

        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def make_and_read_topic():
        txt_path = os.path.join(os.getcwd(), 'topic.txt')

        if not os.path.exists(txt_path):
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write('hand, face')

        with open(txt_path, 'r', encoding='utf-8') as f:
            topics = []

            for topic in f.read().split(','):
                topics.append(topic.strip())

        return topics

    def download_imgs(self, links):

        for topic in Crawling.make_and_read_topic():
            Crawling.make_dir(f'./download/{topic}')

    def execute_crawling(self) :
        img_data = []

        for num, browser in enumerate(self.browser_keys) :

            for topic in Crawling.make_and_read_topic() :
                links = self.collect_links().img_links(browser = browser, topic = topic, limit = self.limit)
                img_data.append([num, links])


if __name__ == '__main__' :
    crawling = Crawling(n_threads = 4, google = True, naver = True, no_gui = False, limit = 5)
    crawling.execute_crawling()