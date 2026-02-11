from twilio.rest import Client
from config import TWILIO_SID, TWILIO_TOKEN, TWILIO_NUMBER, YOUR_NUMBER

client = Client(TWILIO_SID, TWILIO_TOKEN)

call = client.calls.create(
    to=YOUR_NUMBER,
    from_=TWILIO_NUMBER,
    url="https://subinferior-edyth-unbitten.ngrok-free.dev"
)

print("Call initiated:", call.sid)

