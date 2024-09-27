import time
from kiteconnect import KiteTicker
from datetime import timedelta
from common.constants import nifty50_instrument_token, data_fetch_finish_time, data_fetch_start_time, \
    market_opening_time, market_closing_time
from common.entities import TickerData
from common.kite_client import new_kite_websocket_client
from common.utils import current_ist_timestamp, now_ist
from price_app.models import NiftyPrice


def subscribe_to_nifty50_instrument(ws, response):
    ws.subscribe([nifty50_instrument_token])
    ws.set_mode(ws.MODE_LTP, [nifty50_instrument_token])


def close_websocket_connection(ws, code, reason):
    ws.stop()


def save_nifty_ltp_to_db(ws, ticks):
    stock_data: TickerData = ticks[0]
    current_nifty_point: float = stock_data['last_price']

    print(f'starting --> NIFTY [{now_ist()}] : {current_nifty_point}')

    nifty_price: NiftyPrice = NiftyPrice(
        timestamp=current_ist_timestamp(),
        tick_price=current_nifty_point,
    )
    nifty_price.save()

    print(f'done --> NIFTY [{now_ist()}] : {current_nifty_point}')


def start_fetching_nifty_price_and_inserting_into_db():
    kws: KiteTicker = new_kite_websocket_client('NIFTY')

    kws.on_connect = subscribe_to_nifty50_instrument
    kws.on_ticks = save_nifty_ltp_to_db
    kws.on_close = close_websocket_connection

    while now_ist() <= min(data_fetch_start_time, market_opening_time):
        time.sleep(5)

    print('starting nifty price async fetching process........')
    kws.connect(threaded=True)

    while now_ist() <= min(data_fetch_finish_time, market_closing_time):
        time.sleep(1)

    kws.close()
