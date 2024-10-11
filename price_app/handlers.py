from django import http
from datetime import datetime, date, time, timedelta
from django.http import JsonResponse
from typing import List
from django.views.decorators.csrf import csrf_exempt
from common.constants import date_format_string, time_format_string, datetime_format_string
from price_app.classes import PriceData, get_price_data_per_tick, calculate_other_auxiliary_prices
from price_app.models import BankNiftyPrice, NiftyPrice
from price_app.classes import price_data_to_dict
from stock_data_fetch.enums import MarketType
from . import configs
from .cache import get_price_data_cache_key, get_price_data_from_cache, add_key_value_to_cache, cache_key, \
    get_from_cache, add_to_cache


def fetch_price_from_database(
        market: MarketType,
        start_timestamp: datetime,
        end_timestamp: datetime,
) -> List:
    key = cache_key(market, start_timestamp, end_timestamp)
    price_data = get_from_cache(key)
    if price_data is not None:
        return price_data

    if market == MarketType.NIFTY:
        price_data = NiftyPrice.objects.filter(
            timestamp__gte=start_timestamp,
            timestamp__lte=end_timestamp,
        )
    elif market == MarketType.BANKNIFTY:
        price_data = BankNiftyPrice.objects.filter(
            timestamp__gte=start_timestamp,
            timestamp__lte=end_timestamp,
        )

    add_to_cache(key, price_data)

    return price_data


def fetch_nifty_price_data(
        start_timestamp: datetime,
        to_timestamp: datetime,
        smooth_price_averaging_method: str,
        smooth_price_period: int,
        smooth_price_ema_period: int,
        smooth_slope_averaging_method: str,
        smooth_slope_period: int,
        smooth_slope_ema_period: int,
        smooth_momentum_period: int,
        smooth_momentum_ema_period: int,
) -> PriceData:
    nifty_prices: List[NiftyPrice] = fetch_price_from_database(
        MarketType.NIFTY,
        start_timestamp,
        to_timestamp,
    )

    price_data: PriceData = PriceData(
        market_name=MarketType.NIFTY,
        price_list=[get_price_data_per_tick(price_details.timestamp, price_details.tick_price)
                    for price_details in nifty_prices]
    )

    # optionally calculate other data points
    calculate_other_auxiliary_prices(
        price_data,
        smooth_price_averaging_method,
        smooth_price_period,
        smooth_price_ema_period,
        smooth_slope_averaging_method,
        smooth_slope_period,
        smooth_slope_ema_period,
        smooth_momentum_period,
        smooth_momentum_ema_period,
    )

    return price_data


def fetch_banknifty_price_data(
        start_timestamp: datetime,
        to_timestamp: datetime,
        smooth_price_averaging_method: str,
        smooth_price_period: int,
        smooth_price_ema_period: int,
        smooth_slope_averaging_method: str,
        smooth_slope_period: int,
        slope_ema_period: int,
        smooth_momentum_period: int,
        smooth_momentum_ema_period: int,
) -> PriceData:
    bank_nifty_prices: List[BankNiftyPrice] = fetch_price_from_database(
        MarketType.BANKNIFTY,
        start_timestamp,
        to_timestamp,
    )
    price_data: PriceData = PriceData(
        market_name=MarketType.BANKNIFTY,
        price_list=[get_price_data_per_tick(price_details.timestamp, price_details.tick_price)
                    for price_details in bank_nifty_prices]
    )

    # optionally calculate other data points
    calculate_other_auxiliary_prices(
        price_data,
        smooth_price_averaging_method,
        smooth_price_period,
        smooth_price_ema_period,
        smooth_slope_averaging_method,
        smooth_slope_period,
        slope_ema_period,
        smooth_momentum_period,
        smooth_momentum_ema_period,
    )

    return price_data


def get_cached_price_data(
        market_type: MarketType,
        start_timestamp: datetime,
        to_timestamp: datetime,
        smooth_price_averaging_method: str,
        smooth_price_period: int,
        smooth_price_ema_period: int,
        smooth_slope_averaging_method: str,
        smooth_slope_period: int,
        smooth_slope_ema_period: int,
        smooth_momentum_period: int,
        smooth_momentum_ema_period: int,
) -> (str, PriceData):
    cache_key = get_price_data_cache_key(
        market_type.name,
        start_timestamp.strftime(datetime_format_string),
        to_timestamp.strftime(datetime_format_string),
        smooth_price_averaging_method,
        smooth_price_period,
        smooth_price_ema_period,
        smooth_slope_averaging_method,
        smooth_slope_period,
        smooth_slope_ema_period,
        smooth_momentum_period,
        smooth_momentum_ema_period,
    )

    return cache_key, get_price_data_from_cache(cache_key)


# IMPORTANT FUNCTION #
# This is the function which can be used to run optimisation algorithm
def fetch_price_data(
        market_type: MarketType,
        from_date: date,
        to_date: date,
        from_time: time,
        to_time: time,

        smooth_price_averaging_method: str,
        smooth_price_period: int,
        smooth_price_ema_period: int,
        smooth_slope_averaging_method: str,
        smooth_slope_period: int,
        smooth_slope_ema_period: int,
        smooth_momentum_period: int = None,
        smooth_momentum_ema_period: int = None,
) -> PriceData:
    start_timestamp = datetime.combine(from_date, from_time) + timedelta(microseconds=0)
    to_timestamp = datetime.combine(to_date, to_time) + timedelta(microseconds=0)

    if market_type == MarketType.NIFTY:
        price_data = fetch_nifty_price_data(
            start_timestamp,
            to_timestamp,
            smooth_price_averaging_method,
            smooth_price_period,
            smooth_price_ema_period,
            smooth_slope_averaging_method,
            smooth_slope_period,
            smooth_slope_ema_period,
            smooth_momentum_period,
            smooth_momentum_ema_period,
        )
    elif market_type == MarketType.BANKNIFTY:
        price_data = fetch_banknifty_price_data(
            start_timestamp,
            to_timestamp,
            smooth_price_averaging_method,
            smooth_price_period,
            smooth_price_ema_period,
            smooth_slope_averaging_method,
            smooth_slope_period,
            smooth_slope_ema_period,
            smooth_momentum_period,
            smooth_momentum_ema_period,
        )
    else:
        raise Exception(f'invalid market type: {market_type}')

    # add_key_value_to_cache(cache_key, price_data)

    return price_data


@csrf_exempt
def fetch_price(request: http.HttpRequest):
    market_name = MarketType(request.GET['market'])
    from_date = datetime.strptime(request.GET['from_date'], date_format_string).date()
    to_date = datetime.strptime(request.GET['to_date'], date_format_string).date()
    from_time = datetime.strptime(request.GET['from_time'], time_format_string).time()
    to_time = datetime.strptime(request.GET['to_time'], time_format_string).time()

    info = {
        'market_name': market_name,
        'from_date': from_date,
        'to_date': to_date,
        'from_time': from_time,
        'to_time': to_time,
    }
    print(f'fetch price api: {info}')

    smooth_price_period = configs.smooth_price_period
    smooth_price_ema_period = configs.smooth_price_ema_period
    smooth_slope_ema_period = configs.smooth_slope_ema_period
    smooth_slope_period = configs.smooth_slope_period

    smooth_momentum_period = configs.smooth_momentum_period
    smooth_momentum_ema_period = configs.smooth_momentum_ema_period

    price_data: PriceData = fetch_price_data(
        MarketType(market_name),
        from_date, to_date,
        from_time, to_time,
        configs.smooth_price_averaging_method,
        smooth_price_period,
        smooth_price_ema_period,
        configs.smooth_slope_averaging_method,
        smooth_slope_period,
        smooth_slope_ema_period,
        smooth_momentum_period,
        smooth_momentum_ema_period,
    )

    return JsonResponse(price_data_to_dict(price_data))
