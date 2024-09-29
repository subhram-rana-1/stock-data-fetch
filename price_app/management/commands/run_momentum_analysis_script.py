import os

from django.core.management.base import BaseCommand
from price_app.scripts.momentum_analysis_v1 import momentum_analysis
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        momentum_analysis.main()
