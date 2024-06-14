import os
import json
import requests
from garminconnect import (
    Garmin,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
    GarminConnectAuthenticationError,
)
from dotenv import load_dotenv
from datetime import date,datetime
from pathlib import Path
from garth.exc import GarthHTTPError
import time



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
            # Encode Oauth1 and Oauth2 tokens to base64 string and safe to file for next login (alternative way)
            #token_base64 = garmin.garth.dumps()
            #dir_path = os.path.expanduser(tokenstore_base64)
            ##with open(dir_path, "w") as token_file:
            #    token_file.write(token_base64)
            #print(
            #    f"Oauth tokens encoded as base64 string and saved to '{dir_path}' file for future use. (second method)\n"
            #)
        except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError, requests.exceptions.HTTPError) as err:
            return None

    return garmin

def get_garmin_data(client):

    today = date.today()
    """
    Get activity data
    """
    print("client.get_stats(%s)", today.isoformat())
    print("----------------------------------------------------------------------------------------")
    try:
        stats = client.get_stats(today.isoformat())
        with open("./data/current_stats.json", "w") as json_file:
            json.dump(stats,json_file,indent=4)
        return stats
        #steps = stats['totalSteps']
        #activeCalories = stats['activeKilocalories']
        #return({"steps":steps, "activeCalories":activeCalories})
        #print("Jim's Steps: {}".format(jim_steps))
        
    except (
        GarminConnectConnectionError,
        GarminConnectAuthenticationError,
        GarminConnectTooManyRequestsError,
    ) as err:
        print("Error occurred during Garmin Connect Client get stats: %s" % err)
        quit()
    except Exception as e:  # pylint: disable=broad-except
        print(f"Unknown error occurred during Garmin Connect Client get stats: {e}")
        quit()


def update_pihole(action: str, domain_block_list: list):
    pihole_hostname = os.getenv("PIHOLE_HOST")
    pihole_api_token = os.getenv("PIHOLE_API_TOKEN")
    pi_url = f"http://{pihole_hostname}/admin/api.php"
    print(f"Targeting Pi-Hole API using {pi_url}")

    for domain in domain_block_list:
        if domain[1] == 'exact':
            list_type = "black"
        elif domain[1] == "regex":
            list_type = "regex_black"
        else:
            raise ValueError("Unexpected value passed to update_pihole function")
        params = {
            "list" : list_type,
            action : domain[0],
            "auth" : pihole_api_token
        }
        res = requests.get(url=pi_url,params=params)
        if res.status_code == 200:
            if res.json().get("success") == True:
                if action == "add":
                    print(f"Successfully added {domain[0]} to Pi-Hole blocklist")
                elif action == "sub":
                    print(f"Successfully removed {domain[0]} from Pi-Hole blocklist")
                else:
                    print("Unexpected action passed to update_pihole function")
            else:
                print(f"Successfully communicated with Pi-Hole Server but did not get a success message back for domain: {domain}")
                print(res.text)
        else:
            print(f"invalid response from Pi-Hole Server")
            print(res.text)


def get_block_list(bl_path):
    raw_list = [line for line in Path(bl_path).read_text().split("\n") if line]
    final_list = []
    for item in raw_list:
        final_list.append(item.split(" "))
        if len(final_list[-1]) != 2:
            print(f"bad value: {final_list[-1]}")
            raise ValueError("Each line in blocklist must have the domain and filter type separted by a single space")
        if final_list[-1][1] != "exact" and final_list[-1][1] != "regex":
            print(final_list[-1][1])
            raise ValueError("The second item on each line of the blocklist must be either exact or regex")
        
    
    print("Domains to Block/Allow:")
    for domain in final_list:
        print(domain)
    return final_list

def main():
    load_dotenv()

    g_email = os.getenv("GARMIN_EMAIL")
    g_password = os.getenv("GARMIN_PW")
    step_goal = int(os.getenv("DAILY_STEP_GOAL"))
    print(f"Daily Step Goal Set to: {step_goal} steps")
    cal_goal = int(os.getenv("DAILY_CALORIE_GOAL"))
    print(f"Daily Active Calorie Goal Set to: {cal_goal} calories")
    tokenstore = os.getenv("GARMIN_CRED_PATH")
    polling_freq = int(os.getenv("POLLING_FREQ"))

    domain_block_list = get_block_list("./data/blocklist.txt")

    garmin_client = init_api(g_email,g_password,tokenstore)

    while True:
        todays_stats = get_garmin_data(garmin_client)
        
        curr_active_cals = todays_stats.get("activeKilocalories",0)
        curr_steps = todays_stats.get("totalSteps",0)

        if not curr_active_cals:
            curr_active_cals = 0
        if not curr_steps:
            curr_steps = 0

        print(f"Current Active Calories: {curr_active_cals}")
        print(f"Current Steps: {curr_steps}")

        if (curr_active_cals < cal_goal) and (curr_steps < step_goal):
            #Daily fitness goals are not yet met, add domains to blocklist
            update_pihole(action="add", domain_block_list=domain_block_list)
        else:
            #Daily fitness goals have been met, remove domains from pi-hole blocklist
            update_pihole(action="sub", domain_block_list=domain_block_list)
        
        print(f"sleeping for {polling_freq} seconds...")
        time.sleep(polling_freq)

if __name__ == "__main__":
    main()


