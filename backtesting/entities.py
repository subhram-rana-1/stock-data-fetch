import json
from typing import List
from datetime import date, time

from backtesting.enums import Market
from backtesting.models import Trade, Backtesting, DailyBacktesting


class EntryCondition:
    def __init__(
            self,
            max_variance: float,
            min_abs_trend_slope: float,
            min_abs_price_slope: float,
            min_abs_price_momentum: float,
    ):
        self.max_variance = max_variance
        self.min_abs_trend_slope = min_abs_trend_slope
        self.min_abs_price_slope = min_abs_price_slope
        self.min_abs_price_momentum = min_abs_price_momentum

    def to_dict(self) -> dict:
        return {
            'max_variance': self.max_variance,
            'min_abs_trend_slope': self.min_abs_trend_slope,
            'min_abs_price_slope': self.min_abs_price_slope,
            'min_abs_price_momentum': self.min_abs_price_momentum,
        }

    @classmethod
    def from_dict(cls, my_dict: dict):
        return EntryCondition(
            my_dict['max_variance'],
            my_dict['min_abs_trend_slope'],
            my_dict['min_abs_price_slope'],
            my_dict['min_abs_price_momentum'],
        )


class TradeConfig:
    def __init__(
            self,
            trend_line_time_period_in_sec: int,
            entry_conditions: List[EntryCondition],
    ):
        self.trend_line_time_period_in_sec = trend_line_time_period_in_sec
        self.entry_conditions = entry_conditions

    def to_dict(self):
        return {
            'trend_line_time_period_in_sec': self.trend_line_time_period_in_sec,
            'entry_conditions': [
                entry_condition.to_dict()
                for entry_condition in self.entry_conditions
            ]
        }

    @classmethod
    def from_dict(cls, my_dict: dict):
        return TradeConfig(
            my_dict['trend_line_time_period_in_sec'],
            [EntryCondition.from_dict(entry_condition)
             for entry_condition in my_dict['entry_conditions']],
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_string(meta: str):
        return TradeConfig.from_dict(json.loads(meta))


class BacktestingInput:
    def __init__(
            self,
            market: Market,
            start_date: date,
            start_time: time,
            end_date: date,
            end_time: time,
            trade_config: TradeConfig,
    ):
        self.market = market
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time
        self.trade_config = trade_config


class DailyBacktestingResult:
    def __init__(
            self,
            daily_back_testing: DailyBacktesting,
            trades: List[Trade],
    ):
        self.daily_back_testing = daily_back_testing
        self.trades = trades

    def save_to_db(self):
        self.daily_back_testing.save()
        for trade in self.trades:
            trade.save()


class BacktestingResult:
    def __init__(
            self,
            back_testing: Backtesting,
            daily_back_testings: List[DailyBacktestingResult],
    ):
        self.back_testing = back_testing
        self.daily_back_testings = daily_back_testings

    def save_to_db(self):
        self.back_testing.mark_completed()
        for daily_back_testing in self.daily_back_testings:
            daily_back_testing.save_to_db()
