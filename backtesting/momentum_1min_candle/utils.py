from datetime import time
import json
from typing import List
from backtesting.enums import Market


def get_optimised_param_dict(
        market: Market,
        smooth_price_averaging_method: str,
        smooth_slope_averaging_method: str,
        min_entry_time: time,
        profit_target_type: str,
        stoploss_type: str,
        params: List[float],
) -> dict:
    return {
        'market': market.name,
        'chart_config': {
            'smooth_price_averaging_method': smooth_price_averaging_method,
            'smooth_price_period': params[0],
            'smooth_price_ema_period': params[1],
            'smooth_slope_averaging_method': smooth_slope_averaging_method,
            'smooth_slope_period': params[2],
            'smooth_slope_ema_period': params[3],
        },
        'trade_config': {
            'trend_line_time_period': params[4],
            'min_entry_time': min_entry_time,
            'entry_conditions': [
                {
                    'max_variance': params[5],
                    'min_abs_trend_slope': params[6],
                    'min_abs_price_slope': params[7],
                    'min_abs_price_momentum': params[8],
                },
                {
                    'max_variance': params[9],
                    'min_abs_trend_slope': params[10],
                    'min_abs_price_slope': params[11],
                    'min_abs_price_momentum': params[12],
                },
                {
                    'max_variance': params[13],
                    'min_abs_trend_slope': params[14],
                    'min_abs_price_slope': params[15],
                    'min_abs_price_momentum': params[16],
                },
                {
                    'max_variance': params[17],
                    'min_abs_trend_slope': params[17],
                    'min_abs_price_slope': params[18],
                    'min_abs_price_momentum': params[19],
                },
            ],
            'exit_condition': {
                'profit_target_type': profit_target_type,
                'profit_target_points': params[20],
                'stoploss_type': stoploss_type,
                'stoploss_points': params[21],
            }
        },
    }


def write_to_json_file(params_dict: dict):
    with open("./backtesting/momentum_1min_candle/optimised_params.json", "w") as json_file:
        json.dump(params_dict, json_file, indent=4)

