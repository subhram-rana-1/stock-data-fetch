from django.core.management.base import BaseCommand
from backtesting.momentum_v1 import main as momentum_v1_main


class Command(BaseCommand):
    def handle(self, *args, **options):
        momentum_v1_main.main()
