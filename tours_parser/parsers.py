from decimal import Decimal
from typing import NamedTuple

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

    def get_html(self):
        """Скачать HTML-страницу и вернуть объект BeautifulSoup."""
        response = self.session.get(self.base_url)
        response.raise_for_status()
        return response.text

    def get_tour_description(self, tag):
        # Скачать страничку тура
        # ытащить описание
        return ''

    def get_duration(self, tag):
        # Вытащить количесвто максимум минут из строк типа 2,5 - 3,5 часа, 7-8 часов и т.д.
        return 1

    def get_price(self, tag):
        price_tag = tag.find('div', class_='tour__cost').find('span', class_='ajax_price')
        if price_tag:
            return Decimal(price_tag.text)

    def parse_tours(self, html):
        soup = BeautifulSoup(html)
        all_tours = soup.find('div', id='tours')
        tour_tags = all_tours.find_all('div', class_='tour')
        tours = []
        for tag in tour_tags:
            if not tag.get('class') or 'promo' in tag.get('class', []):
                continue
            price = self.get_price(tag)
            price_on_request = not bool(price)
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
        save_tours = Tour.objects.bulk_create(tours_to_create)

    def parse(self):
        html = self.get_html()
        parsed_tours = self.parse_tours(html)
        save_tours = self.save_in_db(parsed_tours)
        print(f"Скачали {len(save_tours)} туров из {self.provider.name}")


if __name__ == '__main__':
    provider = ToursProviders.objects.all().first()
    parser = ParusParser(provider)
    tours = parser.parse()
