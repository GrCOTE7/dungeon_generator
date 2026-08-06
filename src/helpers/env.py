from datetime import datetime as dt


def curr_time():
    now = dt.now()
    return f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"

def custom_invite():
    now = dt.now()
    return f"[{now.hour:02d}:{now.minute:02d}:{now.second:02d}] > "