from django.core.management.base import BaseCommand
from backtesting.momentum_1min_candle.ann import ann


class Command(BaseCommand):
    def handle(self, *args, **options):
        ann.main()
