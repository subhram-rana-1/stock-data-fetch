from django.db import models
from django_mysql.models import EnumField
from backtesting.enums import BacktestingStrategy, BacktestingState, Direction, Market


class Backtesting(models.Model):
    market = EnumField(choices=Market.choices(), null=False)
    strategy = EnumField(choices=BacktestingStrategy.choices(), null=False)
    chart_config = models.TextField(
        null=False,
        max_length=10000,
    )
    trade_config = models.TextField(
        null=False,
        max_length=10000,
    )
    purpose = models.TextField(null=True, max_length=10000)
    start_date = models.DateField(null=False)
    start_time = models.TimeField(null=False)
    end_date = models.DateField(null=False)
    end_time = models.TimeField(null=False)

    trade_count = models.IntegerField(null=True)
    winning_trade_count = models.IntegerField(null=True)
    loosing_trade_count = models.IntegerField(null=True)
    success_rate = models.DecimalField(null=True, decimal_places=2, max_digits=10)

    class Meta:
        db_table = 'backtesting'

    def update_state(self, state: BacktestingState):
        self.state = state.name
        self.save()

    def mark_processing(self):
        self.update_state(BacktestingState.PROCESSING)

    def mark_completed(self):
        self.update_state(BacktestingState.COMPLETED)

    def calculate_success_rate(self):
        self.success_rate = round(int(self.winning_trade_count) / int(self.trade_count) * 100, 2)


class DailyBacktesting(models.Model):
    backtesting = models.ForeignKey(
        Backtesting, on_delete=models.CASCADE,
        related_name='daily_backtestings', related_query_name='daily_backtesting',
        null=False,
    )
    date = models.DateField(null=False)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)
    expected_direction = EnumField(choices=Direction.choices(), null=False)
    trade_count = models.IntegerField(null=False)
    winning_trade_count = models.IntegerField(null=False)
    loosing_trade_count = models.IntegerField(null=False)
    success_rate = models.DecimalField(null=False, decimal_places=2, max_digits=10)

    def calculate_success_rate(self):
        if int(self.trade_count) == 0:
            raise Exception("CODE BUG: DailyBacktesting.trade_count is ZERO. can't calculate success rate")

        self.success_rate = round((int(self.winning_trade_count) / int(self.trade_count)) * 100, 2)

    class Meta:
        db_table = 'daily_backtesting'


class Trade(models.Model):
    daily_backtesting = models.ForeignKey(
        DailyBacktesting, on_delete=models.CASCADE,
        related_name='trades', related_query_name='trade',
        null=False,
    )
    date = models.DateField(null=False)
    expected_direction = EnumField(choices=Direction.choices(), null=False)
    entry_time = models.TimeField(null=False)
    entry_point = models.DecimalField(null=False, decimal_places=2, max_digits=10)
    entry_conditions = models.TextField(null=False, max_length=10000)
    exit_time = models.TimeField(null=False)
    exit_point = models.DecimalField(null=False, decimal_places=2, max_digits=10)
    exit_conditions = models.TextField(null=False, max_length=10000)
    gain = models.DecimalField(null=False, decimal_places=2, max_digits=10)

    class Meta:
        db_table = 'trade'
