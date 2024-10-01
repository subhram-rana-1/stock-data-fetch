import copy
import threading
from backtesting.entities import BacktestingResult, BacktestingInput, ChartConfig, TradeConfig, ExitCondition, \
    EntryCondition
from backtesting.enums import BacktestingStrategy, Market
from backtesting.models import Optimisation
from datetime import date, time
from backtesting.momentum_v1 import core
from typing import List
import time as tm


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
LOCK_ON_OPTIMISATION_RESULT = threading.Lock
OPTIMISATION_RESULT: OptimisationResult = None
LOCK_ON_WAIT_GROUP = threading.Lock
WAIT_GROUP = 0
# ---------------------------------


def increase_wait_group(delta: int):
    global WAIT_GROUP, LOCK_ON_OPTIMISATION_RESULT

    with LOCK_ON_OPTIMISATION_RESULT:
        WAIT_GROUP += delta


def decrease_wait_group(delta: int):
    global WAIT_GROUP, LOCK_ON_OPTIMISATION_RESULT

    with LOCK_ON_OPTIMISATION_RESULT:
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
    trend_line_count = 3
    input_params = [  # todo: add all possible param ranges
        InputParam(
            'chart_config_smooth_price_averaging_method',
            ['simple', 'exponential'],
        ),
        InputParam(
            'chart_config_smooth_price_period',
            [],
        ),
        InputParam(
            'chart_config_smooth_price_ema_period',
            [],
        ),
        InputParam(
            'chart_config_smooth_slope_averaging_method',
            ['simple', 'exponential'],
        ),
        InputParam(
            'chart_config_smooth_slope_period',
            [],
        ),
        InputParam(
            'chart_config_smooth_slope_ema_period',
            [],
        ),

        # --------------------- line slope configs ----------------------
        # IMPORTANT - keep the relative order of following "entry_condition"
        # related configs as it is
        InputParam(
            'entry_condition_max_variance',
            [],
        ),
        InputParam(
            'entry_condition_min_abs_trend_slope',
            [],
        ),
        InputParam(
            'entry_condition_min_abs_price_slope',
            [],
        ),
        InputParam(
            'entry_condition_min_abs_price_momentum',
            [],
        ),
        # ---------------------------------------------------------------

        InputParam(
            'trade_config_exit_condition_profit_target_type',
            [],
        ),
        InputParam(
            'trade_config_exit_condition_profit_target_points',
            [],
        ),
        InputParam(
            'trade_config_exit_condition_stoploss_type',
            [],
        ),
        InputParam(
            'trade_config_exit_condition_stoploss_points',
            [],
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
    global OPTIMISATION_RESULT

    with LOCK_ON_OPTIMISATION_RESULT:
        if optimisation_result.optimisation.optimised_success_rate is None:
            raise Exception('code bug: '
                            'optimisation_result.optimisation.optimised_success_rate is None')

        if OPTIMISATION_RESULT is None:
            OPTIMISATION_RESULT = copy.deepcopy(optimisation_result)
        elif OPTIMISATION_RESULT.optimisation.optimised_success_rate < \
                optimisation_result.optimisation.optimised_success_rate:
            OPTIMISATION_RESULT.optimisation.optimised_success_rate = \
                optimisation_result.optimisation.optimised_success_rate


def perform_backtesting_and_optimise_result(
    optimisation_task_input: OptimisationTaskInput,
    back_test_input: BacktestingInput,
    optimised_result: OptimisationResult,
):
    for date_time_range in optimisation_task_input.date_time_ranges:
        back_test_input.start_date = date_time_range.start_date
        back_test_input.start_time = date_time_range.start_time
        back_test_input.end_date = date_time_range.end_date
        back_test_input.end_time = date_time_range.end_time

        backtest_result = core.get_backtest_result(back_test_input)

        optimised_result.add_back_testing_result(backtest_result)
        optimised_result.optimisation.optimised_trade_count += \
            backtest_result.back_testing.trade_count
        optimised_result.optimisation.optimised_winning_trade_count += \
            backtest_result.back_testing.winning_trade_count
        optimised_result.optimisation.optimised_loosing_trade_count += \
            backtest_result.back_testing.loosing_trade_count

    optimised_result.calculate_success_rate()
    optimise_result_with_exclusive_lock(optimised_result)

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
    else:
        if trend_line_serial_number > \
                len(back_test_input.trade_config.entry_conditions):
            back_test_input.trade_config.entry_conditions.append(EntryCondition())

        if trend_line_serial_number != len(back_test_input.trade_config.entry_conditions):
            raise Exception('code bug: '
                            'trend_line_serial_number != len(back_test_input.trade_config.entry_conditions)')

        if key == 'entry_condition_max_variance':
            back_test_input.trade_config.entry_conditions[-1].max_variance = val
        elif key == 'entry_condition_min_abs_trend_slope':
            back_test_input.trade_config.entry_conditions[-1].min_abs_trend_slope = val
        elif key == 'entry_condition_min_abs_price_slope':
            back_test_input.trade_config.entry_conditions[-1].min_abs_price_slope = val
        elif key == 'entry_condition_min_abs_price_momentum':
            back_test_input.trade_config.entry_conditions[-1].min_abs_price_momentum = val

    return back_test_input


def recursive_compute_back_test_result(
        optimisation_task_input: OptimisationTaskInput,
        i: int,
        back_test_input: BacktestingInput,
        optimised_result: OptimisationResult,
        trend_line_serial_number: int = None,
):
    if i == len(optimisation_task_input.input_params):
        async_perform_backtesting_and_optimise_result(
            optimisation_task_input,
            copy.deepcopy(back_test_input),  # important
            copy.deepcopy(optimised_result),  # important
        )

        return

    key = optimisation_task_input.input_params[i].key
    if not OptimisationTaskInput.is_key_an_entry_condition_key(key):
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
        elif OptimisationTaskInput.is_first_key_for_entry_condition(key):
            if trend_line_serial_number is None:
                trend_line_serial_number = 1

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

    back_test_input = BacktestingInput(
        chart_config=ChartConfig(),
        trade_config=TradeConfig(
            entry_conditions=[],
            exit_condition=ExitCondition(),
        ),
    )

    recursive_compute_back_test_result(
        OptimisationTaskInput(),
        0,
        back_test_input,
        optimised_result,
    )

    while WAIT_GROUP != 0:
        print('still processing ...')
        tm.sleep(3)

    return


def main():
    compute_optimisation_result()

    print(OPTIMISATION_RESULT.get_summary())
    # OPTIMISATION_RESULT.save_to_db()
