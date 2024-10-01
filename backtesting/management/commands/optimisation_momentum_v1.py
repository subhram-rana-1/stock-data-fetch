from django.core.management.base import BaseCommand
from backtesting.momentum_v1 import optimisation as momentum_v1_optimisation


class Command(BaseCommand):
    def handle(self, *args, **options):
        momentum_v1_optimisation.main()
