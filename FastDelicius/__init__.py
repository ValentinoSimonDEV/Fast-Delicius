from __future__ import absolute_import, unicode_literals

# Esto hará que `celery` sea una parte de tu proyecto Django
from .celery import app as celery_app

__all__ = ('celery_app',)
