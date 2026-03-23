from celery import Celery
from celery.signals import worker_ready

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["tasks"]
)

celery_app.conf.task_routes = {
    "tasks.update_portfolio": {"queue": "portfolio"},
    "tasks.update_stock_product_recommendation": {"queue": "recommend"},
}


celery_app.conf.beat_schedule = {
    "run-every-600-minutes": {
        "task": "tasks.update_realtime_price",
        "schedule": 60 * 600, 
        "options": {"queue": "realtime_price"},
    },
}

@worker_ready.connect
def at_start(sender, **kwargs):
    print("trigger update_realtime_price")

    from tasks import update_realtime_price
    update_realtime_price.apply_async(queue="realtime_price")

