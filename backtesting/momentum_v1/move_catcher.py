from datetime import time, datetime, timedelta
from abc import ABC, abstractmethod
from typing import List
from backtesting.entities import TradeConfig, LinearRegressionLine
from backtesting.enums import Direction
from backtesting.models import Trade
from backtesting.utils import get_linear_regression_result
from price_app.classes import PriceDataPerTick


class Trendline(LinearRegressionLine):
    def __init__(self, m: float, c: float, variance: float):
        super().__init__(m, c, variance)

    @classmethod
    def from_linear_regression_line(cls, linear_regression_line: LinearRegressionLine):
        return Trendline(
            linear_regression_line.m,
            linear_regression_line.c,
            linear_regression_line.variance,
        )


class IMoveCatcher(ABC):
    exit_reason_stoploss_hit = 'sl_hit'
    exit_reason_target_hit = 'target_hit'

    @abstractmethod
    def should_make_entry(self, price_list: List[PriceDataPerTick], i: int, trade_config: TradeConfig) \
            -> (bool, str):
        ...

    @abstractmethod
    def should_exit(self, trade: Trade, price_list: List[PriceDataPerTick], i: int, trade_config: TradeConfig) \
            -> (bool, str):
        ...

    @abstractmethod
    def is_winning_trade(self, price_list: List[PriceDataPerTick], entry_idx: int, exit_idx: int,
                         trade_config: TradeConfig) -> bool:
        ...

    @abstractmethod
    def calculate_gain(self, trade: Trade) -> Trade:
        ...

    def _get_index_for_start_time(self, price_list: List[PriceDataPerTick], i: int, start_time: time) -> int:
        lo = 0
        hi = i
        while lo != hi:
            mid: int = lo+int((hi-lo)/2)
            if price_list[mid]['tm'] >= start_time:
                hi = mid
            else:
                lo = mid + 1

        return lo

    def calculate_trend_line(self, price_list: List[PriceDataPerTick], i: int, trade_config: TradeConfig) -> Trendline:
        end_time: time = price_list[i]['tm']

        today = datetime.today()
        end_time_as_datetime = datetime.combine(today, end_time)
        start_time_as_datetime = end_time_as_datetime - timedelta(seconds=trade_config.trend_line_time_period_in_sec)
        start_time = start_time_as_datetime.time()

        j = self._get_index_for_start_time(price_list, i, start_time)

        tick_prices = [price['tick_price'] for price in price_list[j:i+1]]
        return Trendline.from_linear_regression_line(get_linear_regression_result(tick_prices))


class UpMoveCatcher(IMoveCatcher):
    def should_make_entry(self, price_list: List[PriceDataPerTick], i: int, trade_config: TradeConfig) -> (bool, str):
        if price_list[i]['tm'] <= trade_config.min_entry_time:
            return False, f"entry not allowed before min entry time {trade_config.min_entry_time}"

        trendline = self.calculate_trend_line(price_list, i, trade_config)
        for entry_condition in trade_config.entry_conditions:
            if trendline.variance <= entry_condition.max_variance and \
                    trendline.m >= entry_condition.min_abs_trend_slope and \
                    price_list[i]['slope'] >= entry_condition.min_abs_price_slope and \
                    price_list[i]['momentum'] >= entry_condition.min_abs_price_momentum:

                reason1 = (f"trendline: variance {trendline.variance} <= {entry_condition.max_variance} "
                           f"slope {trendline.m} >= {entry_condition.min_abs_trend_slope} ")
                reason2 = (f"price chart: slope {price_list[i]['slope']} >= {entry_condition.min_abs_price_slope} "
                           f"momentum {price_list[i]['momentum']} >= {entry_condition.min_abs_price_momentum}")

                return True, ', '.join([reason1, reason2])

        return False, "No entry criteria met"

    def should_exit(self, trade: Trade, price_list: List[PriceDataPerTick], i: int, trade_config: TradeConfig) \
            -> (bool, str):
        # 1. check stoploss trigger
        if trade_config.exit_condition.stoploss_type == 'fixed':
            cur_tick_price = price_list[i]['tick_price']
            lower_boundary_price = trade.entry_point - trade_config.exit_condition.stoploss_points
            if cur_tick_price <= lower_boundary_price:
                return True, self.exit_reason_stoploss_hit
        else:
            raise Exception(f'exit condition type {trade_config.exit_condition.stoploss_type} '
                            f'is not valid for making an exit')

        # 2. check target hit
        if trade_config.exit_condition.profit_target_type == 'fixed':
            cur_tick_price = price_list[i]['tick_price']
            upper_boundary_price = trade.entry_point + trade_config.exit_condition.profit_target_points
            if cur_tick_price >= upper_boundary_price:
                return True, self.exit_reason_target_hit
        else:
            raise Exception(f'exit condition type {trade_config.exit_condition.stoploss_type} '
                            f'is not valid for making an exit')

        return False, "no exit condition met"

    def is_winning_trade(self, price_list: List[PriceDataPerTick], entry_idx: int, exit_idx: int,
                         trade_config: TradeConfig) -> bool:
        return price_list[exit_idx]['tick_price'] - price_list[entry_idx]['tick_price'] >= \
            trade_config.exit_condition.profit_target_points

    def calculate_gain(self, trade: Trade) -> Trade:
        return trade.exit_point - trade.entry_point


class DownMoveCatcher(IMoveCatcher):
    def should_make_entry(self, price_list: List[PriceDataPerTick], i: int, trade_config: TradeConfig) -> (bool, str):
        if price_list[i]['tm'] <= trade_config.min_entry_time:
            return False, f"entry not allowed before min entry time {trade_config.min_entry_time}"

        trendline = self.calculate_trend_line(price_list, i, trade_config)
        for entry_condition in trade_config.entry_conditions:
            if trendline.variance <= entry_condition.max_variance and \
                    trendline.m <= -1*entry_condition.min_abs_trend_slope and \
                    price_list[i]['slope'] <= -1*entry_condition.min_abs_price_slope and \
                    price_list[i]['momentum'] <= -1*entry_condition.min_abs_price_momentum:
                reason1 = (f"trendline: variance {trendline.variance} <= {entry_condition.max_variance} "
                           f"slope {trendline.m} <= {-1*entry_condition.min_abs_trend_slope} ")
                reason2 = (f"price chart: slope {price_list[i]['slope']} <= {-1*entry_condition.min_abs_price_slope} "
                           f"momentum {price_list[i]['momentum']} <= {-1*entry_condition.min_abs_price_momentum}")

                return True, ', '.join([reason1, reason2])

        return False, "No entry criteria met"

    def should_exit(self, trade: Trade, price_list: List[PriceDataPerTick], i: int, trade_config: TradeConfig) \
            -> (bool, str):
        # 1. check stoploss trigger
        if trade_config.exit_condition.stoploss_type == 'fixed':
            cur_tick_price = price_list[i]['tick_price']
            upper_boundary_price = trade.entry_point + trade_config.exit_condition.stoploss_points
            if cur_tick_price >= upper_boundary_price:
                return True, self.exit_reason_stoploss_hit
        else:
            raise Exception(f'exit condition type {trade_config.exit_condition.stoploss_type} '
                            f'is not valid for making an exit')

        # 2. check target hit
        if trade_config.exit_condition.profit_target_type == 'fixed':
            cur_tick_price = price_list[i]['tick_price']
            lower_boundary_price = trade.entry_point - trade_config.exit_condition.profit_target_points
            if cur_tick_price <= lower_boundary_price:
                return True, self.exit_reason_target_hit
        else:
            raise Exception(f'exit condition type {trade_config.exit_condition.stoploss_type} '
                            f'is not valid for making an exit')

        return False, "no exit condition met"

    def is_winning_trade(self, price_list: List[PriceDataPerTick], entry_idx: int, exit_idx: int,
                         trade_config: TradeConfig) -> bool:
        return price_list[entry_idx]['tick_price'] - price_list[exit_idx]['tick_price'] >= \
            trade_config.exit_condition.profit_target_points

    def calculate_gain(self, trade: Trade) -> Trade:
        return trade.entry_point - trade.exit_point


def new_move_catcher(direction: Direction) -> IMoveCatcher:
    if direction == Direction.UP:
        return UpMoveCatcher()
    elif direction == Direction.DOWN:
        return DownMoveCatcher()
    else:
        raise Exception(f'invalid direction: {direction.name} to created move catcher')
