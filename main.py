from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from random import randint
import requests
import time
import os
import csv
import re
import sys
import traceback
from twocaptcha import TwoCaptcha


API_KEY = 'API_KEY'
# options
options = webdriver.ChromeOptions()

options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0")

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('headless')
options.add_argument('window-size=1920x935')

driver = webdriver.Chrome(
    executable_path=os.path.abspath('chromedriver'),
    options=options
)
driver.set_page_load_timeout(8)
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
urls = []
data_without_mail = []
data = []
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
try:
    all_pages = list()
    with open('data.txt', mode='r') as f:
        file = f.read().split('\n')
    for i in range(len(file)):
        print(f'Ввод поисковых запросов {i + 1} из {len(file)}')
        search = file[i]
        for p in range(25):
            url = f'https://yandex.ru/search/?lr=20103&text={search}&p={p}'
            try:
                driver.get(url)
            except TimeoutException:
                pass
            driver.implicitly_wait(15)
            driver.find_element_by_xpath('/html').send_keys(Keys.END)
            time.sleep(0.5)
            pages = driver.find_elements_by_xpath('//a[@class="Link Link_theme_normal OrganicTitle-Link OrganicTitle-Link_wrap Typo Typo_text_l Typo_line_m organic__url link"]')
            if pages == []:
                print('Капча! Решаем...')
                img = driver.find_element_by_xpath('/html/body/div/form/div[1]/div/div[1]/img')
                api_key = os.getenv('APIKEY_2CAPTCHA', API_KEY)
                solver = TwoCaptcha(api_key)
                p = requests.get(img.get_attribute('src'))
                with open("captchaimg.jpg", "wb") as f:
                    f.write(p.content)
                result = solver.normal('captchaimg.jpg')
                inp = driver.find_element_by_xpath('//input[@name="rep"]')
                inp.send_keys(result['code'] + Keys.ENTER)
                os.remove('captchaimg.jpg')
                print('Капча решена')
                driver.implicitly_wait(15)
            pages = driver.find_elements_by_xpath('//a[@class="Link Link_theme_normal OrganicTitle-Link OrganicTitle-Link_wrap Typo Typo_text_l Typo_line_m organic__url link"]')
            for i in pages:
                all_pages.append(i.get_attribute('href'))
    print(f'Найдено всего {len(all_pages)} сайтов')
    for q in range(len(all_pages)):
        email = 'Почта не найдена'
        try:
            print(f'Парсинг почт {q + 1} из {len(all_pages)}')
        except Exception:
            pass
        try:
            driver.get(all_pages[q])
        except Exception:
            pass
        driver.implicitly_wait(15)
        url = driver.current_url
        body = driver.find_element_by_xpath('/html').text.split()
        for i in range(len(body)):
            """try:
                print(body[i])
            except Exception:
                print('a')"""
            try:
                if '@' in body[i]:
                    if (re.search(regex, body[i])):
                        email = body[i]
                        break
                    else:
                        email = 'Почта не найдена'
            except Exception:
                email = 'Почта не найдена'
        # print(email)
        data.append((email, all_pages[q]))
        driver.implicitly_wait(15)
    with open('result.csv', mode='w', newline='') as f:
        print('Запись в excel...')
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('Почта', 'Ссылка'))
        for i in data:
            if i[0] != 'Почта не найдена':
                writer.writerow(i)
        print('Запись завершена')
    print('Парсинг завершён')
except Exception as e:
    print('Ошибка:\n', traceback.format_exc())
finally:
    driver.close()
    driver.quit()
    print(input('Press ENTER to close this program'))
