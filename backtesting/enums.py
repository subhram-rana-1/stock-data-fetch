from stock_data_fetch.enums import DjangoEnum


class BacktestingStrategy(DjangoEnum):
    MOMENTUM_V1 = 'MOMENTUM_V1'


class BacktestingState(DjangoEnum):
    INITIATED = 'INITIATED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'


class Market(DjangoEnum):
    NIFTY = 'NIFTY'
    BANKNIFTY = 'BANKNIFTY'


class Direction(DjangoEnum):
    UP = 'UP'
    DOWN = 'DOWN'
