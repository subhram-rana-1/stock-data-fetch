import threading

from price_app.classes import PriceData
import hashlib


lock_price_info_cache = threading.Lock()
price_info_cache: dict = {}


def get_price_data_cache_key(
        market_type: str,
        start_timestamp: str,
        to_timestamp: str,
        smooth_price_averaging_method: str,
        smooth_price_period: int,
        smooth_price_ema_period: int,
        smooth_slope_averaging_method: str,
        smooth_slope_period: int,
        smooth_slope_ema_period: int,
        smooth_momentum_period: int,
        smooth_momentum_ema_period: int,
) -> str:
    concatenated_string = (
            market_type +
            start_timestamp +
            to_timestamp +
            smooth_price_averaging_method +
            str(smooth_price_period) +
            str(smooth_price_ema_period) +
            smooth_slope_averaging_method +
            str(smooth_slope_period) +
            str(smooth_slope_ema_period) +
            str(smooth_momentum_period) +
            str(smooth_momentum_ema_period)
    )

    return hashlib.md5(concatenated_string.encode()).hexdigest()


def get_price_data_from_cache(cache_key: str) -> PriceData:
    if cache_key in price_info_cache.keys():
        print(f'fetching price from cache for key: {cache_key}')
        return price_info_cache[cache_key]

    return None


def add_key_value_to_cache(key: str, val):
    with lock_price_info_cache:
        if key not in price_info_cache.keys():
            print(f'adding to price cache, key: {key}')
            price_info_cache[key] = val
