from django.core.management.base import BaseCommand
from backtesting.momentum_1min_candle.optimisation.differential_evolution import main


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
