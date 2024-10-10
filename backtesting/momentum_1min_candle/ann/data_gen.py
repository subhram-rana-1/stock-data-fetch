import os
import csv
from datetime import date, timedelta
from typing import List
from backtesting.momentum_1min_candle.move_catcher import Trendline
from backtesting.momentum_1min_candle.upstox import fetch_candlestick_data_from_upstox, UpstoxCandlestickResponse
from backtesting.utils import get_linear_regression_result
from price_app.classes import PriceDataPerCandle, PriceData, calculate_other_auxiliary_prices
from stock_data_fetch.enums import MarketType


class Input:
    market_type = MarketType.NIFTY
    start_date = date(2024, 8, 1)
    end_date = date(2024, 10, 10)
    dataset_file_path = './backtesting/momentum_1min_candle/ann/dataset.csv'

    dataset_input_headers = ['m1', 'sigma1', 'm2', 'sigma2', 'm3', 'sigma3', 'prie_slope',
                             'price_momentum', 'last_candle_closing_price']
    dataset_output_headers = ['up_entry', 'no_entry', 'down_entry']
    dataset_headers = dataset_input_headers + dataset_output_headers

    smooth_price_averaging_method = 'simple'
    smooth_price_period = 3
    smooth_price_ema_period = 16
    smooth_slope_averaging_method = 'simple'
    smooth_slope_period = 3
    smooth_slope_ema_period = 10

    trading_start_after_n_minutes = 20

    trend_line_1_length = 3
    trend_line_2_length = 6
    trend_line_3_length = 10

    trade_hold_for_max_candles = 6  # 6 minutes
    target_points = 20
    stoploss_points = 13


class AnnData:
    def __init__(
            self,

            # input
            trend_line_slope_1: float,
            trend_line_variance_1: float,
            trend_line_slope_2: float,
            trend_line_variance_2: float,
            trend_line_slope_3: float,
            trend_line_variance_3: float,
            price_slope: float,
            price_momentum: float,
            current_candle_closing_price: float,

            # output
            direction: List[int],  # 1(up entry), 0(no entry), -1(down entry)
    ):
        self.trend_line_slope_1 = trend_line_slope_1
        self.trend_line_variance_1 = trend_line_variance_1
        self.trend_line_slope_2 = trend_line_slope_2
        self.trend_line_variance_2 = trend_line_variance_2
        self.trend_line_slope_3 = trend_line_slope_3
        self.trend_line_variance_3 = trend_line_variance_3
        self.price_slope = price_slope
        self.price_momentum = price_momentum
        self.last_candle_closing_price = current_candle_closing_price
        self.direction = direction

    def get_values_in_list(self) -> List:
        return [
            self.trend_line_slope_1,
            self.trend_line_variance_1,
            self.trend_line_slope_2,
            self.trend_line_variance_2,
            self.trend_line_slope_3,
            self.trend_line_variance_3,
            self.price_slope,
            self.price_momentum,
            self.last_candle_closing_price,
            self.direction[0],
            self.direction[1],
            self.direction[2],
        ]


def get_trend_line(
        price_list: List[PriceDataPerCandle],
        end_index: int,
        length: int,
) -> Trendline:
    start_index = end_index - length
    price_sublist = price_list[start_index:end_index]

    price_points: List[float] = []
    for candle in price_sublist:
        price_points.append(candle['high'])
        price_points.append(candle['lo'])

    return Trendline.from_linear_regression_line(get_linear_regression_result(price_points))


def get_trade_entry_direction(
        price_list: List[PriceDataPerCandle],
        start_index: int,
        trade_hold_for_max_candles: int,
) -> List[int]:
    # direction [up, no, down]
    up_entry = [1, 0, 0]
    no_entry = [0, 1, 0]
    down_entry = [0, 0, 1]

    n = len(price_list)
    if start_index >= n:
        return no_entry

    entry_price = price_list[start_index]['open']
    up_target = entry_price + Input.target_points
    up_stoploss = entry_price - Input.stoploss_points
    down_target = entry_price - Input.target_points
    down_stoploss = entry_price + Input.stoploss_points

    i = start_index
    while i < start_index + trade_hold_for_max_candles:
        if i >= n:
            return no_entry

        if price_list[i]['high'] >= up_target:  # UP move simulation
            # check if SL was hit
            j = start_index
            while j <= i:
                if price_list[j]['lo'] <= up_stoploss:
                    return no_entry
                j += 1

            return up_entry
        elif price_list[i]['lo'] <= down_target:  # DOWN move simulation
            # check if SL was hit
            j = start_index
            while j <= i:
                if price_list[j]['high'] >= down_stoploss:
                    return no_entry
                j += 1

            return down_entry

        i += 1

    return no_entry


def get_ann_data_from_candlestick_data_for_the_day(
        daily_candle_stick: UpstoxCandlestickResponse,
) -> List[AnnData]:
    price_data: PriceData = PriceData(
        market_name=Input.market_type,
        price_list=[]
    )

    for candle in daily_candle_stick.data.candles:
        price_data['price_list'].append(candle.to_tick_by_tick_type_data())

    calculate_other_auxiliary_prices(
        price_data=price_data,
        smooth_price_averaging_method=Input.smooth_price_averaging_method,
        smooth_price_period=Input.smooth_price_period,
        smooth_price_ema_period=Input.smooth_price_ema_period,
        smooth_slope_averaging_method=Input.smooth_slope_averaging_method,
        smooth_slope_period=Input.smooth_slope_period,
        smooth_slope_ema_period=Input.smooth_slope_ema_period,
    )

    dataset: List[AnnData] = []
    price_list: List[PriceDataPerCandle] = price_data['price_list']
    i = Input.trading_start_after_n_minutes
    while i < len(price_list):
        trend_line_1: Trendline = get_trend_line(price_list, i, Input.trend_line_1_length)
        trend_line_2: Trendline = get_trend_line(price_list, i, Input.trend_line_2_length)
        trend_line_3: Trendline = get_trend_line(price_list, i, Input.trend_line_3_length)

        dataset.append(
            AnnData(
                trend_line_slope_1=trend_line_1.m,
                trend_line_variance_1=trend_line_1.variance,
                trend_line_slope_2=trend_line_2.m,
                trend_line_variance_2=trend_line_2.variance,
                trend_line_slope_3=trend_line_3.m,
                trend_line_variance_3=trend_line_3.variance,
                price_slope=price_list[i]['slope'],
                price_momentum=price_list[i]['momentum'],
                current_candle_closing_price=price_list[i]['close'],
                direction=get_trade_entry_direction(price_list, i+1, Input.trade_hold_for_max_candles),
            )
        )

        i += 1

    return dataset


def generate_data():
    upstox_candlestick_data: List[UpstoxCandlestickResponse] = []

    day = Input.start_date
    while day <= Input.end_date:
        upstox_candlestick_data.append(
            fetch_candlestick_data_from_upstox(
                Input.market_type,
                day,
                day,
            )
        )

        day += timedelta(days=1)

    dataset: List[AnnData] = []
    for daily_candle_stick in upstox_candlestick_data:
        dataset.extend(
            get_ann_data_from_candlestick_data_for_the_day(daily_candle_stick)
        )

    csv_file = os.path.abspath(Input.dataset_file_path)
    if os.path.exists(csv_file):
        os.remove(csv_file)

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(Input.dataset_headers)

        for data in dataset:
            writer.writerow(data.get_values_in_list())
