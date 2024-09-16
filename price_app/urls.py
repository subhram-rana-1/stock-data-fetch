from django.urls import path

from price_app.handlers import fetch_price

urlpatterns = [
    path(
        'price',
        fetch_price,
        name='fetch-price',
    ),
]
