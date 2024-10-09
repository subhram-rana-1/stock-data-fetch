from datetime import date, time, timedelta
from typing import List
from backtesting.constants import market_entry_time, market_exit_time
from backtesting.entities import BacktestingInput, BacktestingResult, DailyBacktestingResult, ChartConfig, TradeConfig
from backtesting.enums import BacktestingStrategy, Market, Direction
from backtesting.models import Backtesting, DailyBacktesting, Trade
from backtesting.momentum_1min_candle.move_catcher import new_move_catcher, IMoveCatcher
from backtesting.momentum_1min_candle.upstox import fetch_candlestick_data_from_upstox, UpstoxCandlestickResponse
from price_app.classes import PriceData, PriceDataPerTick, calculate_other_auxiliary_prices, PriceDataPerCandle
from stock_data_fetch.enums import MarketType


def make_entry(
        daily_backtesting: DailyBacktesting,
        price_list: List[PriceDataPerCandle], i: int,
        entry_conditions: str,
) -> Trade:
    return Trade(
        daily_backtesting=daily_backtesting,
        date=daily_backtesting.date,
        expected_direction=daily_backtesting.expected_direction,
        entry_time=price_list[i]['tm'],
        entry_point=price_list[i]['open'],
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
        move_catcher: IMoveCatcher,
        trade_config: TradeConfig,
) -> Trade:
    trade.exit_time = price_list[i]['tm']
    trade.exit_conditions = exit_conditions
    trade.exit_point = move_catcher.get_exit_point(
        trade,
        trade_config,
    )

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

    move_catcher: IMoveCatcher = new_move_catcher(direction)

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
                    trade = make_exit(trade, price_list, j, exit_conditions,
                                      move_catcher, trade_config)
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


def fetch_and_transform_candlestick_price_data(
        market_type: MarketType,
        from_date: date,
        to_date: date,
        from_time: time,
        to_time: time,

        smooth_price_averaging_method: str,
        smooth_price_period: int,
        smooth_price_ema_period: int,
        smooth_slope_averaging_method: str,
        smooth_slope_period: int,
        smooth_slope_ema_period: int,
        smooth_momentum_period: int = None,
        smooth_momentum_ema_period: int = None,
) -> PriceData:
    candlestick_resp: UpstoxCandlestickResponse = fetch_candlestick_data_from_upstox(
        market_type,
        from_date,
        to_date
    )

    price_data = PriceData(
        market_name=market_type,
        price_list=[candle.to_tick_by_tick_type_data() for candle in candlestick_resp.data.candles],
    )

    calculate_other_auxiliary_prices(
        price_data,
        smooth_price_averaging_method,
        smooth_price_period,
        smooth_price_ema_period,
        smooth_slope_averaging_method,
        smooth_slope_period,
        smooth_slope_ema_period,
        smooth_momentum_period,
        smooth_momentum_ema_period,
    )

    return price_data


def get_daily_backtest_result_for_up_and_down(
        day: date,
        start_time: time,
        end_time: time,
        back_testing: Backtesting,
) -> List[DailyBacktestingResult]:
    chart_config = ChartConfig.from_string(back_testing.chart_config)

    price_data: PriceData = fetch_and_transform_candlestick_price_data(
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
            expected_direction=direction.name,
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
        strategy=BacktestingStrategy.ONE_MINUTE_CANDLESTICK_MOMENTUM.name,
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
