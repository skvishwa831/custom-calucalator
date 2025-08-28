from datetime import datetime, timedelta, time

def get_adjusted_date():
    now = datetime.now()
    cutoff_time = time(11, 0)  # ⏰ Cutoff is now 11:00 AM

    if now.time() < cutoff_time:
        adjusted_date = (now - timedelta(days=1)).date()
    else:
        adjusted_date = now.date()
    return adjusted_date