import json

from django import http
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from backtesting.models import Backtesting


@csrf_exempt
@require_POST
def delete_back_testing_data(request: http.HttpRequest) -> JsonResponse:
    body_dict = json.loads(request.body)

    print(f"deleting backtestings: {body_dict['backtesting_ids']}")

    for backtesting_id in body_dict['backtesting_ids']:
        try:
            backtesting = Backtesting.objects.get(pk=backtesting_id)
        except Backtesting.DoesNotExist:
            pass
        else:
            backtesting.delete()

    return JsonResponse({})
