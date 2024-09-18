import os
from datetime import timedelta
from dotenv import load_dotenv
from celery import Celery
from celery.schedules import crontab
import django
load_dotenv()

celery_app = Celery('config')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


celery_app.conf.broker_url = f"redis://{os.environ['REDIS_HOST']}:6379/2"
celery_app.conf.imports = ["urls.tasks"]
celery_app.conf.result_backend = f"rpc://redis:6379/3"
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.result_expires = timedelta(days=1)
celery_app.conf.task_always_eager = False
celery_app.conf.worker_prefetch_multiplier = 1

celery_app.conf.beat_schedule = {
    'create_ready_to_set_token': {
        'task': 'urls.tasks.create_ready_to_set_token',
        'schedule': crontab(hour=0, minute=5),  # 00:05
    },
}
