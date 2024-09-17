from django import http
from datetime import datetime, date, time, timedelta
from django.http import JsonResponse
from typing import TypedDict, List

from common.constants import date_format_string, time_format_string
from price_app.models import BankNiftyPrice, NiftyPrice
from stock_data_fetch.enums import MarketType


class PriceDataPerTick(TypedDict):
    dt: date
    tm: time
    price: float


class PriceData(TypedDict):
    market_name: MarketType
    price_list: List[PriceDataPerTick]


def price_data_to_dict(price_data: PriceData) -> dict:
    return {
        'market_name': price_data['market_name'].value,
        'price_data': [{
            'dt': price_data_per_tick['dt'].strftime(date_format_string),
            'tm': price_data_per_tick['tm'].strftime(time_format_string),
            'price': price_data_per_tick['price'],
        } for price_data_per_tick in price_data['price_list']],
    }


def get_price_data_per_tick(timestamp: datetime, price: float) -> PriceDataPerTick:
    ist_timestamp = timestamp + timedelta(hours=5, minutes=30)

    return PriceDataPerTick(
        dt=ist_timestamp.date(),
        tm=ist_timestamp.time(),
        price=price,
    )


def fetch_nifty_price_data(
        start_timestamp: datetime,
        to_timestamp: datetime,
) -> PriceData:
    nifty_prices: List[NiftyPrice] = NiftyPrice.objects.filter(
        timestamp__gte=start_timestamp,
        timestamp__lte=to_timestamp,
    )

    return PriceData(
        market_name=MarketType.NIFTY,
        price_list=[get_price_data_per_tick(price_details.timestamp, price_details.price)
                    for price_details in nifty_prices]
    )


def fetch_banknifty_price_data(
        start_timestamp: datetime,
        to_timestamp: datetime,
) -> PriceData:
    bank_nifty_prices: List[BankNiftyPrice] = BankNiftyPrice.objects.filter(
        timestamp__gte=start_timestamp,
        timestamp__lte=to_timestamp,
    )

    return PriceData(
        market_name=MarketType.BANKNIFTY,
        price_list=[get_price_data_per_tick(price_details.timestamp, price_details.price)
                    for price_details in bank_nifty_prices]
    )


def fetch_price_data(
        market_type: MarketType,
        from_date: date,
        to_date: date,
        from_time: time,
        to_time: time,
) -> PriceData:
    start_timestamp = datetime.combine(from_date, from_time) + timedelta(microseconds=0)
    to_timestamp = datetime.combine(to_date, to_time) + timedelta(microseconds=0)

    if market_type == MarketType.NIFTY:
        return fetch_nifty_price_data(start_timestamp, to_timestamp)
    if market_type == MarketType.BANKNIFTY:
        return fetch_banknifty_price_data(start_timestamp, to_timestamp)

    raise Exception(f'invalid market type: {market_type}')


def fetch_price(request: http.HttpRequest):
    market_name = MarketType(request.GET['market'])

    from_date = datetime.strptime(request.GET['from_date'], date_format_string).date()
    to_date = datetime.strptime(request.GET['to_date'], date_format_string).date()

    from_time = datetime.strptime(request.GET['from_time'], time_format_string).time()
    to_time = datetime.strptime(request.GET['to_time'], time_format_string).time()

    price_data: PriceData = fetch_price_data(MarketType(market_name), from_date, to_date, from_time, to_time)

    return JsonResponse(price_data_to_dict(price_data))
