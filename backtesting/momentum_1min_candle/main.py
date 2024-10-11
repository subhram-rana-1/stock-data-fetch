from backtesting.entities import TradeConfig, EntryCondition, BacktestingInput, ChartConfig, ExitCondition, \
    BacktestingResult
from backtesting.enums import Market
from backtesting.momentum_1min_candle import core
from datetime import time, date, datetime


def main():
    back_test_input = BacktestingInput(
        market=Market.NIFTY,
        start_date=date(2024, 5, 1),
        start_time=time(9, 15, 0),
        end_date=date(2024, 9, 30),
        end_time=time(14, 45, 0),
        chart_config=ChartConfig(  # todo
            smooth_price_averaging_method='simple',
            smooth_price_period=11,
            smooth_price_ema_period=20,
            smooth_slope_averaging_method='simple',
            smooth_slope_period=35,
            smooth_slope_ema_period=45,
        ),
        trade_config=TradeConfig(
            trend_line_time_period=120,
            min_entry_time=time(9, 48),
            entry_conditions=[
                EntryCondition(
                    max_variance=6.5,
                    min_abs_trend_slope=0.175,
                    min_abs_price_slope=24.7,
                    min_abs_price_momentum=5.37,
                ),
                EntryCondition(
                    max_variance=4.5,
                    min_abs_trend_slope=0.35,
                    min_abs_price_slope=5.2,
                    min_abs_price_momentum=2.69,
                ),
                EntryCondition(
                    max_variance=0.5,
                    min_abs_trend_slope=0.55,
                    min_abs_price_slope=1.9,
                    min_abs_price_momentum=0.129,
                ),
                EntryCondition(
                    max_variance=8.5,
                    min_abs_trend_slope=0.1,
                    min_abs_price_slope=3.1,
                    min_abs_price_momentum=1.67,
                ),
            ],
            exit_condition=ExitCondition(
                profit_target_type='fixed',
                profit_target_points=20,
                stoploss_type='fixed',
                stoploss_points=10,
            )
        ),
    )

    t1 = datetime.now()

    backtest_result: BacktestingResult = core.get_backtest_result(back_test_input)
    t2 = datetime.now()
    print(f'without caching took: {t2-t1} seconds')

    backtest_result: BacktestingResult = core.get_backtest_result(back_test_input)
    t3 = datetime.now()
    print(f'with caching took: {t3-t2} seconds')

    backtest_result.save_to_db()
