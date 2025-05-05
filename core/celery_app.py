
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
import ssl

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core', broker_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_NONE
     },
     redis_backend_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_NONE
     })


app.conf.update(broker_url=os.environ['REDIS_URL'],
                result_backend=os.environ['REDIS_URL'],
                concurrency=2,
                broker_connection_retry=True,
                broker_connection_retry_on_startup=True)

app.autodiscover_tasks()


