import time
from kiteconnect import KiteTicker
from datetime import datetime
from common.constants import data_fetch_finish_time, banknifty_instrument_token, data_fetch_start_time, \
    market_opening_time, market_closing_time, IST_timezone
from common.entities import TickerData
from common.kite_client import new_kite_websocket_client
from price_app.models import BankNiftyPrice


def subscribe_to_banknifty_instrument(ws, response):
    ws.subscribe([banknifty_instrument_token])
    ws.set_mode(ws.MODE_LTP, [banknifty_instrument_token])


def close_websocket_connection(ws, code, reason):
    ws.stop()


def save_banknifty_ltp_to_db(ws, ticks):
    """TODO: save in DB"""
    stock_data: TickerData = ticks[0]
    current_nifty_point = stock_data['last_price']

    nifty_price: BankNiftyPrice = BankNiftyPrice(
        timestamp=datetime.now().astimezone(IST_timezone),
        price=current_nifty_point,
    )
    nifty_price.save()

    print(f'BANKNIFTY : inserting into DB: {current_nifty_point}')


def start_fetching_banknifty_price_and_inserting_into_db():
    kws: KiteTicker = new_kite_websocket_client('BANKNIFTY')

    kws.on_connect = subscribe_to_banknifty_instrument
    kws.on_ticks = save_banknifty_ltp_to_db
    kws.on_close = close_websocket_connection

    while datetime.now().time() <= min(data_fetch_start_time, market_opening_time):
        time.sleep(5)

    kws.connect(threaded=True)

    while datetime.now().time() <= min(data_fetch_finish_time, market_closing_time):
        time.sleep(1)

    kws.close()
