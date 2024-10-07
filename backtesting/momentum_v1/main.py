from backtesting.entities import TradeConfig, EntryCondition, BacktestingInput, ChartConfig, ExitCondition, \
    BacktestingResult
from backtesting.enums import Market
from backtesting.momentum_v1 import core
from datetime import time, date


def main():
    back_test_input = BacktestingInput(
        market=Market.NIFTY,
        start_date=date(2024, 9, 24),
        start_time=time(9, 15, 0),
        end_date=date(2024, 9, 24),
        end_time=time(14, 45, 0),
        chart_config=ChartConfig(  # todo
            smooth_price_averaging_method='simple',
            smooth_price_period=20,
            smooth_price_ema_period=95,
            smooth_slope_averaging_method='simple',
            smooth_slope_period=10,
            smooth_slope_ema_period=40,
        ),
        trade_config=TradeConfig(
            trend_line_time_period_in_sec=140,
            min_entry_time=time(9, 20),
            entry_conditions=[
                EntryCondition(
                    max_variance=6,
                    min_abs_trend_slope=0.3,
                    min_abs_price_slope=6,
                    min_abs_price_momentum=1.4,
                ),
                EntryCondition(
                    max_variance=3,
                    min_abs_trend_slope=0.35,
                    min_abs_price_slope=6.3,
                    min_abs_price_momentum=1.73,
                ),
                EntryCondition(
                    max_variance=9.5,
                    min_abs_trend_slope=0.025,
                    min_abs_price_slope=13.8,
                    min_abs_price_momentum=3.989,
                ),
                EntryCondition(
                    max_variance=4,
                    min_abs_trend_slope=0.525,
                    min_abs_price_slope=30,
                    min_abs_price_momentum=2.56,
                ),
            ],
            exit_condition=ExitCondition(
                profit_target_type='fixed',
                profit_target_points=5,
                stoploss_type='fixed',
                stoploss_points=17,
            )
        ),
    )

    backtest_result: BacktestingResult = core.get_backtest_result(back_test_input)

    backtest_result.save_to_db()
