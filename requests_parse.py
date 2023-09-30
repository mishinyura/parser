import time
import requests
import lxml
from bs4 import BeautifulSoup
import json
from datetime import datetime
from collections.abc import Callable

base_url = 'https://www.perekrestok.ru'
links_categories = ['/cat/mc/113/moloko-syr-ajca', '/cat/mc/148/ovosi-frukty-griby', '/cat/mc/100/makarony-krupy-maslo-specii', '/cat/mc/708/cipsy-sneki-popkorn', '/cat/mc/187/sokolad-konfety-sladosti', '/cat/mc/205/soki-vody-napitki', '/cat/mc/242/hleb-i-vypecka', '/cat/mc/132/maso-i-ptica', '/cat/mc/782/kolbasnye-izdelia', '/cat/mc/174/ryba', '/cat/mc/793/moreprodukty', '/cat/mc/54/zamorozennye-produkty', '/cat/mc/217/sousy-ketcupy-majonezy', '/cat/mc/79/kofe-caj-kakao-sahar', '/cat/mc/224/suhie-zavtraki-musli', '/cat/mc/74/konservacia', '/cat/mc/64/zdorove', '/cat/mc/157/orehi-semecki-suhofrukty', '/cat/mc/108/med-varene-dzemy-siropy']


def timer(func: Callable) -> Callable:
    """
    Декоратор функции, выполняющий логирование времени работы
    :param func: Callable
    :return:
    """
    def wrapper(*args, **kwargs):
        print(f'||| Запуска парсинга начался - {datetime.now()} |||\n{"=" * 30}')
        result = func(*args, **kwargs)
        print(f'{"=" * 30}\n||| Парсинг завершил работу - {datetime.now()} |||')

        return result
    return wrapper


def get_data(url: str) -> BeautifulSoup:
    count = 1
    for _ in range(3):
        if count > 1:
            print(f'Повторная попытка запроса. Всего {count} из 3')
        try:
            res = requests.get(url)
            res.encoding = 'utf-8'
            doc = BeautifulSoup(res.text, 'lxml')
        except Exception as ex:
            print(f'\n---!!!--- Произошла ошибка ответа сервера ---!!!---'
                  f'\nОписание ошибки: {ex}\n')
            time.sleep(5)
        else:
            return doc
        finally:
            count += 1


def get_card_links(lst: list) -> None:
    for chapter_link in lst:
        doc = get_data(f'{base_url}{chapter_link}')
        categories_link = [link.get('href') for link in doc.find_all('a', 'products-slider__header')]
        for category_link in categories_link:
            doc = get_data(f'{base_url}{category_link}')
            products_link = [link.get('href') for link in doc.find_all('a', 'product-card__link')]
            with open('card_links.txt', 'a', encoding='utf-8') as file:
                for product_link in products_link:
                    file.write(f'{product_link}\n')


@timer
def search_data(card_links: str) -> None:
    """
    Ведет поиск данных, сохраняет изображение и записывает данные в json по завершению
    :param category_link: Ожидается спиоск url
    :return: None
    """
    data = {}

    for card in card_links:
        file_name_end = card_links.split('/')[-1]
        repeat = False

        for _ in range(2):
            if repeat:
                print('\nПовторная попытка поиска\n')

            doc = get_data(f'{base_url}{card}')
            categories = [cat.text for cat in doc.find_all('span', 'breadcrumb') if
                          cat.text not in ['Главная', 'Каталог']]

            try:
                name = doc.find('h1', 'product__title').text
                image_url = doc.find(class_='product__gallery').find('img').get('src')
                image = requests.get(image_url).content
                nature_val = [val.text for val in doc.find_all('div', 'product-calories-item__value')]
                nature_key = [key.text for key in doc.find_all('div', 'product-calories-item__title')]
                nature_dict = dict(zip(nature_key, nature_val))
            except Exception as ex:
                print(f'---!!!--- ОШИБКА ПОИСКА ---!!!---'
                      f'\n\tmessage: {ex}'
                      f'\n\tlink: {base_url}{card}'
                      f'\n\tname: {doc.find("h1", "product__title")}'
                      f'\n\timage: {doc.find(class_="product__gallery").find("img").get("src")}'
                      f'\n\tvalue: {doc.find_all("div", "product-calories-item__value")}'
                      f'\n\tkey: {doc.find_all("div", "product-calories-item__title")}\n')
                repeat = True
            else:
                if data.get(categories[-1], None):
                    data[categories[-1]][name] = nature_dict
                else:
                    data.setdefault(categories[-1], {
                        name: nature_dict,
                        'image_name': f'img_{file_name_end}.jpg'
                    })
                print(f'+ Товар {name} | {nature_dict}')

                with open(f'images/img_{file_name_end}.jpg', 'wb') as img:
                    img.write(image)
                print(f'+ Изображение img_{file_name_end}.jpg')
                break

    with open(f'files/data.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    get_card_links(links_categories)
    with open('card_links.txt', 'r', encoding='utf-8') as file:
        search_data(file.readlines())


if __name__ == '__main__':
    main()





