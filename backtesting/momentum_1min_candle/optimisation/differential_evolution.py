from scipy.optimize import differential_evolution

def cost_function_de(params):
    return cost_function(params)


def main():
    res = differential_evolution(cost_function_de, bounds, maxiter=1000, popsize=20)

    print("Best Parameters:", res.x)
    print("Best Cost:", res.fun)
