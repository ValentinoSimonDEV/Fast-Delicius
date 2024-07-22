from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Establece el entorno de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FastDelicius.settings')

app = Celery('FastDelicius')

# Usa una cadena para la configuración para que los workers no necesiten serializar la configuración
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubre automáticamente tareas en todos los packages apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Configuración del beat scheduler
app.conf.beat_schedule = {
    'delete-unpaid-orders-every-5-minutes': {
        'task': 'your_app_name.tasks.delete_unpaid_orders',
        'schedule': crontab(minute='*/5'),
    },
}