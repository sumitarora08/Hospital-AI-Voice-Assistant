from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from excel_db import save_appointment

from smart_nlp import understand
from calendar_logic import (
    parse_datetime,
    is_working_day,
    is_working_hours,
    slot_available,
    next_free_slot
)

app = Flask(__name__)

LAST_TEXT = ""


def make_gather(step, message, name="", disease="", dt=None):

    date_param = ""
    if dt:
        date_param = dt.strftime('%Y-%m-%d %H:%M')

    gather = Gather(
        input='speech',
        action=f"/process?step={step}&name={name}&disease={disease}&date={date_param}",
        language='en-IN',
        speechTimeout='auto',
        timeout=10,
        actionOnEmptyResult=True,
        bargeIn=True
    )

    gather.say(message)
    return gather



# ===== ENTRY =====
@app.route("/", methods=['GET', 'POST'])
def incoming_call():

    print("New Call Started")

    response = VoiceResponse()

    response.append(
        make_gather(
            1,
            "Welcome to City Hospital. Please tell the patient name."
        )
    )

    return str(response)



@app.route("/process", methods=['POST'])
def process():

    global LAST_TEXT

    step = request.args.get("step", "1")
    text = request.form.get("SpeechResult", "").strip()

    print("STEP:", step, "TEXT:", text)

    response = VoiceResponse()

    if not text:
        response.append(make_gather(step, "Sorry I didn't hear. Please repeat."))
        return str(response)

    if text == LAST_TEXT:
        response.append(make_gather(step, "Please continue."))
        return str(response)

    LAST_TEXT = text



    # ============ STEP 1 : NAME ============
    if step == "1":

        data = understand(text)
        name = data["name"]

        response.append(
            make_gather(
                2,
                f"Thank you {name}. Please tell the disease.",
                name=name
            )
        )

        return str(response)



    # ============ STEP 2 : DISEASE ============
    if step == "2":

        name = request.args.get("name")

        data = understand(text)
        disease = data["disease"]

        response.append(
            make_gather(
                3,
                "Please tell appointment date and time.",
                name=name,
                disease=disease
            )
        )

        return str(response)



    # ============ STEP 3 : DATE & TIME ============
    if step == "3":

        name = request.args.get("name")
        disease = request.args.get("disease")

        data = understand(text)
        time_text = data["time"]

        # ----- DATE PERSIST FIX -----
        new_dt = parse_datetime(time_text)
        prev_date = request.args.get("date")

        if prev_date and new_dt:
            # If user said only time
            if not any(w in time_text.lower() for w in [
                "jan","feb","mar","apr","may","jun",
                "jul","aug","sep","oct","nov","dec",
                "today","tomorrow","monday","tuesday",
                "wednesday","thursday","friday"
            ]):

                old = parse_datetime(prev_date)

                dt = old.replace(
                    hour=new_dt.hour,
                    minute=new_dt.minute
                )
            else:
                dt = new_dt
        else:
            dt = new_dt
        # -----------------------------


        if not dt:
            response.append(
                make_gather(
                    3,
                    "I could not understand the date and time. Please repeat.",
                    name, disease
                )
            )
            return str(response)


        if not is_working_day(dt):
            response.append(
                make_gather(
                    3,
                    "Hospital works Monday to Friday only. Please tell another date and time.",
                    name, disease, dt
                )
            )
            return str(response)


        if not is_working_hours(dt):
            response.append(
                make_gather(
                    3,
                    "Selected time is outside hospital hours. Please choose another slot between 9 AM and 6 PM.",
                    name, disease, dt
                )
            )
            return str(response)


        if not slot_available(dt):

            new = next_free_slot(dt)

            response.append(
                make_gather(
                    3,
                    f"This slot is already booked. Next available slot is {new.strftime('%I:%M %p on %d %B')}. Please say another preferred time.",
                    name, disease, new
                )
            )
            return str(response)


        # ---- SAVE SUCCESS ----
        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%I:%M %p")

        ok= save_appointment(name, disease, time_str, date_str)
        if not ok:
           response.say(
            "System is busy saving records. "
            "Please try again in a minute." )
           return str(response)

        response.say(
            f"Appointment confirmed for {name} "
            f"regarding {disease} on {dt.strftime('%d %B')} "
            f"at {time_str}. Thank you."
        )

        return str(response)


    return str(response)



if __name__ == "__main__":
    print("APP FILE STARTING...")
    app.run(debug=True)
