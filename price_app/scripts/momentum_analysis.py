# Runs simulation from start date to end date, generates entry and exit points in momentum catching
# and stores in output xlsx sheet

from datetime import datetime, date, time, timedelta
from typing import List

from price_app.classes import PriceData, PriceDataPerTick
from price_app.handlers import fetch_price_data
from stock_data_fetch.enums import MarketType

# CONSTANTS ---------
direction_up = 'up'
direction_down = 'down'
market_entry_time = time(9, 16)
market_exit_time = time(15, 29)
exit_reason_crossover = 'crossover'
exit_reason_sl_hit = 'sl_hit'
date_str_format = "%Y-%m-%d"
time_str_format = "%H:%M:%S"


# CONFIGS ---------
class Config:
    smooth_price_averaging_method = 'exponential'  # exponential
    smooth_price_period = 8
    smooth_price_ema_period = 40

    smooth_slope_averaging_method = 'simple'  # exponential
    smooth_slope_period = 3
    slope_ema_period = 10

    entry_config_momentum_threshold = 1.5
    sl = 12


# INPUTS ----------
class Input:
    market_type = MarketType.NIFTY
    start_date_time = datetime(2024, 9, 25, 9, 16, 0)
    end_date_time = datetime(2024, 9, 25, 9, 30, 0)


class MarketMoveData:
    def __init__(
            self,
            date: date,
            delta: float,
            expected_direction: str,
            start_time: time,
            end_time: time,
            start_point: float,
            end_point: float,
            exit_reason: str,
    ):
        self.date: date = date
        self.delta: date = delta
        self.expected_direction: str = expected_direction
        self.start_time: time = start_time
        self.end_time: time = end_time
        self.start_point: float = start_point
        self.end_point: float = end_point
        self.exit_reason: str = exit_reason

    def to_dict(self) -> dict:
        return {
            'date': self.date.strftime(date_str_format),
            'delta': round(self.delta, 2),
            'expected_direction': self.expected_direction,
            'start_time': self.start_time.strftime(time_str_format),
            'end_time': self.end_time.strftime(time_str_format),
            'start_point': round(self.start_point, 2),
            'end_point': round(self.end_point, 2),
            'exit_reason': self.exit_reason,
        }


def entry_condition_for_up_move(slope: float, momentum: float,
                                entry_config_momentum_threshold: float) -> bool:
    return slope > 0 and momentum >= entry_config_momentum_threshold


def entry_condition_for_down_move(slope: float, momentum: float,
                                  entry_config_momentum_threshold: float) -> bool:
    return slope < 0 and momentum <= -1 * entry_config_momentum_threshold


def cross_over_happened_in_up_move(cur_smooth_price: float, cur_smooth_price_ema: float) -> bool:
    return cur_smooth_price < cur_smooth_price_ema


def cross_over_happened_in_down_move(cur_smooth_price: float, cur_smooth_price_ema: float) -> bool:
    return cur_smooth_price > cur_smooth_price_ema


def sl_hit_in_upward_expected_move(tick_price: float, start_tick_price: float, sl: float):
    return tick_price <= start_tick_price - sl


def sl_hit_in_downward_expected_move(tick_price: float, start_tick_price: float, sl: float):
    return tick_price >= start_tick_price + sl


def get_market_moves_for_day(
        market_type: MarketType,
        config: Config,
        day: date,
        start_time: time,
        end_time: time,
) -> List[MarketMoveData]:
    price_data: PriceData = fetch_price_data(
        market_type,
        day,
        day,
        start_time,
        end_time,
        config.smooth_price_period,
        config.smooth_price_ema_period,
        config.smooth_slope_period,
        config.slope_ema_period,
    )

    price_list: List[PriceDataPerTick] = price_data['price_list']
    n = len(price_list)
    i = 0

    res: List[MarketMoveData] = []

    while i < n - 1:
        price_info: PriceDataPerTick = price_list[i]

        tm: time = price_info['tm']
        tick_price: float = price_info['tick_price']
        slope: float = price_info['slope']
        smooth_slope: float = price_info['smooth_slope']
        momentum: float = price_info['momentum']

        if entry_condition_for_up_move(slope, momentum, config.entry_config_momentum_threshold):
            start_tm: time = tm
            start_tick_price: float = tick_price

            exit_reason = exit_reason_crossover
            j = i + 1
            while j < n:
                cur_tick_price = price_list[j]['tick_price']
                cur_smooth_price = price_list[j]['smooth_price']
                cur_smooth_price_ema = price_list[j]['smooth_price_ema']

                if sl_hit_in_upward_expected_move(cur_tick_price, start_tick_price, config.sl):
                    exit_reason = exit_reason_sl_hit
                    break

                if cross_over_happened_in_up_move(cur_smooth_price, cur_smooth_price_ema):
                    print('cross over jus happened...')
                    print(f'cur_time: {price_list[j]["tm"]}')
                    print(f'cur_smooth_price: {cur_smooth_price}')
                    print(f'cur_smooth_price_ema: {cur_smooth_price_ema}')
                    break

                j += 1

            if j == n:
                j -= 1

            end_time: time = price_list[j]['tm']
            end_tick_price: float = price_list[j]['tick_price']
            delta = price_list[j]['tick_price'] - start_tick_price

            res.append(MarketMoveData(
                date=day,
                delta=delta,
                expected_direction=direction_up,
                start_time=start_tm,
                end_time=end_time,
                start_point=start_tick_price,
                end_point=end_tick_price,
                exit_reason=exit_reason,
            ))

            i = j + 1
        elif entry_condition_for_down_move(slope, momentum, config.entry_config_momentum_threshold):
            start_tm: time = tm
            start_tick_price: float = tick_price

            exit_reason = exit_reason_crossover
            j = i + 1
            while j < n:
                cur_tick_price = price_list[j]['tick_price']
                cur_smooth_price = price_list[j]['smooth_price']
                cur_smooth_price_ema = price_list[j]['smooth_price_ema']

                if sl_hit_in_downward_expected_move(cur_tick_price, start_tick_price, config.sl):
                    exit_reason = exit_reason_sl_hit
                    break

                if cross_over_happened_in_down_move(cur_smooth_price, cur_smooth_price_ema):
                    print('cross over jus happened...')
                    print(f'cur_time: {price_list[j]["tm"]}')
                    print(f'cur_smooth_price: {cur_smooth_price}')
                    print(f'cur_smooth_price_ema: {cur_smooth_price_ema}')
                    break

                j += 1

            if j == n:
                j -= 1

            end_time: time = price_list[j]['tm']
            end_tick_price: float = price_list[j]['tick_price']
            delta = price_list[j]['tick_price'] - start_tick_price

            res.append(MarketMoveData(
                date=day,
                delta=delta,
                expected_direction=direction_down,
                start_time=start_tm,
                end_time=end_time,
                start_point=start_tick_price,
                end_point=end_tick_price,
                exit_reason=exit_reason,
            ))

            i = j + 1
        else:
            i += 1

    return res


def simulate_momentum_analysis(
        config: Config,
        input: Input,
) -> List[MarketMoveData]:
    global_start_date = Input.start_date_time.date()
    global_start_time = Input.start_date_time.time()
    global_end_date = Input.end_date_time.date()
    global_end_time = Input.end_date_time.time()

    res = []

    day = global_start_date
    while day <= global_end_date:
        start_time = global_start_time if day == global_start_date else market_entry_time
        end_time = global_end_time if day == global_end_date else market_exit_time

        print(f'day: {day}, start time: {start_time}, end time: {end_time}')

        res.extend(get_market_moves_for_day(
            input.market_type,
            config,
            day,
            start_time,
            end_time,
        ))

        day += timedelta(days=1)

    return res


def main():
    market_moves: List[MarketMoveData] = simulate_momentum_analysis(Config(), Input())
    print([market_move.to_dict() for market_move in market_moves])
