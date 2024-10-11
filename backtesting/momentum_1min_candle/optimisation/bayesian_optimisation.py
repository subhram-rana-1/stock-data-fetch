from skopt import gp_minimize

from backtesting.momentum_1min_candle.optimisation import common
from backtesting.momentum_1min_candle.optimisation.common import FixedInputs, \
    preload_cache_for_stock_price, cost_function
from backtesting.momentum_1min_candle.utils import get_optimised_param_dict, write_to_json_file
from skopt.space import Categorical

optimised_params_json_file_path = "backtesting/momentum_1min_candle/optimised_params_bayesian.json"

search_space = [
    Categorical(common.search_range_chat_config_smooth_price_periods, name='chat_config_smooth_price_periods'),
    Categorical(common.search_range_chat_config_smooth_price_ema_periods, name='chat_config_smooth_price_ema_periods'),
    Categorical(common.search_range_chat_config_smooth_slope_periods, name='chat_config_smooth_slope_periods'),
    Categorical(common.search_range_chat_config_smooth_slope_ema_periods, name='chat_config_smooth_slope_ema_periods'),
    Categorical(common.search_range_trade_config_trend_line_time_periods_in_sec, name='trade_config_trend_line_time_periods_in_sec'),
    Categorical(common.search_range_trade_config_entry_condition_1_max_variance, name='trade_config_entry_condition_1_max_variance'),
    Categorical(common.search_range_trade_config_entry_condition_1_min_abs_trend_slope, name='trade_config_entry_condition_1_min_abs_trend_slope'),
    Categorical(common.search_range_trade_config_entry_condition_1_min_abs_price_slope, name='trade_config_entry_condition_1_min_abs_price_slope'),
    Categorical(common.search_range_trade_config_entry_condition_1_min_abs_price_momentum, name='trade_config_entry_condition_1_min_abs_price_momentum'),
    Categorical(common.search_range_trade_config_entry_condition_2_max_variance, name='trade_config_entry_condition_2_max_variance'),
    Categorical(common.search_range_trade_config_entry_condition_2_min_abs_trend_slope, name='trade_config_entry_condition_2_min_abs_trend_slope'),
    Categorical(common.search_range_trade_config_entry_condition_2_min_abs_price_slope, name='trade_config_entry_condition_2_min_abs_price_slope'),
    Categorical(common.search_range_trade_config_entry_condition_2_min_abs_price_momentum, name='trade_config_entry_condition_2_min_abs_price_momentum'),
    Categorical(common.search_range_trade_config_entry_condition_3_max_variance, name='trade_config_entry_condition_3_max_variance'),
    Categorical(common.search_range_trade_config_entry_condition_3_min_abs_trend_slope, name='trade_config_entry_condition_3_min_abs_trend_slope'),
    Categorical(common.search_range_trade_config_entry_condition_3_min_abs_price_slope, name='trade_config_entry_condition_3_min_abs_price_slope'),
    Categorical(common.search_range_trade_config_entry_condition_3_min_abs_price_momentum, name='trade_config_entry_condition_3_min_abs_price_momentum'),
    Categorical(common.search_range_trade_config_entry_condition_4_max_variance, name='trade_config_entry_condition_4_max_variance'),
    Categorical(common.search_range_trade_config_entry_condition_4_min_abs_trend_slope, name='trade_config_entry_condition_4_min_abs_trend_slope'),
    Categorical(common.search_range_trade_config_entry_condition_4_min_abs_price_slope, name='trade_config_entry_condition_4_min_abs_price_slope'),
    Categorical(common.search_range_trade_config_entry_condition_4_min_abs_price_momentum, name='trade_config_entry_condition_4_min_abs_price_momentum'),
]


def main():
    preload_cache_for_stock_price()

    res = gp_minimize(cost_function, search_space, n_calls=20)

    # ---------------- EXAMPLE RESULT -------------------
    # res_x = [np.int64(11), np.int64(20), np.int64(35), np.int64(45), np.int64(120), np.float64(6.5),
    #  np.float64(0.17500000000000002), np.float64(24.700000000000003), np.float64(5.369999999999999), np.float64(4.5),
    #  np.float64(0.35000000000000003), np.float64(5.2), np.float64(2.6899999999999995), np.float64(0.5),
    #  np.float64(0.55), np.float64(1.9000000000000001), np.float64(0.12999999999999998), np.float64(8.5),
    #  np.float64(0.1), np.float64(3.1), np.float64(0.16999999999999998)]
    # ------------------------------------------------------

    print("Best parameters:", res.x)
    print("Best cost:", res.fun)

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
