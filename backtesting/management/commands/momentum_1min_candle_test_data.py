from django.core.management.base import BaseCommand
from backtesting.momentum_1min_candle.optimisation.common import run_algo_on_test_data

from backtesting.momentum_1min_candle.optimisation.bayesian_optimisation import \
    optimised_params_json_file_path as optimised_params_json_file_path_bayesian
from backtesting.momentum_1min_candle.optimisation.differential_evolution import \
    optimised_params_json_file_path as optimised_params_json_file_path_differential_evolution
from backtesting.momentum_1min_candle.optimisation.genetic_algorithm import \
    optimised_params_json_file_path as optimised_params_json_file_path_genetic_algorithm


file_path = optimised_params_json_file_path_genetic_algorithm


class Command(BaseCommand):
    def handle(self, *args, **options):
        run_algo_on_test_data(file_path)
