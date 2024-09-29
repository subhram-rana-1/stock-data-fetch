from typing import TypedDict, List
from datetime import datetime, date, time, timedelta
from common.constants import date_format_string, time_format_string
from price_app.utils import calculate_ema, calculate_sma
from stock_data_fetch.enums import MarketType
from . import configs


class PriceDataPerTick(TypedDict):
    dt: date
    tm: time
    tick_price: float
    smooth_price: float
    smooth_price_ema: float
    slope: float
    smooth_slope: float
    smooth_slope_ema: float
    momentum: float
    smooth_momentum: float
    smooth_momentum_ema: float
    momentum_rate: float


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
            'smooth_price': round(price_data_per_tick.get('smooth_price'), 2) \
                if price_data_per_tick.get('smooth_price') is not None else None,
            'smooth_price_ema': round(price_data_per_tick.get('smooth_price_ema'), 2) \
                if price_data_per_tick.get('smooth_price_ema') is not None else None,
            'slope': round(price_data_per_tick.get('slope'), 2) \
                if price_data_per_tick.get('slope') is not None else None,
            'smooth_slope': round(price_data_per_tick.get('smooth_slope'), 2) \
                if price_data_per_tick.get('smooth_slope') is not None else None,
            'smooth_slope_ema': round(price_data_per_tick.get('smooth_slope_ema'), 2) \
                if price_data_per_tick.get('smooth_slope_ema') is not None else None,
            'momentum': round(price_data_per_tick.get('momentum'), 2) \
                if price_data_per_tick.get('momentum') is not None else None,
            'smooth_momentum': round(price_data_per_tick.get('smooth_momentum'), 2) \
                if price_data_per_tick.get('smooth_momentum') is not None else None,
            'smooth_momentum_ema': round(price_data_per_tick.get('smooth_momentum_ema'), 2) \
                if price_data_per_tick.get('smooth_momentum_ema') is not None else None,
            'momentum_rate': round(price_data_per_tick.get('momentum_rate'), 2) \
                if price_data_per_tick.get('momentum_rate') is not None else None,
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
        smooth_price_averaging_method: str,
        smooth_price_period: int,
        smooth_price_ema_period: int,
        smooth_slope_averaging_method: str,
        smooth_slope_period: int,
        smooth_slope_ema_period: int,
        smooth_momentum_period: int,
        smooth_momentum_ema_period: int,
):
    if len(price_data['price_list']) == 0:
        return

    calculate_smooth_price(price_data, smooth_price_averaging_method, smooth_price_period)
    calculate_smooth_price_ema(price_data, smooth_price_ema_period)

    calculate_slope(price_data)
    calculate_smooth_slope(price_data, smooth_slope_averaging_method, smooth_slope_period)
    calculate_smooth_slope_ema(price_data, smooth_slope_ema_period)

    calculate_momentum(price_data)

    if smooth_momentum_period is not None:
        calculate_smooth_momentum(price_data, smooth_momentum_period)

    if smooth_momentum_ema_period is not None:
        calculate_smooth_momentum_ema(price_data, smooth_momentum_ema_period)

    if smooth_momentum_period is not None and smooth_momentum_ema_period is not None:
        calculate_momentum_rate(price_data)


def calculate_smooth_price(price_data: PriceData, smooth_price_averaging_method: str, smooth_price_period: int):
    price_list = price_data['price_list']
    if price_list[0].get('tick_price') is None:
        raise Exception('tick price is not calculated. Hence '
                        'smooth price can\'t be calculated')

    tick_prices = [price['tick_price'] for price in price_list]

    if smooth_price_averaging_method == 'simple':
        smooth_prices = calculate_sma(tick_prices, smooth_price_period)
    elif smooth_price_averaging_method == 'exponential':
        smooth_prices = calculate_ema(tick_prices, smooth_price_period)
    else:
        smooth_prices = calculate_sma(tick_prices, smooth_price_period)

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


def calculate_smooth_slope(price_data: PriceData, smooth_slope_averaging_method: str, smooth_slope_period: int):
    price_list = price_data['price_list']
    if price_list[0].get('slope') is None:
        raise Exception('slope is not calculated. Hence '
                        'smooth slope can\'t be calculated')

    slopes = [price['slope'] for price in price_list]

    if configs.smooth_slope_averaging_method == 'simple':
        smooth_slopes = calculate_sma(slopes, smooth_slope_period)
    elif configs.smooth_slope_averaging_method == 'exponential':
        smooth_slopes = calculate_ema(slopes, smooth_slope_period)
    else:
        smooth_slopes = calculate_sma(slopes, smooth_slope_period)

    for i in range(len(price_list)):
        price_list[i]['smooth_slope'] = smooth_slopes[i]


def calculate_smooth_slope_ema(price_data: PriceData, smooth_slope_ema_period: int):
    price_list = price_data['price_list']
    if price_list[0].get('smooth_slope') is None:
        raise Exception('smooth slope is not calculated. Hence '
                        'smooth slope ema can\'t be calculated')

    smooth_slopes = [price['smooth_slope'] for price in price_list]
    smooth_slope_emas = calculate_ema(smooth_slopes, smooth_slope_ema_period)
    for i in range(len(price_list)):
        price_list[i]['smooth_slope_ema'] = smooth_slope_emas[i]


def calculate_momentum(price_data: PriceData):
    price_list = price_data['price_list']
    if price_list[0].get('smooth_slope') is None or \
            price_list[0].get('smooth_slope_ema') is None:
        raise Exception('either smooth slope or smooth slope ema is not calculated. Hence '
                        'divergence can\'t be calculated')

    for i in range(len(price_list)):
        price_list[i]['momentum'] = price_list[i]['smooth_slope'] - price_list[i]['smooth_slope_ema']


def calculate_smooth_momentum(price_data: PriceData, smooth_momentum_period: int):
    price_list = price_data['price_list']
    if price_list[0].get('momentum') is None:
        raise Exception('momentum is not calculated. Hence '
                        'smooth momentum can\'t be calculated')

    momentums = [price['momentum'] for price in price_list]

    if configs.smooth_momentum_averaging_method == 'simple':
        smooth_momentums = calculate_sma(momentums, smooth_momentum_period)
    elif configs.smooth_momentum_averaging_method == 'exponential':
        smooth_momentums = calculate_ema(momentums, smooth_momentum_period)
    else:
        smooth_momentums = calculate_sma(momentums, smooth_momentum_period)

    for i in range(len(price_list)):
        price_list[i]['smooth_momentum'] = smooth_momentums[i]


def calculate_smooth_momentum_ema(price_data: PriceData, smooth_momentum_ema_period: int):
    price_list = price_data['price_list']
    if price_list[0].get('smooth_momentum') is None:
        raise Exception('smooth momentum is not calculated. Hence '
                        'smooth momentum ema can\'t be calculated')

    smooth_momentum = [price['smooth_momentum'] for price in price_list]
    smooth_momentum_emas = calculate_ema(smooth_momentum, smooth_momentum_ema_period)
    for i in range(len(price_list)):
        price_list[i]['smooth_momentum_ema'] = smooth_momentum_emas[i]


def calculate_momentum_rate(price_data: PriceData):
    price_list = price_data['price_list']
    if price_list[0].get('smooth_momentum') is None or \
            price_list[0].get('smooth_momentum_ema') is None:
        raise Exception('either smooth momentum or smooth momentum ema is not calculated. Hence '
                        'momentum_rate can\'t be calculated')

    for i in range(len(price_list)):
        price_list[i]['momentum_rate'] = price_list[i]['smooth_momentum'] - price_list[i]['smooth_momentum_ema']
