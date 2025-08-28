from django.utils import timezone
from datetime import datetime, timedelta
from .models import GameDashBoard, GameRecords
import os
import logging

logger = logging.getLogger(__name__)

def delete_file():
    try:
        now = timezone.now()
        two_days_ago = now - timedelta(days=2)
        GameDashBoard.objects.filter(date__lte=two_days_ago.date()).delete()
        GameRecords.objects.filter(date__lte=two_days_ago.date()).delete()
        logger.info("Old records deleted successfully. date: %s", two_days_ago.date())
    except Exception as e:
        logger.error("Error deleting file: %s", e)