from typing import List
from datetime import datetime, date, time
from backtesting.candlesticks.entities import Tick, Candlestick
from price_app.handlers import fetch_price_from_database
from price_app.models import NiftyPrice
from stock_data_fetch.enums import MarketType


def get_candlesticks_from_tick_price(tick_prices: List[Tick], length_in_sec: int) -> List[Candlestick]:
    if len(tick_prices) == 0:
        raise Exception("tick_prices[]'s length can't be ZERO")

    start_tick: Tick = tick_prices[0]
    cur_candle = Candlestick(
        length_in_sec, start_tick.timestamp.date(), start_tick.timestamp.time(),
        start_tick.price, start_tick.price, start_tick.price, start_tick.price,
    )
    prev_tick_time = cur_candle.time

    candlesticks: List[Candlestick] = []
    for i in range(len(tick_prices)):
        if i == 0:
            continue

        tick = tick_prices[i]

        if get_time_diff(prev_tick_time, tick.timestamp.time()) >= length_in_sec:
            candlesticks.append(cur_candle)

            cur_candle = Candlestick(
                length_in_sec, tick.timestamp.date(), tick.timestamp.time(),
                tick.price, tick.price, tick.price, tick.price,
            )
            prev_tick_time = cur_candle.time
        else:
            cur_candle.add_tick_price(tick.price)

    return candlesticks


def fetch_nifty_ticks(
    start_timestamp: datetime,
    to_timestamp: datetime,
) -> List[Tick]:
    ticks: List[Tick] = []

    nifty_prices: List[NiftyPrice] = fetch_price_from_database(
        MarketType.NIFTY,
        start_timestamp,
        to_timestamp,
    )

    for nifty_price in nifty_prices:
        ticks.append(Tick(nifty_price.timestamp, nifty_price.tick_price))

    return ticks


def get_time_diff(prev_time: time, cur_time: time) -> int:
    date_today = date.today()
    datetime1 = datetime.combine(date_today, prev_time)
    datetime2 = datetime.combine(date_today, cur_time)

    time_difference = datetime2 - datetime1
    seconds_difference = int(time_difference.total_seconds())

    return seconds_difference
