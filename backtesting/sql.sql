-- To know the summary of recent testing
select success_rate from backtesting order by id desc limit 1;

-- To know the daily backtesting summary of the recent backtesting
select * from daily_backtesting where backtesting_id =  (select id from backtesting order by id desc limit 1);

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
where backtesting.id=(select id from backtesting order by id desc limit 1)
order by trade.id;

-- To know the total gain recent backtesting
select sum(trade.gain)
from trade
    join daily_backtesting on trade.daily_backtesting_id=daily_backtesting.id
    join backtesting on backtesting.id=daily_backtesting.backtesting_id
where backtesting.id=(select id from backtesting order by id desc limit 1)
order by trade.id;


-- If migration deleted manually from DB, then use the following query
insert into django_migrations
    (id, app, name, applied)
values
    (35, 'price_app', '0001_initial', '2024-10-01 04:30:27.709948');

