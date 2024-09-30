from datetime import timedelta, date, time
from backtesting.constants import market_entry_time, market_exit_time
from backtesting.entities import BacktestingInput, BacktestingResult, DailyBacktestingResult, ChartConfig, TradeConfig
from backtesting.enums import BacktestingState, BacktestingStrategy, Market, Direction
from backtesting.models import Backtesting, Trade, DailyBacktesting
from backtesting.momentum_v1.move_catcher import new_move_catcher
from price_app.classes import PriceData, PriceDataPerTick
from price_app.handlers import fetch_price_data
from typing import List


def make_entry(
        daily_backtesting: DailyBacktesting,
        price_list: List[PriceDataPerTick], i: int,
        entry_conditions: str,
) -> Trade:
    return Trade(
        daily_backtesting=daily_backtesting,
        date=daily_backtesting.date,
        expected_direction=daily_backtesting.expected_direction,
        entry_time=price_list[i]['tm'],
        entry_point=price_list[i]['tick_price'],
        entry_conditions=entry_conditions,
        exit_time=None,
        exit_point=None,
        exit_conditions='',
        gain=0,
    )


def make_exit(
        trade: Trade,
        price_list: List[PriceDataPerTick], i: int,
        exit_conditions: str,
) -> Trade:
    trade.exit_time = price_list[i]['tm']
    trade.exit_point = price_list[i]['tick_price']
    trade.exit_conditions = exit_conditions

    return trade


def get_daily_backtest_result(
        daily_backtesting: DailyBacktesting,
        price_data: PriceData,
        direction: Direction,
        trade_config: TradeConfig,
) -> DailyBacktestingResult:
    daily_backtesting_result = DailyBacktestingResult(
        daily_back_testing=daily_backtesting,
        trades=[],
    )

    move_catcher = new_move_catcher(direction)

    price_list = price_data['price_list']
    n = len(price_list)
    i = 0

    while i < n-1:
        # look for entry
        should_make_entry, entry_conditions = move_catcher.should_make_entry(price_list, i, trade_config)
        if should_make_entry:
            trade = make_entry(daily_backtesting, price_list, i, entry_conditions)

            # look for exit
            j = i+1
            while j < n:
                should_exit, exit_conditions = move_catcher.should_exit(trade, price_list, j, trade_config)
                if should_exit or j == n-1:
                    trade = make_exit(trade, price_list, j, exit_conditions)
                    trade = move_catcher.calculate_gain(trade)

                    daily_backtesting_result.trades.append(trade)
                    daily_backtesting_result.daily_back_testing.trade_count += 1
                    if move_catcher.is_winning_trade(trade, trade_config):
                        daily_backtesting_result.daily_back_testing.winning_trade_count += 1
                    else:
                        daily_backtesting_result.daily_back_testing.loosing_trade_count += 1

                    i = j+1
                    break
                else:
                    j += 1
        else:
            i += 1

    daily_backtesting_result.calculate_success_rate()

    return daily_backtesting_result


def get_daily_backtest_result_for_up_and_down(
        day: date,
        start_time: time,
        end_time: time,
        back_testing: Backtesting,
) -> List[DailyBacktestingResult]:
    chart_config = ChartConfig.from_string(back_testing.chart_config)

    price_data: PriceData = fetch_price_data(
        Market(back_testing.market).to_price_app_market_type(),
        day,
        day,
        start_time,
        end_time,
        chart_config.smooth_price_averaging_method,
        chart_config.smooth_price_period,
        chart_config.smooth_price_ema_period,
        chart_config.smooth_slope_averaging_method,
        chart_config.smooth_slope_period,
        chart_config.smooth_slope_ema_period,
    )

    daily_backtest_results = []
    for direction in [Direction.UP, Direction.DOWN]:
        daily_backtesting = DailyBacktesting(
            backtesting=back_testing,
            date=day,
            start_time=start_time,
            end_time=end_time,
            expected_direction=direction,
            trade_count=0,
            winning_trade_count=0,
            loosing_trade_count=0,
            success_rate=None,
        )

        daily_backtest_results.append(
            get_daily_backtest_result(
                daily_backtesting,
                price_data,
                direction,
                TradeConfig.from_string(back_testing.trade_config),
            ))

    return daily_backtest_results


def get_backtest_result(back_test_input: BacktestingInput) -> BacktestingResult:
    back_testing: Backtesting = Backtesting(
        market=back_test_input.market.name,
        strategy=BacktestingStrategy.MOMENTUM_V1.name,
        chart_config=back_test_input.chart_config.to_json(),
        trade_config=back_test_input.trade_config.to_json(),
        purpose=back_test_input.purpose,
        start_date=back_test_input.start_date,
        start_time=back_test_input.start_time,
        end_date=back_test_input.end_date,
        end_time=back_test_input.end_time,
        trade_count=0,
        winning_trade_count=0,
        loosing_trade_count=0,
        success_rate=None,
    )

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

        daily_backtest_result_for_up_and_down = get_daily_backtest_result_for_up_and_down(
            day,
            start_time,
            end_time,
            back_testing,
        )

        for daily_backtest_result in daily_backtest_result_for_up_and_down:
            back_testing_result.back_testing.winning_trade_count += \
                daily_backtest_result.daily_back_testing.winning_trade_count
            back_testing_result.back_testing.loosing_trade_count += \
                daily_backtest_result.daily_back_testing.loosing_trade_count
            back_testing_result.back_testing.trade_count += \
                daily_backtest_result.daily_back_testing.trade_count

        back_testing_result.daily_back_testing_results.\
            extend(daily_backtest_result_for_up_and_down)

        day += timedelta(days=1)

    back_testing_result.back_testing.calculate_success_rate()

    return back_testing_result
