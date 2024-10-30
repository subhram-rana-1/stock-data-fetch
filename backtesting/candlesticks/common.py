from typing import List

from backtesting.candlesticks.entities import Tick, Candlestick


def get_candlesticks_from_tick_price(tick_prices: List[Tick], length_in_sec: int) -> List[Candlestick]:
    if len(tick_prices) == 0:
        raise Exception("tick_prices[]'s length can't be ZERO")

    start_tick: Tick = tick_prices[0]
    cur_candle = Candlestick(
        length_in_sec, start_tick.timestamp,
        start_tick.price, start_tick.price, start_tick.price, start_tick.price,
    )
    prev_tick_time = cur_candle.timestamp

    candlesticks: List[Candlestick] = []
    for i in range(len(tick_prices)):
        if i == 0:
            continue

        tick = tick_prices[i]

        if int((tick.timestamp - prev_tick_time).total_seconds()) >= length_in_sec:
            candlesticks.append(cur_candle)

            cur_candle = Candlestick(
                length_in_sec, tick.timestamp,
                tick.price, tick.price, tick.price, tick.price,
            )
            prev_tick_time = cur_candle.timestamp
        else:
            cur_candle.add_tick_price(tick.price)

    return candlesticks
