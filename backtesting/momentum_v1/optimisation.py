from backtesting.entities import BacktestingResult
from backtesting.enums import BacktestingStrategy
from backtesting.models import Optimisation
from datetime import date, time
from typing import List


class OptimisationResult:
    def __init__(
            self,
            optimisation: Optimisation,
            backtesting_results: List[BacktestingResult],
    ):
        self.optimisation = optimisation
        self.backtesting_results = backtesting_results

    def save_to_db(self):
        self.optimisation.save()
        for backtesting_result in self.backtesting_results:
            backtesting_result.save_to_db()

    def append_backtesting_result(self, backtesting_result: BacktestingResult):
        # todo: take lock
        self.backtesting_results.append(backtesting_result)


class DateTimeRange:
    def __init__(
            self,
            start_date: date,
            end_date: date,
            start_time: time,
            end_time: time,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time


def compute_optimisation_result() -> OptimisationResult:
    optimised_result = OptimisationResult(
        optimisation=Optimisation(
            strategy=BacktestingStrategy.MOMENTUM_V1.name,
            purpose="code check 1",
            optimised_trade_count=0,
            optimised_winning_trade_count=0,
            optimised_loosing_trade_count=0,
            optimised_success_rate=None,
            optimised_chart_config=None,
            optimised_trade_config=None,
        ),
        backtesting_results=[],
    )

    global_success_rate = 0
    # todo


def main():
    print('opt run')
    # optimisation_result = compute_optimisation_result()
    # optimisation_result.save_to_db()
