from datetime import datetime
import pygad
from backtesting.momentum_1min_candle.optimisation import common
from backtesting.momentum_1min_candle.optimisation.common import cost_function, FixedInputs
from backtesting.momentum_1min_candle.utils import get_optimised_param_dict, write_to_json_file


optimised_params_json_file_path = "backtesting/momentum_1min_candle/optimised_params_ga.json"


class GAParams:
    num_generations = 500
    sol_per_pop = 10000
    num_parents_mating = 25  # [sol_per_pop * 50% ... sol_per_pop * 80%] --> trade oif b/w exploration VS exploitation
    num_genes = common.total_param_count
    parent_selection_type = "rank"
    crossover_type = "uniform"
    crossover_probability = 0.8
    mutation_type = "random"
    mutation_probability = 0.2
    parallel_processing = ("thread", 8)
    gene_space = [
        {'low': 2, 'high': 30, 'step': 2},  # chat_config_smooth_price_periods
        {'low': 10, 'high': 200, 'step': 5},  # chat_config_smooth_price_ema_periods
        {'low': 2, 'high': 30, 'step': 2},  # chat_config_smooth_slope_periods
        {'low': 5, 'high': 50, 'step': 5},  # chat_config_smooth_slope_ema_periods
        {'low': 10, 'high': 200, 'step': 5},  # trade_config_trend_line_time_periods_in_sec
        {'low': 0.5, 'high': 10, 'step': 0.5},  # trade_config_entry_condition_1_max_variance
        {'low': 0, 'high': 2, 'step': 0.025},  # trade_config_entry_condition_1_min_abs_trend_slope
        {'low': 0.1, 'high': 30, 'step': 0.1},  # trade_config_entry_condition_1_min_abs_price_slope
        {'low': 0.01, 'high': 10, 'step': 0.02},  # trade_config_entry_condition_1_min_abs_price_momentum
        {'low': 0.5, 'high': 10, 'step': 0.5},  # trade_config_entry_condition_2_max_variance
        {'low': 0, 'high': 2, 'step': 0.025},  # trade_config_entry_condition_2_min_abs_trend_slope
        {'low': 0.1, 'high': 30, 'step': 0.1},  # trade_config_entry_condition_2_min_abs_price_slope
        {'low': 0.01, 'high': 10, 'step': 0.02},  # trade_config_entry_condition_2_min_abs_price_momentum
        {'low': 0.5, 'high': 10, 'step': 0.5},  # trade_config_entry_condition_3_max_variance
        {'low': 0, 'high': 2, 'step': 0.025},  # trade_config_entry_condition_3_min_abs_trend_slope
        {'low': 0.1, 'high': 30, 'step': 0.1},  # trade_config_entry_condition_3_min_abs_price_slope
        {'low': 0.01, 'high': 10, 'step': 0.02},  # trade_config_entry_condition_3_min_abs_price_momentum
        {'low': 0.5, 'high': 10, 'step': 0.5},  # trade_config_entry_condition_4_max_variance
        {'low': 0, 'high': 2, 'step': 0.025},  # trade_config_entry_condition_4_min_abs_trend_slope
        {'low': 0.1, 'high': 30, 'step': 0.1},  # trade_config_entry_condition_4_min_abs_price_slope
        {'low': 0.01, 'high': 10, 'step': 0.02},  # trade_config_entry_condition_4_min_abs_price_momentum
    ]


def fitness_function(ga_instance: pygad.GA, params, solution_idx):
    print(f'completed generation: {ga_instance.generations_completed}')

    try:
        return -1 * cost_function(params)
    except Exception as e:
        print(f'wrong params: {params}')
        raise


def main():
    ga_instance = pygad.GA(
        num_generations=GAParams.num_generations,
        sol_per_pop=GAParams.sol_per_pop,
        num_parents_mating=GAParams.num_parents_mating,
        num_genes=GAParams.num_genes,
        parent_selection_type=GAParams.parent_selection_type,
        crossover_type=GAParams.crossover_type,
        crossover_probability=GAParams.crossover_probability,
        mutation_type=GAParams.mutation_type,
        mutation_probability=GAParams.mutation_probability,
        mutation_percent_genes=GAParams.mutation_probability,
        parallel_processing=GAParams.parallel_processing,
        gene_space=GAParams.gene_space,
        fitness_func=fitness_function,
    )

    # Run the optimization and get best solution
    t1 = datetime.now()
    ga_instance.run()
    best_chromosome = ga_instance.best_solution()
    t2 = datetime.now()

    params_array = best_chromosome[0]
    best_params = params_array.tolist()

    time_difference = t2 - t1
    total_seconds = int(time_difference.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    print(f"Completed in {minutes} minutes and {seconds} seconds\n"
          f"best params: {best_params}")



    optimised_params_dict = get_optimised_param_dict(
        market=FixedInputs.market,
        smooth_price_averaging_method=FixedInputs.smooth_price_averaging_method,
        smooth_slope_averaging_method=FixedInputs.smooth_slope_averaging_method,
        min_entry_time=FixedInputs.min_entry_time,
        profit_target_type=FixedInputs.profit_target_type,
        stoploss_type=FixedInputs.stoploss_type,
        profit_target_points=FixedInputs.profit_target_points,
        stoploss_points=FixedInputs.stoploss_points,
        params=best_params,
    )

    write_to_json_file(optimised_params_dict, f'./{optimised_params_json_file_path}')
