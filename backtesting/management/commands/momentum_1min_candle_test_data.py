from django.core.management.base import BaseCommand
from backtesting.momentum_1min_candle import optimisation_bayesian_scikit


class Command(BaseCommand):
    def handle(self, *args, **options):
        optimisation_bayesian_scikit.run_algo_on_test_data()
