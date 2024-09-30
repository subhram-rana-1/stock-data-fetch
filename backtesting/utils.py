from typing import List
import statistics
from backtesting.entities import LinearRegressionLine


def get_linear_regression_result(nums: List[float]) -> LinearRegressionLine:
    n = len(nums)
    x_vals = list(range(n))  # Assuming x values are indices (0, 1, 2,...)
    y_vals = nums

    # Summation calculations
    sum_x = sum(x_vals)
    sum_y = sum(y_vals)
    sum_x_squared = sum(x ** 2 for x in x_vals)
    sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))

    # Slope (m) and Intercept (c)
    m = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x ** 2)
    c = (sum_y - m * sum_x) / n

    # Variance calculation
    y_mean = statistics.mean(y_vals)
    variance = sum((y - (m * x + c)) ** 2 for x, y in zip(x_vals, y_vals)) / n

    return LinearRegressionLine(m, c, variance)
