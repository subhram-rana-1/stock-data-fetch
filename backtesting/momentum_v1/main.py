from backtesting.entities import TradeConfig, EntryCondition, BacktestingInput, ChartConfig, ExitCondition, \
    BacktestingResult
from backtesting.enums import Market
from backtesting.momentum_v1 import core
from datetime import time, date


def main():
    back_test_input = BacktestingInput(
        market=Market.NIFTY,
        start_date=date(2024, 10, 1),
        start_time=time(9, 15, 0),
        end_date=date(2024, 10, 1),
        end_time=time(15, 30, 0),
        chart_config=ChartConfig(  # todo
            smooth_price_averaging_method='simple',
            smooth_price_period=20,
            smooth_price_ema_period=20 * 5,
            smooth_slope_averaging_method='simple',
            smooth_slope_period=10,
            smooth_slope_ema_period=10,
        ),
        trade_config=TradeConfig(  # todo
            trend_line_time_period_in_sec=150,
            min_entry_time=time(9, 20),
            entry_conditions=[
                EntryCondition(
                    max_variance=1.1,
                    min_abs_trend_slope=0.25,
                    min_abs_price_slope=1.8,
                    min_abs_price_momentum=0.28,
                ),
                EntryCondition(
                    max_variance=5,
                    min_abs_trend_slope=0.064,
                    min_abs_price_slope=0.4,
                    min_abs_price_momentum=0.15,
                ),
                # todo: add more
            ],
            exit_condition=ExitCondition(
                profit_target_type='fixed',
                profit_target_points=10,
                stoploss_type='fixed',
                stoploss_points=5,
            )
        ),
    )

    backtest_result: BacktestingResult = core.get_backtest_result(back_test_input)

    backtest_result.save_to_db()
