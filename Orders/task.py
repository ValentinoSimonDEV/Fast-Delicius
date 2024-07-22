from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Order

@shared_task
def delete_unpaid_orders():
    time_limit = timezone.now() - timedelta(minutes=5)
    unpaid_orders = Order.objects.filter(payment_state=False, created__lt=time_limit)
    unpaid_orders.delete()