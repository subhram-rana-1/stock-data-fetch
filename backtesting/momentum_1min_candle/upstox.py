import json
from datetime import date, datetime
from typing import List
import requests
import hashlib

from price_app.classes import PriceDataPerTick, PriceDataPerCandle
from stock_data_fetch.enums import MarketType

upstox_ts_format = "%Y-%m-%dT%H:%M:%S%z"
date_str_format = "%Y-%m-%d"
NIFTY_INSTRUMENT_TOKEN = "NSE_INDEX%7CNifty%2050"


class UpstoxPriceCache:
    price_cache = {}

    @classmethod
    def cache_key(
            cls,
            unique_instrument_token: str,
            start_date: date,
            end_date: date,
    ) -> str:
        concatenated_string = unique_instrument_token + \
                              start_date.strftime(date_str_format) + \
                              end_date.strftime(date_str_format)

        return hashlib.md5(concatenated_string.encode()).hexdigest()

    @classmethod
    def get_from_cache(cls, key: str):
        if key not in cls.price_cache:
            print(f'price info NOT available in cache for key: {key}')
            return None

        print(f'price info  AVAILABLE in cache for key: {key}')
        return cls.price_cache[key]

    @classmethod
    def add_to_cache(cls, key: str, val):
        print(f'adding price info to cache for key: {key}')
        cls.price_cache[key] = val


class Candle:
    def __init__(
            self,
            ts: datetime,
            open: float,
            high: float,
            lo: float,
            close: float,
    ):
        self.ts = ts
        self.open = open
        self.high = high
        self.lo = lo
        self.close = close

    @property
    def avg_price(self) -> float:
        return (self.open + self.high + self.lo + self.close) / 4

    def to_tick_by_tick_type_data(self) -> PriceDataPerCandle:
        return PriceDataPerCandle(
            dt=self.ts.date(),
            tm=self.ts.time(),
            open=self.open,
            high=self.high,
            lo=self.lo,
            close=self.close,
            tick_price=self.avg_price,
        )

    @classmethod
    def from_api_resp_candle_dict(cls, candle_dict: dict):
        return Candle(
            datetime.strptime(candle_dict[0], upstox_ts_format),
            candle_dict[1],
            candle_dict[2],
            candle_dict[3],
            candle_dict[4],
        )


class UpstoxCandlesticksData:
    def __init__(self, candles: List[Candle]):
        self.candles: List[Candle] = candles

    def _is_trading_day(self) -> bool:
        return len(self.candles) > 0


class UpstoxCandlestickResponse:
    def __init__(self, upstox_candlesticks_data: UpstoxCandlesticksData):
        self.status = 'success'
        self.data = upstox_candlesticks_data

    @classmethod
    def from_upstox_api_response(cls, resp: dict):
        candles = \
            [Candle.from_api_resp_candle_dict(candle_dict) for candle_dict in resp['data']['candles']]

        candles.reverse()

        return UpstoxCandlestickResponse(
            upstox_candlesticks_data=UpstoxCandlesticksData(candles),
        )


def fetch_candlestick_data_from_upstox(
        market_type: MarketType,
        start_date: date,
        end_date: date,
) -> UpstoxCandlestickResponse:
    if market_type == MarketType.NIFTY:
        unique_instrument_token = NIFTY_INSTRUMENT_TOKEN
    else:
        raise Exception(f'market type not supported in upstox: {market_type.name}')

    cache_key = UpstoxPriceCache.cache_key(unique_instrument_token, start_date, end_date)
    price_info: UpstoxCandlestickResponse = UpstoxPriceCache.get_from_cache(cache_key)
    if price_info is not None:
        return price_info

    resp = requests.get(
        url='https://api.upstox.com/v2/historical-candle/{}/1minute/{}/{}'
        .format(
            unique_instrument_token,
            end_date.strftime(date_str_format),
            start_date.strftime(date_str_format),
        )
    )

    if resp.status_code != 200:
        raise Exception(f'Upstox fetch api failed, status_code: {resp.status_code}')

    resp = UpstoxCandlestickResponse.from_upstox_api_response(json.loads(resp.content))
    UpstoxPriceCache.add_to_cache(cache_key, resp)

    return resp
