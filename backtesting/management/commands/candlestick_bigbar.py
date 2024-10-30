from django.core.management.base import BaseCommand
from backtesting.candlesticks.bigbar import main as candlestick_bigbar_main


class Command(BaseCommand):
    def handle(self, *args, **options):
        candlestick_bigbar_main.main()
