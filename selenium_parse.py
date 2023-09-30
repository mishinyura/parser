import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

user_agent = "Your User-Agent"#user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0
browser_driver_path = 'Path webdriver'#C:/Users/Босс/Desktop/prog/PycharmProjects/parser/firefoxdriver/geckodriver.exe


def settings_options(path: str):
    sv = Service(executable_path=path)
    if path.endswith('chromedriver.exe'):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--user-agent={user_agent}")
        driver = webdriver.Chrome(
            service=sv,
            options=options
        )
        return driver
    elif path.endswith('geckodriver.exe'):
        options = webdriver.FirefoxOptions()
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('general.useragent.override', user_agent)
        driver = webdriver.Firefox(
            service=sv,
            options=options
        )
        return driver


def get_data(url):
    driver = settings_options(browser_driver_path)
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

#https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html
# https://www.auchan.ru/catalog/
# https://n5m.ru/usagent.html
get_data('https://n5m.ru/usagent.html')