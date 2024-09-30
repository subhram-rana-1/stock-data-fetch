import time
from kiteconnect import KiteTicker
from common.constants import data_fetch_finish_time, banknifty_instrument_token, data_fetch_start_time, \
    market_opening_time, market_closing_time
from common.entities import TickerData
from common.kite_client import new_kite_websocket_client
from common.utils import now_ist, current_ist_timestamp
from price_app.models import BankNiftyPrice


def subscribe_to_banknifty_instrument(ws, response):
    ws.subscribe([banknifty_instrument_token])
    ws.set_mode(ws.MODE_LTP, [banknifty_instrument_token])


def close_websocket_connection(ws, code, reason):
    ws.stop()


def save_banknifty_ltp_to_db(ws, ticks):
    stock_data: TickerData = ticks[0]
    current_banknifty_point = stock_data['last_price']

    print(f'starting --> BANKNIFTY[{now_ist()}] : {current_banknifty_point}')

    banknifty_price: BankNiftyPrice = BankNiftyPrice(
        timestamp=current_ist_timestamp(),
        tick_price=current_banknifty_point,
    )
    banknifty_price.save()

    print(f'done --> BANKNIFTY[{now_ist()}] : {current_banknifty_point}')


def start_fetching_banknifty_price_and_inserting_into_db():
    kws: KiteTicker = new_kite_websocket_client('BANKNIFTY')

    kws.on_connect = subscribe_to_banknifty_instrument
    kws.on_ticks = save_banknifty_ltp_to_db
    kws.on_close = close_websocket_connection

    while now_ist() <= min(data_fetch_start_time, market_opening_time):
        time.sleep(5)

    print('starting bank nifty price async fetching process........')
    kws.connect(threaded=True)

    while now_ist() <= min(data_fetch_finish_time, market_closing_time):
        time.sleep(1)

    kws.close()
