from backtesting.entities import TradeConfig, EntryCondition, BacktestingInput, ChartConfig
from backtesting.enums import Market
from backtesting.momentum_v1 import core
from datetime import time, date


def main():
    back_test_input = BacktestingInput(
        market=Market.NIFTY,
        start_date=date(2024, 9, 27),
        start_time=time(9, 15, 0),
        end_date=date(2024, 9, 27),
        end_time=time(15, 30, 0),
        chart_config=ChartConfig(
            smooth_price_averaging_method=,
            smooth_price_period=,
            smooth_price_ema_period=,
            smooth_slope_averaging_method=,
            smooth_slope_period=,
            smooth_slope_ema_period=,
        ),  # todo
        trade_config=TradeConfig(  # todo
            trend_line_time_period_in_sec=120,
            entry_conditions=[
                EntryCondition(),
                EntryCondition(),
                EntryCondition(),
            ]
        ),
    )

    backtest_result = core.get_backtest_result(back_test_input)

    backtest_result.save_to_db()
