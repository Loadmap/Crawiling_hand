import os
import json
import datetime
import requests
from collect_links import CollectLinks

class Crawling :

    def __init__(self, n_threads = 4, google = True, naver = True, no_gui = False, save_path = 'download', limit = 10) :
        self.n_treads = n_threads
        self.google = google
        self.naver = naver
        self.no_gui = no_gui
        self.limit = limit = 1000 if limit == 0 else limit
        self.collect_links = CollectLinks
        self.browser_data, self.browser_keys = CollectLinks.read_json_browser()

        os.makedirs(f'./{save_path}', exist_ok = True)

    @staticmethod
    def make_dir(name) :
        path = os.path.join(os.getcwd(), name)

        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def make_and_read_topic() :
        txt_path = os.path.join(os.getcwd(), 'topic.txt')

        if not os.path.exists(txt_path) :
            with open(txt_path, 'w', encoding='utf-8') as f :
                f.write('hand, face')

        with open(txt_path, 'r', encoding='utf-8') as f :
            topics = []

            for topic in f.read().split(',') :
                topics.append(topic.strip())

        return topics

    @staticmethod
    def get_extension(link) :
        sep = str(link).split('.')
        ext = sep[-1].lower()

        if ext == 'jpg' or ext == 'jpeg' :

            return 'jpg'

        elif ext == 'png' :

            return 'png'

        elif ext == 'gif' :

            return 'gif'

        else:

            return 'jpg'

    def make_log(self, browser, limit) :
        log_data = {}
        topics = self.make_and_read_topic()

        self.make_dir('log')

        for topic in topics:
            link = self.collect_links().img_links(browser = browser, topic = topic, limit = limit)
            log_data.setdefault(browser, []).append([topic, link])

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            log_path = f'./log/{timestamp}.txt'
            cnt = 0

            while os.path.exists(log_path) :
                cnt += 1
                log_path = f'./log/{timestamp} ({cnt}).txt'

            with open(log_path, 'w', encoding='utf-8') as f :
                json.dump(log_data, f, ensure_ascii = False, indent = 4)

        except Exception as e :

            return

        return log_data


if __name__ == '__main__' :
    crawling = Crawling(n_threads = 4, google = True, naver = True, no_gui = False, limit = 5)
