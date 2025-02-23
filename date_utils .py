from datetime import datetime
import pytz

def get_current_ist_time():
    """Returns the current time in IST format as a string."""
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
