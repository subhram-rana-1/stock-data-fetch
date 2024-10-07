from typing import List
import statistics
from backtesting.entities import LinearRegressionLine


def get_linear_regression_result_util(nums: List[float]) -> LinearRegressionLine:
    n = len(nums)
    x_vals = list(range(n))  # Assuming x values are indices (0, 1, 2,...)
    y_vals = nums

    # Summation calculations
    sum_x = sum(x_vals)
    sum_y = sum(y_vals)
    sum_x_squared = sum(x ** 2 for x in x_vals)
    sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))

    # Slope (m) and Intercept (c)
    try:
        m = (n * sum_xy - sum_x * sum_y) / (n * sum_x_squared - sum_x ** 2)
    except Exception as e:
        info = {
            'n': n,
            'sum_xy': sum_xy,
            'sum_x': sum_x,
            'sum_y': sum_y,
            'sum_x_squared': sum_x_squared,
            'x_vals': x_vals,
            'nums': nums,
        }
        print(f'slope error: {e}, info: {info}')
        raise

    try:
        c = (sum_y - m * sum_x) / n
    except Exception as e:
        info = {
            'sum_y': sum_y,
            'm': m,
            'sum_x': sum_x,
        }
        print(f'slope error: {e}, info: {info}')
        raise

    # Variance calculation
    y_mean = statistics.mean(y_vals)
    variance = sum((y - (m * x + c)) ** 2 for x, y in zip(x_vals, y_vals)) / n

    return LinearRegressionLine(m, c, variance)


def get_linear_regression_result(nums: List[float], gap: int = 1) -> LinearRegressionLine:
    modified_nums = []
    i = 0
    while i < len(nums):
        modified_nums.append(nums[i])
        i += gap

    if len(modified_nums) == 1 and modified_nums[0] == 1:
        print('if len(modified_nums) == 1 and modified_nums[0] == 1:')
        print(f'nums: {nums}')

    return get_linear_regression_result_util(modified_nums)
