import os
import json
import time
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException

# 드라이버
class CollectLinks :

    # 생성자
    def __init__(self, no_gui = False) :

        # Chrome 웹드라이버 설정
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')  # To maintain user cookies
        chrome_options.add_argument('--disable-dev-shm-usage')

        if no_gui :
            chrome_options.add_argument('--headless')  # Headless 모드 (GUI 없이 실행)

        chromedriver_path = Service(chromedriver_autoinstaller.install())
        self.driver = webdriver.Chrome(service = chromedriver_path, options = chrome_options)

        # Chrome 브라우저의 버전 정보 가져오기
        browser_version = self.driver.capabilities['browserVersion']
        chromedriver_version = self.driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]

        print('=' * 100)
        print('정상 작동')
        print(f'현재 Chrome 브라우저 버전: {browser_version}')
        print(f'현재 ChromeDriver 버전: {chromedriver_version}')

        # 버전 출력
        if browser_version.split('.')[0] != chromedriver_version.split('.')[0] :
            print('버전이 다릅니다.')
        
        # json 파일 자동 생성
        self.browser_data = self.make_json_browser()

        print('=' * 100)

    # jason 파일 생성
    @staticmethod
    def make_json_browser():
        save_path = os.getcwd()

        data = {
            "google": {
                "search_url": "https://www.google.com/search?q={topic}&tbm=isch{option}",
                "click_xpath": "//div[@jsname='dTDiAc']",
                "img_xpath": "//div[@jsname='figiqf']//img"
            },
            "naver": {
                "search_url": "https://search.naver.com/search.naver?&where=image&query={topic}&{option}",
                "click_xpath": "//div[@class='tile_item _fe_image_tab_content_tile']//img[@class='_fe_image_tab_content_thumbnail_image']",
                "img_xpath": "//div[@class='image']//img"
            }
        }

        if not os.path.exists(os.path.join(save_path, 'browser.json')):

            with open('browser.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                print(f'데이터가 {save_path} 경로에 json 형식으로 올바르게 저장되되었습니다.')

        else:
            print('현재 경로에 파일 존재')

        try:
            with open('browser.json', 'r', encoding='utf-8') as f:
                browser_data = json.load(f)

        except Exception as e:
            print(f'{save_path} 경로에 파일이 올바르지 않습니다.')
            print(f'{e}')

        return browser_data

    # img click area

    def click_img_area(self, xpath) :

        try :
            click_img = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            click_img.click()

        except Exception as e :
            print(f'click_img_area 에러발생 {e}')
            print(f'새로 고침 실행')
            self.driver.refresh()
            time.sleep(2)

            return self.click_img_area(xpath)

        return click_img

    # topic_select
    def get_scroll(self) :
        pos = self.driver.execute_script("return window.pageYOffset;")

        return pos

    def scroll_down(self) :
        last_pos = 0
        pause_cnt = 0
        max_pause_cnt = 20

        while True :
            self.driver.execute_script("window.scrollBy({top : window.innerHeight * 2, behavior : 'smooth'})")
            time.sleep(0.5)

            new_pos = self.get_scroll()

            if last_pos == new_pos :
                pause_cnt += 1

            else :
                pause_cnt = 0
                last_pos = new_pos

            if pause_cnt >= max_pause_cnt :
                break

    # img src 링크
    def img_links(self, browser, topic, option='', limit=20):

        if 'google' in self.browser_data and browser == 'google':
            google_data = self.browser_data['google']
            self.driver.get(google_data['search_url'].format(topic = topic, option = option))

            self.click_img_area(google_data['click_xpath'])
            img_xpath = google_data['img_xpath']

        if 'naver' in self.browser_data and browser == 'naver':
            naver_data = self.browser_data['naver']
            self.driver.get(naver_data['search_url'].format(topic = topic, option = option))

            time.sleep(2)
            self.click_img_area(naver_data['click_xpath'])
            img_xpath = naver_data['img_xpath']

        next_button = self.driver.find_element(By.TAG_NAME, 'body')

        links = []
        cnt = 0
        limit = 100 if limit == 0 else limit

        while len(links) < limit:
            t1 = time.time()

            while True:
                imgs = self.driver.find_elements(By.XPATH, img_xpath)
                t2 = time.time()

                if len(imgs) > 0:
                    break

                if t1 - t2 > 5:
                    print(f'이미지 찾기 실패 {imgs}')
                    break

            try:
                src = imgs[0].get_attribute('src')

                if src is not None and src not in links:
                    links.append(src)
                    print(f'{cnt + 1}, {src}')

                    cnt += 1

            except StaleElementReferenceException:
                print(f'{StaleElementReferenceException} 발생')
                pass

            except Exception as e:
                print(f'네이버 크롤링 에러 발생 {e}')

            next_button.send_keys(Keys.RIGHT)

        print('=' * 100)
        print(f'{browser.capitalize()} 크롤링 완료')
        print(f'Browser : {browser.capitalize()}, Topic : {topic}, 이미지 수 : {cnt}개')
        print('=' * 100)

        self.driver.close()

        return links

if __name__ == '__main__':
    topic = 'hand'

    collect = CollectLinks()
    collect.img_links(browser = 'naver', topic = topic, limit = 0)

    collect.driver.quit()