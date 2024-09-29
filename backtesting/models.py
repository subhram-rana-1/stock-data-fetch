import json
from django.db import models
from django_mysql.models import EnumField
from backtesting.enums import BacktestingStrategy
from typing import List


class Backtesting(models.Model):
    strategy = EnumField(choices=BacktestingStrategy.choices(), null=False)
    config = models.TextField(
        null=False,
        max_length=10000,
    )
    purpose = models.TextField(null=True, max_length=10000)
    date = models.DateField(null=False)
    start_time = models.TimeField(null=False)
    time_taken = models.DecimalField(null=False, decimal_places=2, max_digits=10)  # in seconds
    success_rate = models.DecimalField(null=False, decimal_places=2, max_digits=10)

    class Meta:
        db_table = 'backtesting'


class Trade(models.Model):
    backtesting = models.ForeignKey(
        Backtesting, on_delete=models.CASCADE,
        related_name='trades', related_query_name='trade',
        null=False,
    )
    date = models.DateField(null=False)
    entry_time = models.TimeField(null=False)
    entry_point = models.DecimalField(null=False, decimal_places=2, max_digits=10)
    entry_conditions = models.TextField(null=False, max_length=10000)
    exit_time = models.TimeField(null=False)
    exit_point = models.DecimalField(null=False, decimal_places=2, max_digits=10)
    exit_conditions = models.TextField(null=False, max_length=10000)
    gain = models.DecimalField(null=False, decimal_places=2, max_digits=10)

    class Meta:
        db_table = 'trade'


class EntryCondition:
    def to_dict(self) -> dict:
        ...

    @classmethod
    def from_dict(cls, my_dict: dict):
        return EntryCondition()


class TradeConfig:
    def __init__(
            self,
            trend_line_time_period_in_sec: int,
            entry_conditions: List[EntryCondition],
    ):
        self.trend_line_time_period_in_sec = trend_line_time_period_in_sec
        self.entry_conditions = entry_conditions

    def to_dict(self):
        return {
            'trend_line_time_period_in_sec': self.trend_line_time_period_in_sec,
            'entry_conditions': [
                entry_condition.to_dict()
                for entry_condition in self.entry_conditions
            ]
        }

    @classmethod
    def from_dict(cls, my_dict: dict):
        return TradeConfig(
            my_dict['trend_line_time_period_in_sec'],
            [EntryCondition.from_dict(entry_condition)
             for entry_condition in my_dict['entry_conditions']],
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_string(meta: str):
        return TradeConfig.from_dict(json.loads(meta))
