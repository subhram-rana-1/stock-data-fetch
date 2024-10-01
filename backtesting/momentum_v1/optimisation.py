from backtesting.entities import BacktestingResult
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
            strategy=,
            purpose=,
            optimised_trade_count=,
            optimised_winning_trade_count=,
            optimised_loosing_trade_count=,
            optimised_success_rate=,
            optimised_chart_config=,
            optimised_trade_config=,
        )
    )

    global_success_rate = 0

def main():
    optimisation_result = compute_optimisation_result()
    optimisation_result.save_to_db()
