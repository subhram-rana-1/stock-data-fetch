from django.core.management.base import BaseCommand
from backtesting.momentum_v1 import optimisation_bayesian_scikit


class Command(BaseCommand):
    def handle(self, *args, **options):
        optimisation_bayesian_scikit.main()
