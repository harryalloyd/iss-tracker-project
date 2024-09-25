import requests
from datetime import datetime
import smtplib
import time
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(filename='iss_tracker.log', level=logging.INFO)

MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")



MY_LAT = 38.623629
MY_LNG = -121.361672

def is_iss_overhead():
    try:
        response = requests.get(url="http://api.open-notify.org/iss-now.json")
        response.raise_for_status()
        data = response.json()

        iss_latitude = float(data["iss_position"]["latitude"])
        iss_longitude = float(data["iss_position"]["longitude"])

        if MY_LAT - 10 <= iss_latitude <= MY_LAT + 10 and MY_LNG - 10 <= iss_longitude <= MY_LNG + 10:
            return True
    except requests.RequestException as e:
        logging.error(f"Error fetching ISS position: {e}")
    return False

def is_night():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LNG,
        "formatted": 0,
    }

    try:
        response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
        response.raise_for_status()
        data = response.json()

        sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
        sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

        time_now = datetime.now().hour

        if time_now >= sunset or time_now <= sunrise:
            return True
    except requests.RequestException as e:
        logging.error(f"Error fetching sunrise/sunset data: {e}")
    return False

def send_email():
    try:
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=MY_PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=MY_EMAIL,
                # .encode('utf-8') allows me to use emojis so don't remove it
                msg=f"Subject:Look Up! 👆🚀🛰 \n\nThe ISS is right above you!".encode('utf-8')
            )
        logging.info("Email sent successfully.")
    except smtplib.SMTPException as e:
        logging.error(f"Error sending email: {e}")

while True:
    time.sleep(60)  # Run every minute
    if is_iss_overhead() and is_night():
        send_email()
