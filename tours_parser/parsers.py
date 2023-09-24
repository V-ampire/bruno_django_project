from decimal import Decimal
from typing import NamedTuple
import re

import requests

from bs4 import BeautifulSoup

from tours.models import Tour
from tours_parser.models import ToursProviders


class ParsedTour(NamedTuple):
    name: str
    description: str
    price: Decimal
    price_on_request: bool
    duration: int
    provider_label: str
    # schedule: Добавить инфу для сохрания расписания


class ParusParser:
    """Класс реализует логику выкачивая инфы из источников."""

    def __init__(self, provider):
        self.provider = provider
        self.label = self.provider.label
        self.base_url = self.provider.base_url
        self.session = requests.Session()

    def get_html(self, url):
        """Скачать HTML-страницу и вернуть объект BeautifulSoup."""
        response = self.session.get(url)
        if response.status_code >= 400:
            print(f'Ошибка при загрузке страницы {url}')
            return ''
        return response.text

    def parse_main_content_parapraphs(self, main_content_tag):
            """Парсим параграфы"""
            return '\n'.join([f"<p>{p.text}</p>" for p in main_content_tag.find_all('p')])

    def parse_main_content_schedule(self, main_content_tag):
        """Парсим программу экскурсии если она есть"""
        if not main_content_tag.find('ol'):
            return ''

        schedule_items = main_content_tag.find('ol').find_all('li')
        items_text = '\n'.join([f"<p>{item.text}</p>" for item in schedule_items])
        return """<h4>Программа экскурсии:</h4>
        {items_text}
        """

    def get_tour_description(self, tag):
        """Возвращаем строку с html-тегами чтобы красиво отображать у нас на странице"""
        print(f"Парсим описание для {tag.find('h4', class_='tour__title').text}")
        detail_url = tag.find('a', class_='tour__header').get('href')
        html = self.get_html(detail_url)
        if not html:
            # Не смогли загрузить страницу
            return ''
        # Сначала простое описание в абзацах
        soup = BeautifulSoup(html, 'html.parser')
        main_content_tags = soup.find_all('div', class_='tours-content')
        paragraphs_text = '\n'.join(self.parse_main_content_parapraphs(tag) for tag in main_content_tags)
        schedule_text =  '\n'.join(self.parse_main_content_parapraphs(tag) for tag in main_content_tags)
        # Теперь то что входит в стоимость тура если она указана
        cost_info = soup.find('div', class_='cost_block')
        if cost_info:
            cost_items_text = '\n'.join([f"<li>{item.text}</li>" for item in cost_info.find_all('li')])
        else:
            cost_items_text = ''
        return f"""
        {paragraphs_text}
        <h4>В стоимость входит:</h4>
        {cost_items_text}
        """

    def get_duration(self, tag):
        # Вытащить количесвто максимум минут из строк типа 2,5 - 3,5 часа, 7-8 часов и т.д.
        pattern = '[-+]?[0-9]*[.,]?[0-9]+(?:[eE][-+]?[0-9]+)?'
        durations_str = tag.find('span', class_='tour__duration').text
        # Нахожу максимальную продолжительность в минутах
        # Сначала используя рег. выражения находим все числа типа 3 или 3,5
        # Потом заменяем запятые на точки и приводим к float
        # Умножаем на 60 так как у паруса все в часах и делаем число целым так как база хранит целые числа
        return max([int(float(num.replace(',', '.')) * 60) for num in re.findall(pattern, durations_str)])

    def get_price(self, tag):
        price_tag = tag.find('div', class_='tour__cost').find('span', class_='ajax_price')
        if price_tag:
            return Decimal(price_tag.text)

    def parse_tours(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        all_tours = soup.find('div', id='tours')
        tour_tags = all_tours.find_all('div', class_='tour')
        tours = []
        for tag in tour_tags:
            if not tag.get('class') or 'promo' in tag.get('class', []):
                continue
            price = self.get_price(tag)
            price_on_request = not bool(price)
            name = tag.find('h4', class_='tour__title').text
            print(f'Парсим {name}')
            tours.append(ParsedTour(
                name=tag.find('h4', class_='tour__title').text,
                description=self.get_tour_description(tag),
                price=price,
                price_on_request=price_on_request,
                duration=self.get_duration(tag),
                provider_label=self.label
            ))
        return tours

    def save_in_db(self, parsed_tours):
        tours_to_create = []
        for parsed_tour in parsed_tours:
            tours_to_create.append(Tour(
                provider=self.provider,
                name=parsed_tour.name,
                description=parsed_tour.description,
                price=parsed_tour.price,
                price_on_request=parsed_tour.price_on_request,
                duration=parsed_tour.duration
            ))
        Tour.objects.bulk_create(tours_to_create)
        return tours_to_create

    def parse(self):
        html = self.get_html(self.base_url)
        parsed_tours = self.parse_tours(html)
        save_tours = self.save_in_db(parsed_tours)
        print(f"Скачали {len(save_tours)} туров из {self.provider.name}")


if __name__ == '__main__':
    Tour.objects.all().delete()
    provider = ToursProviders.objects.all().first()
    parser = ParusParser(provider)
    tours = parser.parse()
