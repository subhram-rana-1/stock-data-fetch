from django.db import models


class NiftyPrice(models.Model):
    date = models.DateField(null=False)
    timestamp = models.TimeField(null=False)
    price = models.FloatField(null=False)

    class Meta:
        db_table = 'nifty_price'

    def __str__(self):
        return f"Date: {self.date}, Timestamp: {self.timestamp}, Price: {self.price}"


class BankNiftyPrice(models.Model):
    date = models.DateField(null=False)
    timestamp = models.DateTimeField(null=False)
    price = models.FloatField(null=False)

    class Meta:
        db_table = 'bank_nifty_price'

    def __str__(self):
        return f"Date: {self.date}, Timestamp: {self.timestamp}, Price: {self.price}"
