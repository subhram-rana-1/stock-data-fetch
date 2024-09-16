import time
from kiteconnect import KiteTicker
from datetime import datetime
from common.constants import nifty50_instrument_token, data_fetch_finish_time, IST_timezone
from common.entities import TickerData
from common.kite_client import new_kite_websocket_client
from price_app.models import NiftyPrice


def subscribe_to_nifty50_instrument(ws, response):
    ws.subscribe([nifty50_instrument_token])
    ws.set_mode(ws.MODE_LTP, [nifty50_instrument_token])


def close_websocket_connection(ws, code, reason):
    ws.stop()


def save_nifty_ltp_to_db(ws, ticks):
    stock_data: TickerData = ticks[0]
    current_nifty_point: float = stock_data['last_price']

    nifty_price: NiftyPrice = NiftyPrice(
        date=datetime.now().date(),
        timestamp=datetime.now().astimezone(IST_timezone).time(),
        price=current_nifty_point,
    )
    nifty_price.save()

    print(f'NIFTY : inserting into DB: {current_nifty_point}')


def start_fetching_nifty_price_and_inserting_into_db():
    kws: KiteTicker = new_kite_websocket_client('NIFTY')

    kws.on_connect = subscribe_to_nifty50_instrument
    kws.on_ticks = save_nifty_ltp_to_db
    kws.on_close = close_websocket_connection

    kws.connect(threaded=True)

    while datetime.now().time() <= data_fetch_finish_time:
        time.sleep(1)

    kws.close()
