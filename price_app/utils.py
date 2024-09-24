from typing import List

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
