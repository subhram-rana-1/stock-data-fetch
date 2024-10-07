from django.core.management.base import BaseCommand
from backtesting.momentum_v1 import optimisation_grid_search


class Command(BaseCommand):
    def handle(self, *args, **options):
        optimisation_grid_search.main()
