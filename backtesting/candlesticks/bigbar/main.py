from datetime import date, time, timedelta, datetime
from typing import List

from backtesting.candlesticks.common import fetch_nifty_ticks, get_candlesticks_from_tick_price
from backtesting.candlesticks.entities import DailyTrading, Tick, Candlestick, Trade
from price_app.constants import MARKET_START_TIME, MARKET_CLOSE_TIME


class Config:
    start_date = date(2024, 9, 18)
    end_date = date(2024, 9, 18)
    time_slots = [
        [time(7, 0), time(10,  30)]
    ]
    candle_time_length_in_sec = 20
    big_bar_length = 5
    fixed_stoploss = 5
    fixed_target = 10


def perform_strategy_for_today_for_timeslot(
        candlesticks: List[Candlestick],
        start_time: time,
        end_time: time,
) -> List[Trade]:
    trades: List[Trade] = []

    i = 0
    n = len(candlesticks)
    while i < n and candlesticks[i].time < start_time:
        i += 1

    print(f'entry candle start time: {candlesticks[i].time}')

    # simulate trading
    while i < n-1:
        candlestick = candlesticks[i]

        if candlestick.body >= Config.big_bar_length:
            # take long position
            i += 1
            candlestick = candlesticks[i]

            entry_price = candlestick.open
            target = entry_price + Config.fixed_target
            stoploss = entry_price - Config.fixed_stoploss

            trade = Trade(candlestick.date, candlestick.time, entry_price)

            j = i
            while j < n and candlesticks[j].time <= end_time:
                if candlesticks[j].low <= stoploss:
                    trade.exit_time = candlesticks[j].time
                    trade.exit_price = stoploss
                    break
                elif candlesticks[j].low >= target:
                    trade.exit_time = candlesticks[j].time
                    trade.exit_price = target
                    break
                else:
                    j += 1

            if trade.exit_price is None:
                j -= 1
                trade.exit_time = candlesticks[j].time
                trade.exit_price = candlesticks[j].close

            trade.calculate_gain('up')
            trades.append(trade)
            i = j + 1
        elif candlestick.body <= -1 * Config.big_bar_length:
            # take short position
            i += 1
            candlestick = candlesticks[i]

            entry_price = candlestick.open
            target = entry_price - Config.fixed_target
            stoploss = entry_price + Config.fixed_stoploss

            trade = Trade(candlestick.date, candlestick.time, entry_price)

            j = i
            while j < n and candlesticks[j].time <= end_time:
                if candlesticks[j].high >= stoploss:
                    trade.exit_time = candlesticks[j].time
                    trade.exit_price = stoploss
                    break
                elif candlesticks[j].low <= target:
                    trade.exit_time = candlesticks[j].time
                    trade.exit_price = target
                    break
                else:
                    j += 1

            if trade.exit_price is None:
                j -= 1
                trade.exit_time = candlesticks[j].time
                trade.exit_price = candlesticks[j].close

            trade.calculate_gain('down')
            trades.append(trade)
            i = j + 1
        else:
            i += 1

    return trades


def perform_strategy_for_today(date: date) -> DailyTrading:
    ticks: List[Tick] = fetch_nifty_ticks(
        datetime.combine(date, MARKET_START_TIME),
        datetime.combine(date, MARKET_CLOSE_TIME),
    )

    print(f'first tick: {ticks[0].timestamp}')
    print(f'last tick: {ticks[len(ticks)-1].timestamp}')

    candlesticks: List[Candlestick] = \
        get_candlesticks_from_tick_price(ticks, Config.candle_time_length_in_sec)

    # print(f'candlesticks: {[candlestick.to_dict() for candlestick in candlesticks]}')

    daily_trading = DailyTrading(date)
    for time_slot in Config.time_slots:
        print(f'calculating for slot: {time_slot}')
        trades: List[Trade] = perform_strategy_for_today_for_timeslot(candlesticks, time_slot[0], time_slot[1])
        daily_trading.append_trades(trades)

    return daily_trading


def perform_strategy() -> List[DailyTrading]:
    daily_tradings: List[DailyTrading] = []

    today = Config.start_date
    while today <= Config.end_date:
        daily_trading: DailyTrading = perform_strategy_for_today(today)
        daily_tradings.append(daily_trading)

        today += timedelta(days=1)

    return daily_tradings


def main():
    daily_tradings: List[DailyTrading] = perform_strategy()

    for daily_trading in daily_tradings:
        for trade in daily_trading.trades:
            print(f'{trade.date} <--> {trade.entry_time} {trade.entry_price} <--> {trade.exit_time} {trade.exit_price} <--> {trade.gain}')


if __name__ == '__main__':
    main()
