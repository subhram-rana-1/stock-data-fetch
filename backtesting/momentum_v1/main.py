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
            smooth_price_period=30,
            smooth_price_ema_period=150,
            smooth_slope_averaging_method='simple',
            smooth_slope_period=10,
            smooth_slope_ema_period=10,
        ),
        trade_config=TradeConfig(
            trend_line_time_period=150,
            min_entry_time=time(9, 48),
            entry_conditions=[
                EntryCondition(
                    max_variance=12,
                    min_abs_trend_slope=0.14,
                    min_abs_price_slope=0.6,
                    min_abs_price_momentum=0.42,
                ),
                # EntryCondition(
                #     max_variance=5.5,
                #     min_abs_trend_slope=0.074,
                #     min_abs_price_slope=14.7,
                #     min_abs_price_momentum=7.9,
                # ),
                # EntryCondition(
                #     max_variance=6.5,
                #     min_abs_trend_slope=0.09,
                #     min_abs_price_slope=15.8,
                #     min_abs_price_momentum=9.12,
                # ),
                # EntryCondition(
                #     max_variance=8,
                #     min_abs_trend_slope=0.024,
                #     min_abs_price_slope=23.6,
                #     min_abs_price_momentum=8.66,
                # ),
            ],
            exit_condition=ExitCondition(
                profit_target_type='fixed',
                profit_target_points=5,
                stoploss_type='fixed',
                stoploss_points=5,
            )
        ),
    )

    backtest_result: BacktestingResult = core.get_backtest_result(back_test_input)

    backtest_result.save_to_db()
