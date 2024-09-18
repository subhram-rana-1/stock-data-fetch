import threading
import time
from common.constants import data_fetch_start_time
from common.kite_client import KiteConnectClient
from kiteconnect import KiteConnect

from common.utils import now_ist
from stock_data_fetch.banknifty_price_fetch import start_fetching_banknifty_price_and_inserting_into_db
from stock_data_fetch.nifty_price_fetch import start_fetching_nifty_price_and_inserting_into_db


def async_start_fetching_nifty_price_data(kc: KiteConnect):
    print('[ASYNC SPAWN] - async_start_fetching_nifty_price_data ...')

    thread = threading.Thread(target=start_fetching_nifty_price_and_inserting_into_db)
    thread.start()


def async_start_fetching_banknifty_price_data(kc: KiteConnect):
    print('[ASYNC SPAWN] - async_start_fetching_banknifty_price_data ...')

    thread = threading.Thread(target=start_fetching_banknifty_price_and_inserting_into_db)
    thread.start()


def main():
    print(f'[MAIN] : Started data fetch main function ...')

    kc: KiteConnect = KiteConnectClient()

    while now_ist() < data_fetch_start_time:
        time.sleep(3)

    async_start_fetching_nifty_price_data(kc)
    time.sleep(0.5)  # sleeping to instantiate web socket without any 'ReactorAlreadyRunning' exception
    async_start_fetching_banknifty_price_data(kc)
