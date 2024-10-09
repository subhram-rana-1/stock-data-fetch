from datetime import date, time, timedelta, datetime
from backtesting.entities import BacktestingInput, ChartConfig, \
    TradeConfig, ExitCondition, EntryCondition, BacktestingResult
from backtesting.enums import Market
from typing import List
from skopt import gp_minimize
import numpy as np
from skopt.space import Categorical

from backtesting.momentum_1min_candle.utils import get_optimised_param_dict, write_to_json_file
from backtesting.momentum_v1 import core
from price_app.handlers import fetch_price_from_database


market_start_time = time(9, 15)
market_end_time = time(15, 30)


def get_nums(start, end, interval) -> List:
    if isinstance(start, float) or isinstance(end, float) or isinstance(interval, float):
        return list(np.arange(start, end + interval, interval))

    return [x for x in range(start, end + 1, interval)]


class FixedInputs:
    """ We can change this manually and run optimisation
    and can observe which fixed input combination give
    the best result"""

    market = Market.NIFTY
    start_date = date(2024, 9, 24)
    start_time = time(9, 15, 0)
    end_date = date(2024, 9, 24)
    end_time = time(14, 45, 0)
    min_entry_time = time(9, 20)

    smooth_price_averaging_method = 'simple'
    smooth_slope_averaging_method = 'simple'
    profit_target_type = 'fixed'
    profit_target_points = 20
    stoploss_type = 'fixed'
    stoploss_points = 10


search_space = [
    Categorical(get_nums(5, 30, 3), name='chat_config_smooth_price_periods'),
    Categorical(get_nums(20, 200, 15), name='chat_config_smooth_price_ema_periods'),
    Categorical(get_nums(5, 50, 5), name='chat_config_smooth_slope_periods'),
    Categorical(get_nums(5, 50, 5), name='chat_config_smooth_slope_ema_periods'),

    Categorical(get_nums(60, 360, 20), name='trade_config_trend_line_time_periods_in_sec'),

    Categorical(get_nums(0.5, 10, 0.5), name='trade_config_entry_condition_1_max_variance'),
    Categorical(get_nums(0, 0.6, 0.025), name='trade_config_entry_condition_1_min_abs_trend_slope'),
    Categorical(get_nums(0.1, 30, 0.1), name='trade_config_entry_condition_1_min_abs_price_slope'),
    Categorical(get_nums(0.01, 10, 0.02), name='trade_config_entry_condition_1_min_abs_price_momentum'),

    Categorical(get_nums(0.5, 10, 0.5), name='trade_config_entry_condition_2_max_variance'),
    Categorical(get_nums(0, 0.6, 0.025), name='trade_config_entry_condition_2_min_abs_trend_slope'),
    Categorical(get_nums(0.1, 30, 0.1), name='trade_config_entry_condition_2_min_abs_price_slope'),
    Categorical(get_nums(0.01, 10, 0.02), name='trade_config_entry_condition_2_min_abs_price_momentum'),

    Categorical(get_nums(0.5, 10, 0.5), name='trade_config_entry_condition_3_max_variance'),
    Categorical(get_nums(0, 0.6, 0.025), name='trade_config_entry_condition_3_min_abs_trend_slope'),
    Categorical(get_nums(0.1, 30, 0.1), name='trade_config_entry_condition_3_min_abs_price_slope'),
    Categorical(get_nums(0.01, 10, 0.02), name='trade_config_entry_condition_3_min_abs_price_momentum'),

    Categorical(get_nums(0.5, 10, 0.5), name='trade_config_entry_condition_4_max_variance'),
    Categorical(get_nums(0, 0.6, 0.025), name='trade_config_entry_condition_4_min_abs_trend_slope'),
    Categorical(get_nums(0.1, 30, 0.1), name='trade_config_entry_condition_4_min_abs_price_slope'),
    Categorical(get_nums(0.01, 10, 0.02), name='trade_config_entry_condition_4_min_abs_price_momentum'),

    # Categorical(get_nums(5, 10, 1), name='trade_config_exit_conditions_profit_target_points'),
    # Categorical(get_nums(5, 20, 1), name='trade_config_exit_conditions_stoploss_points'),
]


def calculate_cost(backtest_result: BacktestingResult) -> float:
    net_point_gain = 0
    for daily_back_testing_result in backtest_result.daily_back_testing_results:
        for trade in daily_back_testing_result.trades:
            net_point_gain += trade.gain

    return -1 * net_point_gain

    # success_rate = backtest_result.back_testing.success_rate
    # success_rate = success_rate if success_rate is not None else -100
    # normalised_success_rate = success_rate * 100
    # normalised_net_point_gain = net_point_gain
    #
    # weightage_success_rate = 0.6
    # weightage_net_point_gain = 0.4
    #
    # positive_value = (normalised_success_rate * weightage_success_rate) + \
    #                  (normalised_net_point_gain * weightage_net_point_gain)
    #
    # cost = -1 * positive_value
    #
    # return cost


def cost_function(params) -> float:
    # print(f'params: {params}')

    chat_config_smooth_price_period, \
        chat_config_smooth_price_ema_period, \
        chat_config_smooth_slope_period, \
        chat_config_smooth_slope_ema_period, \
        trade_config_trend_line_time_period_in_sec, \
        trade_config_entry_condition_1_max_variance, \
        trade_config_entry_condition_1_min_abs_trend_slope, \
        trade_config_entry_condition_1_min_abs_price_slope, \
        trade_config_entry_condition_1_min_abs_price_momentum, \
        trade_config_entry_condition_2_max_variance, \
        trade_config_entry_condition_2_min_abs_trend_slope, \
        trade_config_entry_condition_2_min_abs_price_slope, \
        trade_config_entry_condition_2_min_abs_price_momentum, \
        trade_config_entry_condition_3_max_variance, \
        trade_config_entry_condition_3_min_abs_trend_slope, \
        trade_config_entry_condition_3_min_abs_price_slope, \
        trade_config_entry_condition_3_min_abs_price_momentum, \
        trade_config_entry_condition_4_max_variance, \
        trade_config_entry_condition_4_min_abs_trend_slope, \
        trade_config_entry_condition_4_min_abs_price_slope, \
        trade_config_entry_condition_4_min_abs_price_momentum = params
        # trade_config_exit_conditions_profit_target_points, \
        # trade_config_exit_conditions_stoploss_points = params

    back_test_input = BacktestingInput(
        market=FixedInputs.market,
        start_date=FixedInputs.start_date,
        start_time=FixedInputs.start_time,
        end_date=FixedInputs.end_date,
        end_time=FixedInputs.end_time,
        chart_config=ChartConfig(
            smooth_price_averaging_method=FixedInputs.smooth_price_averaging_method,
            smooth_price_period=chat_config_smooth_price_period,
            smooth_price_ema_period=chat_config_smooth_price_ema_period,
            smooth_slope_averaging_method=FixedInputs.smooth_slope_averaging_method,
            smooth_slope_period=chat_config_smooth_slope_period,
            smooth_slope_ema_period=chat_config_smooth_slope_ema_period,
        ),
        trade_config=TradeConfig(
            trend_line_time_period=trade_config_trend_line_time_period_in_sec,
            min_entry_time=FixedInputs.min_entry_time,
            entry_conditions=[
                EntryCondition(
                    max_variance=trade_config_entry_condition_1_max_variance,
                    min_abs_trend_slope=trade_config_entry_condition_1_min_abs_trend_slope,
                    min_abs_price_slope=trade_config_entry_condition_1_min_abs_price_slope,
                    min_abs_price_momentum=trade_config_entry_condition_1_min_abs_price_momentum,
                ),
                EntryCondition(
                    max_variance=trade_config_entry_condition_2_max_variance,
                    min_abs_trend_slope=trade_config_entry_condition_2_min_abs_trend_slope,
                    min_abs_price_slope=trade_config_entry_condition_2_min_abs_price_slope,
                    min_abs_price_momentum=trade_config_entry_condition_2_min_abs_price_momentum,
                ),
                EntryCondition(
                    max_variance=trade_config_entry_condition_3_max_variance,
                    min_abs_trend_slope=trade_config_entry_condition_3_min_abs_trend_slope,
                    min_abs_price_slope=trade_config_entry_condition_3_min_abs_price_slope,
                    min_abs_price_momentum=trade_config_entry_condition_3_min_abs_price_momentum,
                ),
                EntryCondition(
                    max_variance=trade_config_entry_condition_4_max_variance,
                    min_abs_trend_slope=trade_config_entry_condition_4_min_abs_trend_slope,
                    min_abs_price_slope=trade_config_entry_condition_4_min_abs_price_slope,
                    min_abs_price_momentum=trade_config_entry_condition_4_min_abs_price_momentum,
                ),
            ],
            exit_condition=ExitCondition(
                profit_target_type=FixedInputs.profit_target_type,
                profit_target_points=FixedInputs.profit_target_points,
                stoploss_type=FixedInputs.stoploss_type,
                stoploss_points=FixedInputs.stoploss_points,
            )
        )
    )

    backtest_result: BacktestingResult = core.get_backtest_result(back_test_input)

    return calculate_cost(backtest_result)


def preload_cache_for_stock_price():
    day = FixedInputs.start_date
    while day <= FixedInputs.end_date:
        start_time = FixedInputs.start_time if day == FixedInputs.start_date else market_start_time
        end_time = FixedInputs.end_time if day == FixedInputs.end_date else market_end_time

        start_timestamp = datetime.combine(day, start_time) + timedelta(microseconds=0)
        to_timestamp = datetime.combine(day, end_time) + timedelta(microseconds=0)

        _ = fetch_price_from_database(
            FixedInputs.market.to_price_app_market_type(),
            start_timestamp,
            to_timestamp,
        )

        day += timedelta(days=1)


def main():
    preload_cache_for_stock_price()

    res = gp_minimize(cost_function, search_space, n_calls=1)

    optimised_params_dict = get_optimised_param_dict(
        market=FixedInputs.market,
        smooth_price_averaging_method=FixedInputs.smooth_price_averaging_method,
        smooth_slope_averaging_method=FixedInputs.smooth_slope_averaging_method,
        min_entry_time=FixedInputs.min_entry_time,
        profit_target_type=FixedInputs.profit_target_type,
        stoploss_type=FixedInputs.stoploss_type,
        params=res.x.tolist(),
    )
    write_to_json_file(optimised_params_dict)
