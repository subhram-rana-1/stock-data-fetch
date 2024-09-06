#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import threading

from price_fetch import main as price_fetch_main


def async_start_fetch_price():
    print('[ASYNC SPAWN] - price fetch main function ...')

    thread = threading.Thread(target=price_fetch_main.main)
    thread.start()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_data_fetch.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    async_start_fetch_price()

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
