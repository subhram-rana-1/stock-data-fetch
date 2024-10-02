import pytz
from datetime import time

market_opening_time = time(9, 15)
market_closing_time = time(15, 30)

data_fetch_start_time = market_opening_time
data_fetch_finish_time = market_closing_time

nifty50_instrument_token = 256265  # taken from ZERODHA
banknifty_instrument_token = 260105  # taken from ZERODHA

IST_timezone = pytz.timezone('Asia/Kolkata')

date_format_string = "%Y-%m-%d"
time_format_string = "%H:%M:%S"
datetime_format_string = "%Y-%m-%d %H:%M:%S"
