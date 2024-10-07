import copy
import os
import threading
import traceback

from backtesting.entities import BacktestingResult, BacktestingInput, ChartConfig, TradeConfig, ExitCondition, \
    EntryCondition
from backtesting.enums import BacktestingStrategy, Market
from backtesting.models import Optimisation
from datetime import date, time
from backtesting.momentum_v1 import core
from typing import List
import time as tm
import numpy as np
import signal

from price_app.handlers import fetch_price_data


class OptimisationResult:
    def __init__(
            self,
            optimisation: Optimisation,
            backtesting_results: List[BacktestingResult],
    ):
        self.optimisation = optimisation
        self.backtesting_results = backtesting_results

    def calculate_success_rate(self):
        self.optimisation.calculate_success_rate()
        # print(f'new success rate: {self.optimisation.optimised_success_rate}')

    def add_back_testing_result(self, backtest_result: BacktestingResult):
        self.backtesting_results.append(backtest_result)

    def get_summary(self) -> dict:
        return {
            'trade_count': self.optimisation.optimised_trade_count,
            'winning_trade_count': self.optimisation.optimised_winning_trade_count,
            'loosing_trade_count': self.optimisation.optimised_loosing_trade_count,
            'success_rate': self.optimisation.optimised_success_rate,
            'chart_config': ChartConfig.from_string(
                self.optimisation.optimised_chart_config,
            ).to_dict(),
            'trade_config': TradeConfig.from_string(
                self.optimisation.optimised_trade_config,
            ).to_dict(),
        }

    def save_to_db(self):
        self.optimisation.save()
        for backtesting_result in self.backtesting_results:
            backtesting_result.save_to_db()


# --------- constants -------------
LOCK_ON_OPTIMISATION_RESULT = threading.Lock()
OPTIMISATION_RESULT: OptimisationResult = None
LOCK_ON_WAIT_GROUP = threading.Lock()
WAIT_GROUP = 0
cnt = 1
rec_cnt = 1
STOP_THREADS = False
THREADS = []
# ---------------------------------


def terminate_signal_handler(sig, frame):
    global STOP_THREADS
    STOP_THREADS = True


signal.signal(signal.SIGINT, terminate_signal_handler)


def increase_wait_group(delta: int):
    global WAIT_GROUP

    with LOCK_ON_WAIT_GROUP:
        WAIT_GROUP += delta


def decrease_wait_group(delta: int):
    global WAIT_GROUP

    with LOCK_ON_WAIT_GROUP:
        WAIT_GROUP -= delta


class DateTimeRange:
    def __init__(
            self,
            start_date: date,
            start_time: time,
            end_date: date,
            end_time: time,
            trading_start_time: time,
    ):
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time
        self.trading_start_time = trading_start_time


class InputParam:
    def __init__(self, key, values):
        self.key = key
        self.values = values


class OptimisationTaskInput:
    market = Market.NIFTY
    date_time_ranges = [
        DateTimeRange(
            date(2024, 10, 1),
            time(9, 15),
            date(2024, 10, 1),
            time(15, 30),
            time(9, 20),
        ),
    ]
    trend_line_count = 1
    input_params = [  # todo: add all possible param ranges
        InputParam(
            'chart_config_smooth_price_averaging_method',
            ['simple'],
        ),
        InputParam(
            'chart_config_smooth_price_period',
            [20],
        ),
        InputParam(
            'chart_config_smooth_price_ema_period',
            [100],
        ),
        InputParam(
            'chart_config_smooth_slope_averaging_method',
            ['exponential'],
        ),
        InputParam(
            'chart_config_smooth_slope_period',
            [10],
        ),
        InputParam(
            'chart_config_smooth_slope_ema_period',
            [10],
        ),
        InputParam(
            'trend_line_time_period_in_sec',
            [150],
        ),

        # # --------------------- line slope configs ----------------------
        # # IMPORTANT - keep the relative order of following "entry_condition"
        # # related configs as it is
        InputParam(
            'entry_condition_max_variance',
            [1.1, 5],
        ),
        InputParam(
            'entry_condition_min_abs_trend_slope',
            [0.25, 0.064],
        ),
        InputParam(
            'entry_condition_min_abs_price_slope',
            [1.8, 0.4],
        ),
        InputParam(
            'entry_condition_min_abs_price_momentum',
            [0.28, 0.15],
        ),
        # # ---------------------------------------------------------------

        InputParam(
            'trade_config_exit_condition_profit_target_type',
            ['fixed'],
        ),
        InputParam(
            'trade_config_exit_condition_profit_target_points',
            [10],
        ),
        InputParam(
            'trade_config_exit_condition_stoploss_type',
            ['fixed'],
        ),
        InputParam(
            'trade_config_exit_condition_stoploss_points',
            [5],
        ),
    ]

    def get_first_entry_condition_key_index(self) -> int:
        for i in range(len(self.input_params)):
            if self.input_params[i].key == 'entry_condition_max_variance':
                return i

        raise Exception('entry_condition_max_variance key not found in '
                        'OptimisationTaskInput.input_params')

    @staticmethod
    def is_first_key_for_entry_condition(key: str) -> bool:
        return key == 'entry_condition_max_variance'

    @staticmethod
    def is_last_key_for_entry_condition(key: str) -> bool:
        return key == 'entry_condition_min_abs_price_momentum'

    @staticmethod
    def is_key_an_entry_condition_key(key: str) -> bool:
        return key in [
            'entry_condition_max_variance',
            'entry_condition_min_abs_trend_slope',
            'entry_condition_min_abs_price_slope',
            'entry_condition_min_abs_price_momentum',
        ]


def optimise_result_with_exclusive_lock(optimisation_result: OptimisationResult):
    global OPTIMISATION_RESULT, cnt

    # print(f'{cnt} optimise_result_with_exclusive_lock(): '
    #       f'{optimisation_result.optimisation.optimised_success_rate}')
    # cnt += 1

    with LOCK_ON_OPTIMISATION_RESULT:
        if optimisation_result.optimisation.optimised_success_rate is None:
            raise Exception('code bug: '
                            'optimisation_result.optimisation.optimised_success_rate is None')

        if OPTIMISATION_RESULT is None:
            OPTIMISATION_RESULT = copy.deepcopy(optimisation_result)
            print(f'assigning for first time: '
                  f'{OPTIMISATION_RESULT.optimisation.optimised_success_rate}')
        elif OPTIMISATION_RESULT.optimisation.optimised_success_rate < \
                optimisation_result.optimisation.optimised_success_rate:
            OPTIMISATION_RESULT = copy.deepcopy(optimisation_result)

            print(f'optimised: OPTIMISATION_RESULT: '
                  f'{OPTIMISATION_RESULT.optimisation.optimised_success_rate}')


def perform_backtesting_and_optimise_result(
    optimisation_task_input: OptimisationTaskInput,
    back_test_input: BacktestingInput,
    optimised_result: OptimisationResult,
):
    try:
        for date_time_range in optimisation_task_input.date_time_ranges:
            back_test_input.start_date = date_time_range.start_date
            back_test_input.start_time = date_time_range.start_time
            back_test_input.end_date = date_time_range.end_date
            back_test_input.end_time = date_time_range.end_time
            back_test_input.trade_config.min_entry_time = date_time_range.trading_start_time

            backtest_result = core.get_backtest_result(back_test_input)
            print(f'success_rate--> {backtest_result.back_testing.success_rate}')
            optimised_result.add_back_testing_result(backtest_result)

        optimised_result.calculate_success_rate()
        optimise_result_with_exclusive_lock(optimised_result)
    except Exception as e:
        print(f'Exception: perform_backtesting_and_optimise_result: {e}')
        print(traceback.format_exc())
        os.kill(os.getpid(), signal.SIGINT)
    finally:
        decrease_wait_group(1)


def async_perform_backtesting_and_optimise_result(
        optimisation_task_input: OptimisationTaskInput,
        back_test_input: BacktestingInput,
        optimised_result: OptimisationResult,
):
    increase_wait_group(1)

    thread = threading.Thread(
        target=perform_backtesting_and_optimise_result,
        args=(optimisation_task_input, back_test_input, optimised_result),
    )
    thread.start()

    global THREADS
    THREADS.append(thread)


def set_backtest_input_param(
        optimisation_task_input: OptimisationTaskInput,
        back_test_input: BacktestingInput,
        key: str,
        val: object,
        trend_line_serial_number: int = None,
) -> BacktestingInput:
    if not optimisation_task_input.is_key_an_entry_condition_key(key):
        if key == 'chart_config_smooth_price_averaging_method':
            back_test_input.chart_config.smooth_slope_averaging_method = val
        elif key == 'chart_config_smooth_price_period':
            back_test_input.chart_config.smooth_price_period = val
        elif key == 'chart_config_smooth_price_ema_period':
            back_test_input.chart_config.smooth_price_ema_period = val
        elif key == 'chart_config_smooth_slope_averaging_method':
            back_test_input.chart_config.smooth_price_averaging_method = val
        elif key == 'chart_config_smooth_slope_period':
            back_test_input.chart_config.smooth_slope_period = val
        elif key == 'chart_config_smooth_slope_ema_period':
            back_test_input.chart_config.smooth_slope_ema_period = val
        elif key == 'trade_config_exit_condition_profit_target_type':
            back_test_input.trade_config.exit_condition.profit_target_type = val
        elif key == 'trade_config_exit_condition_profit_target_points':
            back_test_input.trade_config.exit_condition.profit_target_points = val
        elif key == 'trade_config_exit_condition_stoploss_type':
            back_test_input.trade_config.exit_condition.stoploss_type = val
        elif key == 'trade_config_exit_condition_stoploss_points':
            back_test_input.trade_config.exit_condition.stoploss_points = val
        elif key == 'trend_line_time_period_in_sec':
            back_test_input.trade_config.trend_line_time_period_in_sec = val
    else:
        if key == 'entry_condition_max_variance':
            back_test_input.trade_config.entry_conditions[trend_line_serial_number-1].max_variance = val
        elif key == 'entry_condition_min_abs_trend_slope':
            back_test_input.trade_config.entry_conditions[trend_line_serial_number-1].min_abs_trend_slope = val
        elif key == 'entry_condition_min_abs_price_slope':
            back_test_input.trade_config.entry_conditions[trend_line_serial_number-1].min_abs_price_slope = val
        elif key == 'entry_condition_min_abs_price_momentum':
            back_test_input.trade_config.entry_conditions[trend_line_serial_number-1].min_abs_price_momentum = val

    return back_test_input


def recursive_compute_back_test_result(
        optimisation_task_input: OptimisationTaskInput,
        i: int,
        back_test_input: BacktestingInput,
        optimised_result: OptimisationResult,
        trend_line_serial_number: int = None,
):
    if STOP_THREADS:
        return

    if i == len(optimisation_task_input.input_params):
        # global rec_cnt
        # print(f'{rec_cnt} recursion')
        # rec_cnt += 1

        async_perform_backtesting_and_optimise_result(
            optimisation_task_input,
            copy.deepcopy(back_test_input),  # important
            copy.deepcopy(optimised_result),  # important
        )

        return

    key = optimisation_task_input.input_params[i].key
    if not OptimisationTaskInput.is_key_an_entry_condition_key(key):
        # print(f'non entry --> {key}')
        for val in optimisation_task_input.input_params[i].values:
            back_test_input = set_backtest_input_param(
                optimisation_task_input,
                back_test_input,
                key,
                val,
            )

            recursive_compute_back_test_result(
                optimisation_task_input,
                i+1,
                back_test_input,
                optimised_result,
            )
    else:
        if OptimisationTaskInput.is_last_key_for_entry_condition(key):
            # print(f'entry --> {key}, {trend_line_serial_number}')
            for val in optimisation_task_input.input_params[i].values:
                back_test_input = set_backtest_input_param(
                    optimisation_task_input,
                    back_test_input,
                    key,
                    val,
                    trend_line_serial_number,
                )

                if trend_line_serial_number < optimisation_task_input.trend_line_count:
                    recursive_compute_back_test_result(
                        optimisation_task_input,
                        optimisation_task_input.get_first_entry_condition_key_index(),
                        back_test_input,
                        optimised_result,
                        trend_line_serial_number + 1,
                    )
                else:
                    recursive_compute_back_test_result(
                        optimisation_task_input,
                        i+1,
                        back_test_input,
                        optimised_result,
                    )
        else:
            if OptimisationTaskInput.is_first_key_for_entry_condition(key):
                if trend_line_serial_number is None:
                    trend_line_serial_number = 1

            # print(f'entry --> {key}, {trend_line_serial_number}')

            for val in optimisation_task_input.input_params[i].values:
                back_test_input = set_backtest_input_param(
                    optimisation_task_input,
                    back_test_input,
                    key,
                    val,
                    trend_line_serial_number,
                )

                recursive_compute_back_test_result(
                    optimisation_task_input,
                    i+1,
                    back_test_input,
                    optimised_result,
                    trend_line_serial_number,
                )


def preload_price_dat_from_database_to_cache(optimisation_task_input: OptimisationTaskInput):
    for date_time in optimisation_task_input.date_time_ranges:
        _ = fetch_price_data(
            market_type=Market.to_price_app_market_type(optimisation_task_input.market),
            from_date=date_time.start_date,
            to_date=date_time.end_date,
            from_time=date_time.start_time,
            to_time=date_time.end_time,
            smooth_price_averaging_method='simple',
            smooth_price_period=20,
            smooth_price_ema_period=100,
            smooth_slope_averaging_method='exponential',
            smooth_slope_period=10,
            smooth_slope_ema_period=10,
        )


def compute_optimisation_result():
    optimised_result = OptimisationResult(
        optimisation=Optimisation(
            strategy=BacktestingStrategy.MOMENTUM_V1.name,
            purpose="code check 1",
            optimised_trade_count=0,
            optimised_winning_trade_count=0,
            optimised_loosing_trade_count=0,
            optimised_success_rate=0,
            optimised_chart_config=None,
            optimised_trade_config=None,
        ),
        backtesting_results=[],
    )

    optimisation_task_input = OptimisationTaskInput()

    # preload_price_dat_from_database_to_cache(optimisation_task_input)

    back_test_input = BacktestingInput(
        market=Market.NIFTY,
        chart_config=ChartConfig(),
        trade_config=TradeConfig(
            entry_conditions=[EntryCondition()
                              for i in range(optimisation_task_input.trend_line_count)],
            exit_condition=ExitCondition(),
        ),
    )

    # thread = threading.Thread(target=show_optimised_success_rate)
    # thread.start()

    recursive_compute_back_test_result(
        optimisation_task_input,
        0,
        back_test_input,
        optimised_result,
    )

    for thread in THREADS:
        thread.join()

    return


def show_optimised_success_rate():
    for i in range(100):
        if OPTIMISATION_RESULT is not None:
            print('OPTIMISATION_RESULT.optimisation.optimised_success_rate: ',
                  OPTIMISATION_RESULT.optimisation.optimised_success_rate)
        tm.sleep(1)


def main():
    compute_optimisation_result()

    print(OPTIMISATION_RESULT.get_summary())
    # OPTIMISATION_RESULT.save_to_db()
