from django import http
from datetime import datetime, date, time
from django.http import JsonResponse
from stock_data_fetch.common import time_format_string, date_format_string
from typing import TypedDict, List

from stock_data_fetch.enums import MarketType

class PriceDataPerSecond(TypedDict):
    dt: date
    tm: time
    price: float

class PriceData(TypedDict):
    market_name: MarketType
    price_list: List[PriceDataPerSecond]


def price_data_to_dict(price_data: PriceData) -> dict:
    return {
        'market_name': price_data['market_name'].value,
        'price_data': [{
            'dt': price_data_per_second['dt'].strftime(date_format_string),
            'tm': price_data_per_second['tm'].strftime(time_format_string),
            'price': price_data_per_second['price'],
        } for price_data_per_second in price_data['price_list']],
    }


def fetch_price_data(
        market_type: MarketType,
        from_date: date,
        to_date: date,
        from_time: time,
        to_time: time,
) -> dict:
    """TODO"""


def fetch_price(request: http.HttpRequest):
    market_name = MarketType(request.GET['market'])

    from_date = datetime.strptime(request.GET['from_date'], date_format_string).date()
    to_date = datetime.strptime(request.GET['to_date'], date_format_string).date()

    from_time = datetime.strptime(request.GET['from_time'], time_format_string).time()
    to_time = datetime.strptime(request.GET['to_time'], time_format_string).time()

    price_data: dict = fetch_price_data(MarketType(market_name), from_date, to_date, from_time, to_time)

    return JsonResponse(price_data_to_dict(price_data))
