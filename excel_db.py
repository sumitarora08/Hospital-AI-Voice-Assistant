import pandas as pd
import os

FILE = "appointments_main.xlsx"


def save_appointment(name, disease, time, date):

    data = {
        "Name": name,
        "Disease": disease,
        "Date": date,
        "Time": time
    }

    # ---- If file exists → append ----
    if os.path.exists(FILE):
        df = pd.read_excel(FILE)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

    # ---- If first time → create ----
    else:
        df = pd.DataFrame([data])

    df.to_excel(FILE, index=False)
