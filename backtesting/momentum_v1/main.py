from backtesting.entities import TradeConfig, EntryCondition, BacktestingInput
from backtesting.enums import Market
from backtesting.momentum_v1.core import get_backtest_result
from datetime import time, date


def main():
    back_test_input = BacktestingInput(
        market=Market.NIFTY,
        start_date=date(2024, 9, 27),
        start_time=time(9, 15, 0),
        end_date=date(2024, 9, 27),
        end_time=time(15, 30, 0),
        trade_config=TradeConfig(  # todo
            trend_line_time_period_in_sec=120,
            entry_conditions=[
                EntryCondition(),
                EntryCondition(),
                EntryCondition(),
            ]
        ),
    )

    backtest_result = get_backtest_result(back_test_input)

    backtest_result.save_to_db()
