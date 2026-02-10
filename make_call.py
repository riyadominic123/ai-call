import os
from twilio.rest import Client
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, YOUR_PHONE_NUMBER, NGROK_URL

def make_call():
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, YOUR_PHONE_NUMBER, NGROK_URL]):
        print("Error: Missing configuration. Please check your .env file.")
        return

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    try:
        call = client.calls.create(
            to=YOUR_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            url=f"{NGROK_URL}/twilio_voice"
        )
        print(f"Call initiated! SID: {call.sid}")
    except Exception as e:
        print(f"Failed to initiate call: {e}")

if __name__ == "__main__":
    make_call()
