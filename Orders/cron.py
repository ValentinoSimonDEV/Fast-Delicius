from django.utils import timezone
from datetime import timedelta
from.models import Order

def delete_unpaid_orders():
    time_limit = timezone.now() - timedelta(hours=1)
    unpaid_orders = Order.objects.filter(payment_state=False, created__lt=time_limit)
    unpaid_orders.delete()