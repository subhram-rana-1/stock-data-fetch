from typing import TypedDict, List
from datetime import datetime, date, time, timedelta
from common.constants import date_format_string, time_format_string
from price_app.utils import calculate_ema
from stock_data_fetch.enums import MarketType


class PriceDataPerTick(TypedDict):
    dt: date
    tm: time
    tick_price: float
    smooth_price: float
    smooth_price_ema: float
    slope: float
    slope_ema: float
    divergence: float


class PriceData(TypedDict):
    market_name: MarketType
    price_list: List[PriceDataPerTick]


def price_data_to_dict(price_data: PriceData) -> dict:
    return {
        'market_name': price_data['market_name'].value,
        'price_data': [{
            'dt': price_data_per_tick['dt'].strftime(date_format_string),
            'tm': price_data_per_tick['tm'].strftime(time_format_string),
            'tick_price': price_data_per_tick['tick_price'],
            'smooth_price': round(price_data_per_tick.get('smooth_price'), 2),
            'smooth_price_ema': round(price_data_per_tick.get('smooth_price_ema'), 2),
            'slope': round(price_data_per_tick.get('slope'), 2),
            'slope_ema': round(price_data_per_tick.get('slope_ema'), 2),
            'divergence': round(price_data_per_tick.get('divergence'), 2),
        } for price_data_per_tick in price_data['price_list']],
    }


def get_price_data_per_tick(timestamp: datetime, price: float) -> PriceDataPerTick:
    ist_timestamp = timestamp + timedelta(hours=5, minutes=30)

    return PriceDataPerTick(
        dt=ist_timestamp.date(),
        tm=ist_timestamp.time(),
        tick_price=price,
    )


def calculate_other_auxiliary_prices(
        price_data: PriceData,
        smooth_price_period: int,
        smooth_price_ema_period: int,
        slope_ema_period: int,
):
    calculate_smooth_price(price_data, smooth_price_period)
    calculate_smooth_price_ema(price_data, smooth_price_ema_period)
    calculate_slope(price_data)
    calculate_slope_ema(price_data, slope_ema_period)
    calculate_divergence(price_data)


def calculate_smooth_price(price_data: PriceData, smooth_price_period: int):
    price_list = price_data['price_list']
    if price_list[0].get('tick_price') is None:
        raise Exception('tick price is not calculated. Hence '
                        'smooth price can\'t be calculated')

    tick_prices = [price['tick_price'] for price in price_list]
    smooth_prices = calculate_ema(tick_prices, smooth_price_period)
    for i in range(len(price_list)):
        price_list[i]['smooth_price'] = smooth_prices[i]


def calculate_smooth_price_ema(price_data: PriceData, smooth_price_ema_period: int):
    price_list = price_data['price_list']
    if price_list[0].get('smooth_price') is None:
        raise Exception('smooth price is not calculated. Hence '
                        'smooth price ema can\'t be calculated')

    smooth_price = [price['smooth_price'] for price in price_list]
    smooth_price_emas = calculate_ema(smooth_price, smooth_price_ema_period)
    for i in range(len(price_list)):
        price_list[i]['smooth_price_ema'] = smooth_price_emas[i]


def calculate_slope(price_data: PriceData):
    price_list = price_data['price_list']
    if price_list[0].get('smooth_price') is None or \
            price_list[0].get('smooth_price_ema') is None:
        raise Exception('either smooth price or smooth price ema is not calculated. Hence '
                        'slope can\'t be calculated')

    for i in range(len(price_list)):
        price_list[i]['slope'] = price_list[i]['smooth_price'] - price_list[i]['smooth_price_ema']


def calculate_slope_ema(price_data: PriceData, slope_ema_period: int):
    price_list = price_data['price_list']
    if price_list[0].get('slope') is None:
        raise Exception('slope is not calculated. Hence '
                        'slope ema can\'t be calculated')

    slope = [price['slope'] for price in price_list]
    slope_emas = calculate_ema(slope, slope_ema_period)
    for i in range(len(price_list)):
        price_list[i]['slope_ema'] = slope_emas[i]


def calculate_divergence(price_data: PriceData):
    price_list = price_data['price_list']
    if price_list[0].get('slope') is None or \
            price_list[0].get('slope_ema') is None:
        raise Exception('either slope or slope ema is not calculated. Hence '
                        'divergence can\'t be calculated')

    for i in range(len(price_list)):
        price_list[i]['divergence'] = price_list[i]['slope'] - price_list[i]['slope_ema']

    