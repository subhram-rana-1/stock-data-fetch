from stock_data_fetch.enums import DjangoEnum, MarketType


class BacktestingStrategy(DjangoEnum):
    MOMENTUM_V1 = 'MOMENTUM_V1'


class BacktestingState(DjangoEnum):
    INITIATED = 'INITIATED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'


class Market(DjangoEnum):
    NIFTY = 'NIFTY'
    BANKNIFTY = 'BANKNIFTY'

    def to_price_app_market_type(self) -> MarketType:
        if self.name == Market.NIFTY.name:
            return MarketType.NIFTY
        elif self.name == Market.NIFTY.name:
            return MarketType.NIFTY
        else:
            raise Exception(f"market {self.name} can't be converted to MarketType")


class Direction(DjangoEnum):
    UP = 'UP'
    DOWN = 'DOWN'
