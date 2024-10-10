from django.core.management.base import BaseCommand
from backtesting.momentum_1min_candle.optimisation.bayesian_optimisation import main


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
