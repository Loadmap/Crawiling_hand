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

        if not os.path.exists(os.path.join(save_path, 'browser.json')) :

            with open('browser.json', 'w', encoding = 'utf-8') as f :
                json.dump(data, f, indent = 4)
                print(f'데이터가 {save_path} 경로에 json 형식으로 올바르게 저장되되었습니다.')

        else:
            print('현재 경로에 파일 존재')

    @staticmethod
    def read_json_browser():

        with open('browser.json', 'r', encoding='utf-8') as f:
            browser_data = json.load(f)

        return browser_data

    @staticmethod
    def check_json_browser(browser) :

        try:
            browser_data = CollectLinks.read_json_browser()

            if browser not in browser_data :
                raise KeyError(f'{browser} 브라우저 데이터가 존재하지 않음')

            check_browser = browser_data[browser]

            for data in ['search_url', 'click_xpath', 'img_xpath'] :

                if data not in check_browser :
                    raise KeyError(f'{browser} 브라우저에 대한 {data} 데이터가 존재하지 않음')

        except FileNotFoundError :
            print(f'올바른 경로에 browser.json 파일이 존재하지 않습니다. 파일 경로를 확인하세요.')

            return

        except json.JSONDecodeError :
            print('파일 내용이 올바른 JSON 형식이 아닙니다. 파일을 확인하세요.')

            return

        except KeyError as e :
            print(f'브라우저 에러 : {e}')

            return

        except Exception as e :
            print(f'예상 외의 에러 {e} 발생')

            return

        return browser_data[browser]

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
    def img_links(self, browser, topic, option='', limit=20) :
        browser_data = self.check_json_browser(browser)

        try:
            search_data = browser_data

        except (KeyError, TypeError):

            return

        except Exception as e:
            print(f'예상 외의 에러 {e} 발생')

            return

        self.driver.get(search_data['search_url'].format(topic = topic, option = option))
        time.sleep(2)
        self.click_img_area(search_data['click_xpath'])
        img_xpath = search_data['img_xpath']

        next_button = self.driver.find_element(By.TAG_NAME, 'body')

        links = []
        cnt = 0
        limit = 100 if limit == 0 else limit

        while len(links) < limit :
            t1 = time.time()

            while True:
                imgs = self.driver.find_elements(By.XPATH, img_xpath)
                t2 = time.time()

                if len(imgs) > 0 or (t1 - t2 > 5) :
                    break

            if not imgs :
                print(f'이미지 찾기 실패 {imgs}')
                continue

            retry_cnt = 3

            while retry_cnt > 0 :

                try:
                    src = imgs[0].get_attribute('src')

                    if src is not None and src not in links :
                        links.append(src)
                        cnt += 1

                        print(f'{cnt}, {src}')

                    break

                except StaleElementReferenceException :
                    print('-' * 100)
                    print(f'{cnt}번째 {src}에서 {StaleElementReferenceException} 발생')
                    print('-' * 100)

                    imgs = self.driver.find_elements(By.XPATH, img_xpath)
                    retry_cnt -= 1

                except Exception as e :
                    print(f'네이버 크롤링 에러 발생 {e}')

                    break

            if retry_cnt == 0 :
                print(f'{cnt}번째 이미지 로드 실패 다음 이미지로 넘어감')

            next_button.send_keys(Keys.RIGHT)

        print('=' * 100)
        print(f'{browser.capitalize()} 크롤링 완료')
        print(f'Browser : {browser.capitalize()}, Topic : {topic}, 이미지 수 : {cnt}개')
        print('=' * 100)

        self.driver.close()

        return links

if __name__ == '__main__' :
    topic = 'hand'

    collect = CollectLinks()
    # print(collect.read_json_browser())
    print(collect.check_json_browser('naver'))
    collect.img_links(browser = 'naver', topic = topic, limit = 10)

    collect.driver.quit()