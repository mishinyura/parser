import time

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

user_agent = "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"


def get_data(url):
    print('Запускаем функцию')
    options = webdriver.FirefoxOptions()
    options.set_preference('dom.webdriver.enabled', False)
    options.set_preference('general.useragent.override', user_agent)
    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("user-agent=AutomationControlled")

    sv = Service(executable_path='C:/Users/Босс/Desktop/prog/PycharmProjects/parse_selenium/geckodriver.exe')
    driver = webdriver.Firefox(
        service=sv,
        options=options
    )
    # driver.get(url=url)

    try:
        print(f'Запрашиваем {url} у браузера')
        driver.get(url=url)
        print(driver.find_elements(By.CLASS_NAME, 'youMayNeedCategoryItem'))
        time.sleep(2)
        with open('index.html', 'w') as file:
            file.write(driver.page_source)
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()
    print('Завершаем функцию')

#https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
# https://www.auchan.ru/catalog/
# https://n5m.ru/usagent.html
get_data('https://www.auchan.ru/catalog/')