from datetime import time
import json
from typing import List
from backtesting.enums import Market
from price_app.scripts.momentum_analysis.momentum_analysis import time_str_format


def get_optimised_param_dict(
        market: Market,
        smooth_price_averaging_method: str,
        smooth_slope_averaging_method: str,
        min_entry_time: time,
        profit_target_type: str,
        stoploss_type: str,
        profit_target_points: float,
        stoploss_points: float,
        params: List[float],
) -> dict:
    return {
        'market': market.name,
        'chart_config': {
            'smooth_price_averaging_method': smooth_price_averaging_method,
            'smooth_price_period': round(float(params[0]), 2),
            'smooth_price_ema_period': round(float(params[1]), 2),
            'smooth_slope_averaging_method': smooth_slope_averaging_method,
            'smooth_slope_period': round(float(params[2]), 2),
            'smooth_slope_ema_period': round(float(params[3]), 2),
        },
        'trade_config': {
            'trend_line_time_period': round(float(params[4]), 2),
            'min_entry_time': min_entry_time.strftime(time_str_format),
            'entry_conditions': [
                {
                    'max_variance': round(float(params[5]), 2),
                    'min_abs_trend_slope': round(float(params[6]), 2),
                    'min_abs_price_slope': round(float(params[7]), 2),
                    'min_abs_price_momentum': round(float(params[8]), 2),
                },
                {
                    'max_variance': round(float(params[9]), 2),
                    'min_abs_trend_slope': round(float(params[10]), 2),
                    'min_abs_price_slope': round(float(params[11]), 2),
                    'min_abs_price_momentum': round(float(params[12]), 2),
                },
                {
                    'max_variance': round(float(params[13]), 2),
                    'min_abs_trend_slope': round(float(params[14]), 2),
                    'min_abs_price_slope': round(float(params[15]), 2),
                    'min_abs_price_momentum': round(float(params[16]), 2),
                },
                {
                    'max_variance': round(float(params[17]), 2),
                    'min_abs_trend_slope': round(float(params[18]), 2),
                    'min_abs_price_slope': round(float(params[19]), 2),
                    'min_abs_price_momentum': round(float(params[20]), 2),
                },
            ],
            'exit_condition': {
                'profit_target_type': profit_target_type,
                'profit_target_points': profit_target_points,
                'stoploss_type': stoploss_type,
                'stoploss_points': stoploss_points,
            }
        },
    }


def write_to_json_file(params_dict: dict, file_path: str):
    with open(file_path, "w") as json_file:
        json.dump(params_dict, json_file, indent=4)

