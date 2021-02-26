from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from random import randint
import time
import os
import csv
import sys
import traceback


# options
options = webdriver.ChromeOptions()

# user-agent
options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0")

# disable webdriver mode

# # for older ChromeDriver under version 79.0.3945.16
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option("useAutomationExtension", False)

# for ChromeDriver version 79.0.3945.16 or over
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    executable_path=os.path.abspath('chromedriver'),
    options=options
)
try:
    info = list()
    result = list()
    with open('data.txt', mode='r') as f:
        file = f.read().split('\n')
    for i in file:
        driver.get(f'https://play.google.com/store/search?q={i}&c=apps')
        driver.implicitly_wait(25)
        while True:
            scroll_height = 2000
            document_height_before = driver.execute_script("return document.documentElement.scrollHeight")
            driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
            time.sleep(1.5)
            document_height_after = driver.execute_script("return document.documentElement.scrollHeight")
            if document_height_after == document_height_before:
                break
        time.sleep(randint(1, 2))
        blocks = driver.find_elements_by_xpath('//div[@class="RZEgze"]')
        print(f'Найдено {len(blocks)} по запросу "{i}"')
        for block in blocks:
            a = block.find_element_by_xpath('.//a[@href]')
            info.append([a.get_attribute('href'), i])
    for j in range(len(info)):
        print(f'Обработка результатов {j + 1} из {len(info)}')
        url = info[j][0]
        driver.get(url)
        driver.implicitly_wait(50)
        name = driver.find_element_by_xpath('//h1[@class="AHFaub"]').text
        name = name.replace(",", "")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            mail = driver.find_element_by_xpath('//a[@class="hrTbp euBY6b"]').text
        except Exception:
            mail = 'Почта не найдена'
        result.append((mail, name, url))
    result = list(set(result))
    with open('result.csv', mode='w') as f:
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('Почта', 'Название', 'Ссылка'))
        for i in result:
            writer.writerow(i)
except Exception as e:
    print('Произошла ошибка!')
    print('Ошибка:\n', traceback.format_exc())
finally:
    driver.close()
    driver.quit()
