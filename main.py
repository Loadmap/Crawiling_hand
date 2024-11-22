import os
import shutil
import json
import requests
from collect_links import CollectLinks
from datetime import datetime

class Crawling :

    def __init__(self, n_threads = 4, crawl_google = True, crawl_naver = True, no_gui = False, save_path = './download', limit = 10) :
        self.n_treads = n_threads
        self.crawl_google = crawl_google
        self.crawl_naver = crawl_naver
        self.no_gui = no_gui
        self.save_path = save_path
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

    @staticmethod
    def save_files(response, file_path) :

        try:

            with open(f'{file_path}', 'wb') as f :
                shutil.copyfileobj(response.raw, f)

        except Exception as e :
            print(f'저장 실패  : {e}')

    def make_data(self, browser, topic) :
        data = {}
        topics = self.make_and_read_topic()

        self.make_dir('data')


        link = self.collect_links().img_links(browser = browser, topic = topic, limit = self.limit)
        data.setdefault(browser, []).append([topic, link])

        # try:
        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        #     data_path = f'./data/{timestamp}.txt'
        #     cnt = 0
        #
        #     while os.path.exists(data_path) :
        #         cnt += 1
        #         data_path = f'./data/{timestamp} ({cnt}).txt'
        #
        #     with open(data_path, 'w', encoding='utf-8') as f :
        #         json.dump(data, f, ensure_ascii = False, indent = 4)
        #
        # except Exception as e :
        #     print(f'예상치 못한 오류 발생 : {e}')
        #
        #     return

        return data

    def download_imgs(self, browser, links, topic, max_cnt = 0) :
        self.make_dir(f'{self.save_path}/{topic}')

        img_topic = links[browser][0][0]
        img_links = links[browser][0][1]

        total = len(img_links)
        success_cnt = 0

        if max_cnt == 0 :
            max_cnt = total

        print(f'{browser} 로부터 다운로드 중')

        for idx, link in enumerate(img_links) :

            if success_cnt >= max_cnt :

                break

            try:

                print(f'{success_cnt + 1} / {total} : {link}')

                response = requests.get(link, stream=True, timeout=10)
                ext = self.get_extension(link)

                link_path = f'{self.save_path}/{topic}/{browser}_{str(idx).zfill(4)}'
                link_ext_path = f'{link_path}.{ext}'

                self.save_files(response, link_ext_path)

                success_cnt += 1

                del response

                print('다운로드 완료')

            except Exception as e :
                print(f'예상치 못한 오류로 이미지 다운로드 실패 : {e}')

        print('-' * 100)

    def download_from_browser(self, topic) :

        try :

            if self.crawl_google == True :
                browser = 'google'
                links = self.make_data(browser, topic)

            elif self.crawl_naver == True :
                browser = 'naver'
                links = self.make_data(browser, topic)

            else :
                print('해당 브라우저 데이터를 찾을 수 없음')
                links = []

        except Exception as e :
            print(f'예상치 못한 오류 발생 : {e}')

            return

        self.download_imgs(browser, links, topic)

if __name__ == '__main__' :
    crawling = Crawling(n_threads = 4, crawl_google = True, crawl_naver = True, no_gui = False, save_path = './download', limit = 5)
    crawling.download_from_browser(topic = 'hand')
