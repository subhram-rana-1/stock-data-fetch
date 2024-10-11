from scipy.optimize import differential_evolution

from backtesting.momentum_1min_candle.optimisation import common
from backtesting.momentum_1min_candle.optimisation.bayesian_optimisation import optimised_params_json_file_path
from backtesting.momentum_1min_candle.optimisation.common import cost_function, FixedInputs
from backtesting.momentum_1min_candle.utils import get_optimised_param_dict, write_to_json_file


optimised_params_json_file_path = \
    "backtesting/momentum_1min_candle/optimised_params_differential_evolution.json"


search_bounds = [
    [common.search_range_chat_config_smooth_price_periods[0],
     common.search_range_chat_config_smooth_price_periods[1]],

    [common.search_range_chat_config_smooth_price_ema_periods[0],
     common.search_range_chat_config_smooth_price_ema_periods[1]],

    [common.search_range_chat_config_smooth_slope_periods[0],
     common.search_range_chat_config_smooth_slope_periods[1]],

    [common.search_range_chat_config_smooth_slope_ema_periods[0],
     common.search_range_chat_config_smooth_slope_ema_periods[1]],

    [common.search_range_trade_config_trend_line_time_periods_in_sec[0],
     common.search_range_trade_config_trend_line_time_periods_in_sec[1]],

    [common.search_range_trade_config_entry_condition_1_max_variance[0],
     common.search_range_trade_config_entry_condition_1_max_variance[1]],

    [common.search_range_trade_config_entry_condition_1_min_abs_trend_slope[0],
     common.search_range_trade_config_entry_condition_1_min_abs_trend_slope[1]],

    [common.search_range_trade_config_entry_condition_1_min_abs_price_slope[0],
     common.search_range_trade_config_entry_condition_1_min_abs_price_slope[1]],

    [common.search_range_trade_config_entry_condition_1_min_abs_price_momentum[0],
     common.search_range_trade_config_entry_condition_1_min_abs_price_momentum[1]],

    [common.search_range_trade_config_entry_condition_2_max_variance[0],
     common.search_range_trade_config_entry_condition_2_max_variance[1]],

    [common.search_range_trade_config_entry_condition_2_min_abs_trend_slope[0],
     common.search_range_trade_config_entry_condition_2_min_abs_trend_slope[1]],

    [common.search_range_trade_config_entry_condition_2_min_abs_price_slope[0],
     common.search_range_trade_config_entry_condition_2_min_abs_price_slope[1]],

    [common.search_range_trade_config_entry_condition_2_min_abs_price_momentum[0],
     common.search_range_trade_config_entry_condition_2_min_abs_price_momentum[1]],

    [common.search_range_trade_config_entry_condition_3_max_variance[0],
     common.search_range_trade_config_entry_condition_3_max_variance[1]],

    [common.search_range_trade_config_entry_condition_3_min_abs_trend_slope[0],
     common.search_range_trade_config_entry_condition_3_min_abs_trend_slope[1]],

    [common.search_range_trade_config_entry_condition_3_min_abs_price_slope[0],
     common.search_range_trade_config_entry_condition_3_min_abs_price_slope[1]],

    [common.search_range_trade_config_entry_condition_3_min_abs_price_momentum[0],
     common.search_range_trade_config_entry_condition_3_min_abs_price_momentum[1]],

    [common.search_range_trade_config_entry_condition_4_max_variance[0],
     common.search_range_trade_config_entry_condition_4_max_variance[1]],

    [common.search_range_trade_config_entry_condition_4_min_abs_trend_slope[0],
     common.search_range_trade_config_entry_condition_4_min_abs_trend_slope[1]],

    [common.search_range_trade_config_entry_condition_4_min_abs_price_slope[0],
     common.search_range_trade_config_entry_condition_4_min_abs_price_slope[1]],

    [common.search_range_trade_config_entry_condition_4_min_abs_price_momentum[0],
     common.search_range_trade_config_entry_condition_4_min_abs_price_momentum[1]],

]


def main():
    res = differential_evolution(cost_function, search_bounds, maxiter=1000, popsize=20)

    print("Best Parameters:", res.x)
    print("Best Cost:", res.fun)

    optimised_params_dict = get_optimised_param_dict(
        market=FixedInputs.market,
        smooth_price_averaging_method=FixedInputs.smooth_price_averaging_method,
        smooth_slope_averaging_method=FixedInputs.smooth_slope_averaging_method,
        min_entry_time=FixedInputs.min_entry_time,
        profit_target_type=FixedInputs.profit_target_type,
        stoploss_type=FixedInputs.stoploss_type,
        profit_target_points=FixedInputs.profit_target_points,
        stoploss_points=FixedInputs.stoploss_points,
        params=res.x,
    )

    write_to_json_file(optimised_params_dict, f'./{optimised_params_json_file_path}')
