from django.core.management.base import BaseCommand
from backtesting.momentum_1min_candle.ann.data_gen import generate_data


class Command(BaseCommand):
    def handle(self, *args, **options):
        generate_data()
