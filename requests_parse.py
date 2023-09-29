import time

import requests
import lxml
from bs4 import BeautifulSoup
import json
from datetime import datetime

base_url = 'https://www.perekrestok.ru'
ig = ['', 'Акции', 'Скидки', 'Готовая еда', 'Фестиваль пенного', 'От Перекрёстка', 'Молоко, сыр, яйца', 'Товары для мам и детей', 'Продукты быстрого приготовления', 'Зоотовары', 'Красота, гигиена, аптека', 'Уборка', 'Посуда', 'Для дома и дачи', 'Алкогольные напитки', 'Системы нагревания, табак']
links_categories = ['/cat/mc/242/hleb-i-vypecka', '/cat/mc/132/maso-i-ptica', '/cat/mc/782/kolbasnye-izdelia', '/cat/mc/174/ryba', '/cat/mc/793/moreprodukty', '/cat/mc/54/zamorozennye-produkty', '/cat/mc/217/sousy-ketcupy-majonezy', '/cat/mc/79/kofe-caj-kakao-sahar', '/cat/mc/224/suhie-zavtraki-musli', '/cat/mc/74/konservacia', '/cat/mc/64/zdorove', '/cat/mc/157/orehi-semecki-suhofrukty', '/cat/mc/108/med-varene-dzemy-siropy']


def timer(func):
    def wrapper(*args, **kwargs):
        print('_' * 30)
        print(f'||| Запуска парсинга начался - {datetime.now()} |||')
        print('#' * 30)
        result = func(*args, **kwargs)
        print('#' * 30)
        print(f'||| Функция завершила работу - {datetime.now()} |||')
        print('_' * 30)

        return result
    return wrapper


def get_data(url: str) -> BeautifulSoup:
    count = 0
    for _ in range(3):
        if count:
            print(f'Повторная попытка запроса. COUNT {count}')
        try:
            res = requests.get(url)
            res.encoding = 'utf-8'
            doc = BeautifulSoup(res.text, 'lxml')
        except Exception as ex:
            print(f'---!!!--- Произошла ошибка ответа сервера: {ex} ---!!!---')
            time.sleep(5)
        else:
            return doc
        finally:
            count += 1


@timer
def search_data(category_link: str) -> dict:
    data_dict = {}
    doc = get_data(category_link)
    categories_link = [link.get('href') for link in doc.find_all('a', 'products-slider__header')]
    for category_link in categories_link:
        doc = get_data(f'{base_url}{category_link}')
        products_link = [link.get('href') for link in doc.find_all('a', 'product-card__link')]
        for product_link in products_link:
            doc = get_data(f'{base_url}{product_link}')
            categories = [cat.text for cat in doc.find_all('span', 'breadcrumb') if cat.text not in ['Главная', 'Каталог']]
            try:
                name = doc.find('h1', 'product__title').text
                nature_val = [val.text for val in doc.find_all('div', 'product-calories-item__value')]
                nature_key = [key.text for key in doc.find_all('div', 'product-calories-item__title')]
                nature_dict = dict(zip(nature_key, nature_val))
            except Exception as ex:
                print(f'---!!!--- ОШИБКА ПОИСКА {ex} ---!!!---'
                      f'\nСсылка {base_url}{product_link}'
                      f'\nКод: '
                      f'\n\tname = doc.find("h1", "product__title").text'
                      f'\n\tnature_val = [val.text for val in doc.find_all("div", "product-calories-item__value")]'
                      f'\n\tnature_key = [key.text for key in doc.find_all("div", "product-calories-item__title")]'
                      f'\nЗначение без применения функций: '
                      f'\n\t{doc.find("h1", "product__title")}'
                      f'\n\t{doc.find_all("div", "product-calories-item__value")}'
                      f'\n\t{doc.find_all("div", "product-calories-item__title")}')
            else:
                if data_dict.get(categories[-1], None):
                    data_dict[categories[-1]][name] = nature_dict
                else:
                    data_dict.setdefault(categories[-1], {name: nature_dict})
                print(f'***Успешно получили данные {name} | {nature_dict}')

    return data_dict


num_file = 6
for link in links_categories:
    data = search_data(f'{base_url}{link}')
    with open(f'rec{num_file}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        print(print('=' * 30))
        print('Запись файла rec{num_file}.json прошла успешно.'
              '\nВремя: {time}'
              '\n{link_category}'.format(
            num_file=num_file,
            time=datetime.now(),
            link_category=link
        )
              )
        print(print('=' * 30))
    num_file += 1

