import threading
import time
from common.constants import data_fetch_start_time, data_fetch_finish_time
from common.kite_client import KiteConnectClient
from kiteconnect import KiteConnect
from datetime import datetime

from price_fetch.banknifty import start_fetching_banknifty_price_and_inserting_into_db
from price_fetch.nifty import start_fetching_nifty_price_and_inserting_into_db


def async_start_fetching_nifty_price_data(kc: KiteConnect):
    print('[ASYNC SPAWN] - async_start_fetching_nifty_price_data ...')

    thread = threading.Thread(target=start_fetching_nifty_price_and_inserting_into_db)
    thread.start()


def async_start_fetching_banknifty_price_data(kc: KiteConnect):
    print('[ASYNC SPAWN] - async_start_fetching_banknifty_price_data ...')

    thread = threading.Thread(target=start_fetching_banknifty_price_and_inserting_into_db)
    thread.start()


def main():
    kc: KiteConnect = KiteConnectClient()

    while datetime.now().time() < data_fetch_start_time:
        time.sleep(3)

    async_start_fetching_nifty_price_data(kc)
    async_start_fetching_banknifty_price_data(kc)

    while datetime.now().time() <= data_fetch_finish_time:
        time.sleep(3)


if __name__ == '__main__':
    main()
