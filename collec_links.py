import os
import chromedriver_autoinstaller
import selenium
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# 드라이버
class collect_links() :

    # 생성자
    def __init__(self, no_gui = False) :

        # Chrome 웹드라이버 설정
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')  # To maintain user cookies
        chrome_options.add_argument('--disable-dev-shm-usage')

        if no_gui :
            chrome_options.add_argument('--headless')  # Headless 모드 (GUI 없이 실행)

        chromedriver_path = Service(chromedriver_autoinstaller.install())
        self.driver = webdriver.Chrome(service = chromedriver_path, options = chrome_options)

        # Chrome 브라우저의 버전 정보 가져오기
        browser_version = self.driver.capabilities['browserVersion']
        chromedriver_version = self.driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0]

        print('=' * 50)
        print('정상 작동')
        print(f'현재 Chrome 브라우저 버전: {browser_version}')
        print(f'현재 ChromeDriver 버전: {chromedriver_version}')

        # 버전 출력
        if browser_version.split('.')[0] != chromedriver_version.split('.')[0] :
            print('버전이 다릅니다.')

        print('=' * 50)

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
    def google_img_links(self, topic, option = '', limit = 30) :
        self.driver.get(f'https://www.google.com/search?q={topic}&tbm=isch{option}')

        self.click_img_area('//div[@jsname="dTDiAc"]')
        next_button = self.driver.find_element(By.TAG_NAME, 'body')

        links = []
        cnt = 1

        while len(links) < limit:
            img_xpath = '//div[@jsname="figiqf"]//img'
            t1 = time.time()

            while True:
                imgs = self.driver.find_elements(By.XPATH, img_xpath)
                t2 = time.time()

                if len(imgs) > 0:
                    break

                if t2 - t1 > 5:
                    print(f'이미지 찾기 실패 {imgs}')
                    break

            try:
                src = imgs[0].get_attribute('src')

                if src is not None and src not in links:
                    print(f'{cnt}. {src.strip()}')
                    links.append(src)
                    cnt += 1

            except Exception as e:
                print(f'구글 크롤링 에러발생 {e}')

            next_button.send_keys(Keys.RIGHT)
        print('=' * 25 + '구글 크롤링 완료' + '=' * 25)
        print(f'topic : {topic} 이미지 수 : {limit}개 구글 크롤링 완료')
        print('=' * 23 + '=' * len('구글 크롤링 완료') * 2 + '=' * 23)

        return links


topic = 'hand'

collect = collect_links()
collect.google_img_links(topic)

collect.driver.quit()