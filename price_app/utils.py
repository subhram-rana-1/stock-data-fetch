from typing import List

import math

from price_app.constants import ema_smoothing


def calculate_ema(
        input_list: List[float],
        period: int,
) -> List[float]:
    ema_list = []

    # first ema = sma
    sum = 0
    for i in range(period):
        sum += input_list[i]
    ema_list.append(sum / period)

    # calculate rest of all
    smoothing_factor = ema_smoothing / (period + 1)
    i = 1
    while i < len(input_list):
        cur_ema = (smoothing_factor * input_list[i]) + \
                  ((1 - smoothing_factor) * ema_list[i-1])
        ema_list.append(cur_ema)

        i += 1

    return ema_list


def calculate_sma(
        input_list: List[float],
        period: int,
) -> List[float]:
    sma_list = []

    sum = 0
    for i in range(len(input_list)):
        sum += input_list[i]

        if i < (period-1):
            sma_list.append(input_list[i])
        else:
            if i >= period:
                sum -= input_list[i-period]

            sma_list.append(sum / period)

    return sma_list


def get_start_range(num: float, bucket_size: int) -> int:
    return math.floor(num/bucket_size) * bucket_size


def get_bucket_key(start_range: int, end_range: int) -> str:
    return f'{start_range} <-> {end_range}'


# output: {"10-20": [3, cum_occurrence, cum_%age], "20-30": [4, cum_occurrence, cum_%age]}
def get_occurrence_distribution(nums: List[float], grouping_range_width: int) -> dict:
    nums.sort()
    occurrence_distribution = {}

    START_RANGE = get_start_range(nums[0], grouping_range_width)
    END_RANGE = START_RANGE + grouping_range_width

    start_range = START_RANGE
    end_range = END_RANGE

    i = 0
    sum_of_occurrence = 0
    tot_cumulative_occurrence = 0
    while i < len(nums):
        if nums[i] <= end_range:
            sum_of_occurrence += 1
        else:
            key = get_bucket_key(start_range, end_range)
            occurrence_distribution[key] = [sum_of_occurrence]
            tot_cumulative_occurrence += sum_of_occurrence

            start_range = end_range
            end_range = start_range + grouping_range_width

            sum_of_occurrence = 0
            i -= 1

        i += 1

    if sum_of_occurrence != 0:
        occurrence_distribution[get_bucket_key(start_range, end_range)] = [sum_of_occurrence]
        tot_cumulative_occurrence += sum_of_occurrence

    # calculate cumulative percentage
    start_range = START_RANGE
    end_range = END_RANGE
    tot_sum_so_far = 0
    while True:
        key = get_bucket_key(start_range, end_range)
        if key not in occurrence_distribution:
            break

        count = occurrence_distribution[key][0]
        tot_sum_so_far += count

        cur_percentage = round(tot_sum_so_far / tot_cumulative_occurrence * 100)
        occurrence_distribution[key].append(tot_sum_so_far)
        occurrence_distribution[key].append(cur_percentage)

        start_range = end_range
        end_range = start_range + grouping_range_width

    return occurrence_distribution
