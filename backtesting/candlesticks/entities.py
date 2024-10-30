from datetime import datetime


class Tick:
    def __init__(
            self,
            timestamp: datetime,
            price: float
    ):
        self.timestamp = timestamp
        self.price = price


class Candlestick:
    def __init__(
            self,
            length_in_sec: int,
            timestamp: datetime,
            open: float,
            high: float,
            low: float,
            close: float,
    ):
        self.length_in_sec = length_in_sec
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def add_tick_price(self, price: float):
        if self.open is None or self.low is None or \
                self.high is None or self.close is None:
            raise Exception('either of open, low, high, cloe price is none')

        self.low = min(self.low, price)
        self.high = max(self.high, price)
        self.close = price
