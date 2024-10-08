from django.core.management.base import BaseCommand
from backtesting.momentum_1min_candle import main as momentum_1min_candle_main


class Command(BaseCommand):
    def handle(self, *args, **options):
        momentum_1min_candle_main.main()
