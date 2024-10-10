from scipy.optimize import differential_evolution
from backtesting.momentum_1min_candle.optimisation.bayesian_optimisation import optimised_params_json_file_path
from backtesting.momentum_1min_candle.optimisation.common import cost_function, FixedInputs, search_bounds
from backtesting.momentum_1min_candle.utils import get_optimised_param_dict, write_to_json_file


optimised_params_json_file_path = \
    "backtesting/momentum_1min_candle/optimised_params_differential_evolution.json"


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
