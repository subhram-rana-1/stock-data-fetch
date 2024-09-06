import time
from kiteconnect import KiteTicker
from datetime import datetime
from common.constants import data_fetch_finish_time, banknifty_instrument_token
from common.kite_client import new_kite_websocket_client


def subscribe_to_banknifty_instrument(ws, response):
    ws.subscribe([banknifty_instrument_token])
    ws.set_mode(ws.MODE_LTP, [banknifty_instrument_token])


def close_websocket_connection(ws, code, reason):
    ws.stop()


def save_banknifty_ltp_to_db(ws, ticks):
    """TODO: save in DB"""
    print('BANKNIFTY : inserting into DB')


def start_fetching_banknifty_price_and_inserting_into_db():
    kws: KiteTicker = new_kite_websocket_client()

    kws.on_connect = subscribe_to_banknifty_instrument
    kws.on_ticks = save_banknifty_ltp_to_db
    kws.on_close = close_websocket_connection

    kws.connect(threaded=True)

    while datetime.now().time() <= data_fetch_finish_time:
        time.sleep(1)

    kws.close()
