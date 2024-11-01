from datetime import datetime, date, time, timedelta
from typing import List


class Tick:
    def __init__(
            self,
            timestamp: datetime,  # input time stamp must be in UTC
            price: float
    ):
        self.timestamp = timestamp + timedelta(hours=5, minutes=30)
        self.price = price


class Candlestick:
    def __init__(
            self,
            length_in_sec: int,
            date: date,
            time: time,
            open: float,
            high: float,
            low: float,
            close: float,
    ):
        self.length_in_sec = length_in_sec
        self.date = date
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def to_dict(self):
        return {
            'length_in_sec': self.length_in_sec,
            'date': self.date,
            'time': self.time,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
        }

    def add_tick_price(self, price: float):
        if self.open is None or self.low is None or \
                self.high is None or self.close is None:
            raise Exception('either of open, low, high, cloe price is none')

        self.low = min(self.low, price)
        self.high = max(self.high, price)
        self.close = price

        return self

    @property
    def body(self) -> float:
        return self.close - self.open

    @property
    def body_length(self):
        return abs(self.body)


class Trade:
    def __init__(
            self,
            date: date,
            entry_time: time,
            entry_price: float,
            exit_time: time = None,
            exit_price: float = None,
            gain: float = 0,
    ):
        self.date = date
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.gain = gain

    def calculate_gain(self, direction: str):
        if self.entry_price is None or self.exit_price is None:
            raise Exception(f'not able to calculate gain. '
                            f'entry_price: {self.entry_price}, '
                            f'exit_price: {self.exit_price}')

        if direction == 'up':
            self.gain = self.exit_price - self.entry_price
        elif direction == 'down':
            self.gain = self.entry_price - self.exit_price
        else:
            raise Exception(f'invalid direction string: {direction}')

        return self


class DailyTrading:
    def __init__(self, today: date):
        self.date = today
        self.trades: List[Trade] = []
        self.net_gain = 0

    def append_trades(self, trades: List[Trade]):
        for trade in trades:
            self.trades.append(trade)
            self.net_gain += trade.gain

        return self

    def calculate_summary(self):
        for trade in self.trades:
            self.net_gain += trade.gain

        return self
