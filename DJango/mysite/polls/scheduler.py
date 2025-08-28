# polls/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import delete_file


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_file, "cron", hour=23, minute=0)
    scheduler.start()