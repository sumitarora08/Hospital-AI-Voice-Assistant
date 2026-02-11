from datetime import datetime, timedelta
import pandas as pd
import os
import dateparser

FILE = "appointments_main.xlsx"

HOSPITAL_START = 9
HOSPITAL_END = 18
GAP = 30   # 30 minutes


def parse_datetime(text):

    return dateparser.parse(
        text,
        settings={'PREFER_DATES_FROM': 'future'}
    )


def is_working_day(dt):
    # Monday=0 ... Sunday=6
    return dt.weekday() < 5


def is_working_hours(dt):
    return HOSPITAL_START <= dt.hour < HOSPITAL_END


def slot_available(dt):

    if not os.path.exists(FILE):
        return True

    df = pd.read_excel(FILE)

    date = dt.strftime("%Y-%m-%d")
    time = dt.strftime("%I:%M %p")

    for _, row in df.iterrows():

        if str(row["Date"]) == date and str(row["Time"]) == time:
            return False

    return True


def next_free_slot(dt):

    while True:

        # working day check
        if not is_working_day(dt):
            dt += timedelta(days=1)
            dt = dt.replace(hour=HOSPITAL_START, minute=0)
            continue

        # working hours check
        if dt.hour < HOSPITAL_START:
            dt = dt.replace(hour=HOSPITAL_START, minute=0)

        if dt.hour >= HOSPITAL_END:
            dt = dt + timedelta(days=1)
            dt = dt.replace(hour=HOSPITAL_START, minute=0)

        # round to 30 min
        minute = (dt.minute // GAP) * GAP
        dt = dt.replace(minute=minute)

        if slot_available(dt):
            return dt

        dt += timedelta(minutes=GAP)
