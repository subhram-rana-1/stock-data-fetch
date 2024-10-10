import pygad
import numpy as np


def main():
    ga_instance = pygad.GA(num_generations=num_generations,
                           num_parents_mating=num_parents_mating,
                           fitness_func=fitness_function,
                           sol_per_pop=sol_per_pop,
                           num_genes=num_genes,
                           initial_population=initial_population,
                           parent_selection_type="rank",
                           crossover_type="uniform",
                           mutation_type="random",
                           mutation_percent_genes=10)

    # Run the optimization
    ga_instance.run()

    # Get the best solution
    best_solution = ga_instance.best_solution()
    print(f"Best Parameters: {best_solution}")