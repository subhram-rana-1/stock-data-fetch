-- To know the summary of recent testing
select id from backtesting order by id limit 1;

-- To know the daily backtesting summary of the recent backtesting
select * from daily_backtesting where backtesting_id =  (select id from backtesting order by id limit 1)

-- To know the trades of recent backtesting
select trade.date,
       trade.expected_direction,
       trade.entry_time,
       trade.exit_time,
       trade.entry_point,
       trade.exit_point,
       trade.gain
from trade
    join daily_backtesting on trade.daily_backtesting_id=daily_backtesting.id
    join backtesting on backtesting.id=daily_backtesting.backtesting_id
where backtesting.id=(select id from backtesting order by id limit 1)
order by trade.id;