import threading

from django.core.management.base import BaseCommand
from price_fetch import main as price_fetch_main


def async_start_fetch_price():
    print('[ASYNC SPAWN] - price fetch main function ...')

    thread = threading.Thread(target=price_fetch_main.main)
    thread.start()


class Command(BaseCommand):

    def handle(self, *args, **options):
        """Spawns all kafka consumers in inventory app"""
        async_start_fetch_price()
