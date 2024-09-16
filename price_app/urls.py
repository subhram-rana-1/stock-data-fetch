from django.urls import path

from price_app.handlers import fetch_price

urlpatterns = [
    path(
        'price/{str:market_name}',
        fetch_price,
        name='fetch-price',
    ),
]
