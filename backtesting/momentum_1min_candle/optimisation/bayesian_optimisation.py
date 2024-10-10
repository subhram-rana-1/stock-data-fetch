import os
from skopt import gp_minimize
from backtesting.entities import BacktestingInput, BacktestingResult
from backtesting.momentum_1min_candle import core
from backtesting.momentum_1min_candle.optimisation.common import FixedInputsForTestDataset, FixedInputs, \
    preload_cache_for_stock_price, cost_function, search_space
from backtesting.momentum_1min_candle.utils import get_optimised_param_dict, write_to_json_file


optimised_params_json_file_path = "backtesting/momentum_1min_candle/optimised_params_bayesian.json"

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


def run_algo_on_test_data():
    back_test_input = BacktestingInput.from_json_file(
        market=FixedInputsForTestDataset.market,
        start_date=FixedInputsForTestDataset.start_date,
        start_time=FixedInputsForTestDataset.start_time,
        end_date=FixedInputsForTestDataset.end_date,
        end_time=FixedInputsForTestDataset.end_time,
        json_abs_file_path=os.path.abspath(optimised_params_json_file_path),
    )

    backtest_result: BacktestingResult = core.get_backtest_result(back_test_input)

    backtest_result.save_to_db()
