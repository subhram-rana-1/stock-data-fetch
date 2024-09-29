from datetime import timedelta
from backtesting.constants import market_entry_time, market_exit_time
from backtesting.entities import BacktestingInput, BacktestingResult, DailyBacktestingResult
from backtesting.enums import BacktestingState, BacktestingStrategy
from backtesting.models import Backtesting


# todo
def get_daily_backtest_result() -> DailyBacktestingResult:
    ...


def get_backtest_result(back_test_input: BacktestingInput) -> BacktestingResult:
    back_testing: Backtesting = Backtesting(
        market=back_test_input.market,
        strategy=BacktestingStrategy.MOMENTUM_V1.name,
        chart_config=back_test_input.chart_config.to_json(),
        trade_config=back_test_input.trade_config.to_json(),
        purpose=back_test_input.purpose,
        start_date=back_test_input.start_date,
        start_time=back_test_input.start_time,
        end_date=back_test_input.end_date,
        end_time=back_test_input.end_time,
        state=BacktestingState.INITIATED.name,
    )

    back_testing.save()

    print(f'backtesting initiated: {back_testing.__str__()}')

    back_testing_result = BacktestingResult(
        back_testing=back_testing,
        daily_back_testing_results=[],
    )

    global_start_date = back_test_input.start_date
    global_start_time = back_test_input.start_time
    global_end_date = back_test_input.end_date
    global_end_time = back_test_input.end_time


    day = global_start_date
    while day <= global_end_date:
        start_time = global_start_time if day == global_start_date else market_entry_time
        end_time = global_end_time if day == global_end_date else market_exit_time

        print(f'daily backtesting initiated for {day}, start time: {start_time}, end time: {end_time}')

        daily_backtest_result = get_daily_backtest_result()
        back_testing_result.daily_back_testing_results.append(daily_backtest_result)

        day += timedelta(days=1)

    return back_testing_result
