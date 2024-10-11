import os.path
from datetime import date, time, timedelta, datetime
from backtesting.entities import BacktestingInput, ChartConfig, \
    TradeConfig, ExitCondition, EntryCondition, BacktestingResult
from backtesting.enums import Market
from typing import List
from skopt import gp_minimize
import numpy as np

from backtesting.momentum_1min_candle.utils import get_optimised_param_dict, write_to_json_file
from backtesting.momentum_1min_candle import core
from price_app.handlers import fetch_price_from_database


market_start_time = time(9, 15)
market_end_time = time(15, 30)


def get_nums(start, end, interval) -> List:
    # int
    if isinstance(start, int) and isinstance(end, int) and isinstance(interval, int):
        return [x for x in range(start, end + 1, interval)]

    # float
    return list(np.arange(start, end + interval, interval))


class FixedInputs:
    """ We can change this manually and run optimisation
    and can observe which fixed input combination give
    the best result"""

    market = Market.NIFTY
    start_date = date(2024, 8, 1)
    start_time = time(9, 15, 0)
    end_date = date(2024, 8, 30)
    end_time = time(15, 30, 0)
    min_entry_time = time(9, 20)

    smooth_price_averaging_method = 'simple'
    smooth_slope_averaging_method = 'simple'
    profit_target_type = 'fixed'
    profit_target_points = 20
    stoploss_type = 'fixed'
    stoploss_points = 13


class FixedInputsForTestDataset:
    """ We can change this manually and run optimisation
    and can observe which fixed input combination give
    the best result"""

    market = Market.NIFTY
    start_date = date(2024, 9, 1)
    start_time = time(9, 15, 0)
    end_date = date(2024, 9, 30)
    end_time = time(15, 30, 0)


total_param_count = 21
search_range_chat_config_smooth_price_periods = get_nums(5, 30, 3)
search_range_chat_config_smooth_price_ema_periods = get_nums(20, 200, 15)
search_range_chat_config_smooth_slope_periods = get_nums(5, 50, 5)
search_range_chat_config_smooth_slope_ema_periods = get_nums(5, 50, 5)
search_range_trade_config_trend_line_time_periods_in_sec = get_nums(60, 360, 20)
search_range_trade_config_entry_condition_1_max_variance = get_nums(0.5, 10, 0.5)
search_range_trade_config_entry_condition_1_min_abs_trend_slope = get_nums(0, 0.6, 0.025)
search_range_trade_config_entry_condition_1_min_abs_price_slope = get_nums(0.1, 30, 0.1)
search_range_trade_config_entry_condition_1_min_abs_price_momentum = get_nums(0.01, 10, 0.02)
search_range_trade_config_entry_condition_2_max_variance = get_nums(0.5, 10, 0.5)
search_range_trade_config_entry_condition_2_min_abs_trend_slope = get_nums(0, 0.6, 0.025)
search_range_trade_config_entry_condition_2_min_abs_price_slope = get_nums(0.1, 30, 0.1)
search_range_trade_config_entry_condition_2_min_abs_price_momentum = get_nums(0.01, 10, 0.02)
search_range_trade_config_entry_condition_3_max_variance = get_nums(0.5, 10, 0.5)
search_range_trade_config_entry_condition_3_min_abs_trend_slope = get_nums(0, 0.6, 0.025)
search_range_trade_config_entry_condition_3_min_abs_price_slope = get_nums(0.1, 30, 0.1)
search_range_trade_config_entry_condition_3_min_abs_price_momentum = get_nums(0.01, 10, 0.02)
search_range_trade_config_entry_condition_4_max_variance = get_nums(0.5, 10, 0.5)
search_range_trade_config_entry_condition_4_min_abs_trend_slope = get_nums(0, 0.6, 0.025)
search_range_trade_config_entry_condition_4_min_abs_price_slope = get_nums(0.1, 30, 0.1)
search_range_trade_config_entry_condition_4_min_abs_price_momentum = get_nums(0.01, 10, 0.02)


def calculate_cost(
        back_test_input: BacktestingInput,
        backtest_result: BacktestingResult,
) -> float:
    # max_cost = 10000000
    #
    # i = 0
    # entry_condition_cnt = len(back_test_input.trade_config.entry_conditions)
    # while i < entry_condition_cnt - 1:
    #     entry_condition = back_test_input.trade_config.entry_conditions[i]
    #     next_entry_condition = back_test_input.trade_config.entry_conditions[i+1]
    #
    #     if entry_condition.max_variance >= next_entry_condition.max_variance:
    #         return max_cost
    #
    #     if entry_condition.min_abs_trend_slope <= next_entry_condition.min_abs_trend_slope:
    #         return max_cost
    #
    #     if entry_condition.min_abs_price_slope >= next_entry_condition.min_abs_price_slope:
    #         return max_cost
    #
    #     if entry_condition.min_abs_price_momentum >= next_entry_condition.min_abs_price_momentum:
    #         return max_cost

    net_point_gain = 0
    for daily_back_testing_result in backtest_result.daily_back_testing_results:
        for trade in daily_back_testing_result.trades:
            net_point_gain += trade.gain

    return -1 * net_point_gain


def cost_function(params) -> float:
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

    return calculate_cost(back_test_input, backtest_result)


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


def run_algo_on_test_data(optimised_params_json_file_path: str):
    back_test_input = BacktestingInput.from_json_file(
        market=FixedInputsForTestDataset.market,
        start_date=FixedInputsForTestDataset.start_date,
        start_time=FixedInputsForTestDataset.start_time,
        end_date=FixedInputsForTestDataset.end_date,
        end_time=FixedInputsForTestDataset.end_time,
        json_abs_file_path=os.path.abspath(optimised_params_json_file_path),
    )

    backtest_result: BacktestingResult = core.get_backtest_result(back_test_input)

    backtest_result.save_to_db()
