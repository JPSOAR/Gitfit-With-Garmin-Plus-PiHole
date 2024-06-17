import os
import json
from datetime import date
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)
from dotenv import load_dotenv
from garth.exc import GarthHTTPError
import requests


#initialize connection to garmin connect see https://github.com/cyberjunky/python-garminconnect
#for full example
def init_api(email, password, tokenstore):
    """Initialize Garmin API with your credentials."""

    #tokenstore_base64 = f"{tokenstore}_base64"
    #print(tokenstore_base64)

    try:
        # Using Oauth1 and OAuth2 token files from directory
        print(
            f"Trying to login to Garmin Connect using token data from directory '{tokenstore}'...\n"
        )

        garmin = Garmin()
        garmin.login(tokenstore)

    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        # Session is expired. You'll need to log in again
        print(
            "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
            f"They will be stored in '{tokenstore}' for future use.\n"
        )
        try:
            garmin = Garmin(email=email, password=password, is_cn=False)
            garmin.login()
            # Save Oauth1 and Oauth2 token files to directory for next login
            garmin.garth.dump(tokenstore)
            print(
                f"Oauth tokens stored in '{tokenstore}' directory for future use. (first method)\n"
            )
        except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError, requests.exceptions.HTTPError) as err:
            return None
    return garmin


#Load environment variables containing creds
#Create a .env file in the root of this project to accomplish this
load_dotenv()
g_email = os.getenv("GARMIN_EMAIL")
g_password = os.getenv("GARMIN_PW")
tokenstore = os.getenv("GARMIN_CRED_PATH")
PIHOLE_API_TOKEN = os.getenv("PIHOLE_API_TOKEN")
#Create connection to garmin using credentials
garmin_client = init_api(g_email,g_password,tokenstore)

#Get date to pass to garmin
today = date.today()
#Query Garmin API to get today's tats
stats = garmin_client.get_stats(today.isoformat())
#Obtain just the total steps and active calories
steps = stats['totalSteps']
activeCalories = stats['activeKilocalories']

print(f"Steps: {steps}")
print(f"Active Calories: {activeCalories}")


if steps < 1000 and activeCalories < 600:
    print("Goal not met, block streaming URLS in PiHole!")

    pihole_url = "http://pi.hole/admin/api.php"

    params = {
        "list" : "black",
        "add" : "netflix.com",
        "auth" : PIHOLE_API_TOKEN
    }

    res = requests.get(url=pihole_url,params=params)
    print(res.json())

else:
    print("Nice job meeting your fitness goal today, enjoy your streaming!")

    pihole_url = "http://pi.hole/admin/api.php"

    params = {
        "list" : "black",
        "sub" : "netflix.com",
        "auth" : PIHOLE_API_TOKEN
    }
    res = requests.get(url=pihole_url,params=params)
    print(res.json())