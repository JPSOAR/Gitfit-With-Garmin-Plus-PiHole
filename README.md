# "Git" Fit with Garmin Connect and Pi-Hole
Ensure you meet your daily fitness goals by using Pi-Hole to block access to web content (like netflix) until you've burned enough calories or met your step goal for the day.  

See my blog post about my adventure creating this project:
https://www.jpit.io/posts/gitfit-with-garmin-plus-pihole/

## Requirements
1. A garmin fitness tracker (like a smart watch) that syncs to Garmin Connect
2. A Garmin Connect account
3. A Pi-Hole running on your network

## Run Locally with Python
1. Clone this repository and then `cd` to that folder on your machine
2. Create a new python virtual environment by running `python -m venv ./venv`
3. activate the venv with `source .\venv\bin\activate`
4. install required modules with `pip install -r requirements.txt`
5. Create a file called `.env` in the root of the repository and add the following content to it
```
GARMIN_EMAIL="YOURGARMINACCOUNT@EXAMPLE.com"
GARMIN_PW="Your Garmin Password"
GARMIN_CRED_PATH="./.garminconnect"
PIHOLE_HOST="pi.hole"
PIHOLE_API_TOKEN="Your Pihole API Token"
DAILY_STEP_GOAL="10000"
DAILY_CALORIE_GOAL="600"
POLLING_FREQ="600"
```
| .env Variables | Description |
|---|---|
| GARMIN_EMAIL | The email/account you use to login to connect.garmin.com |
| GARMIN_PW | The password for your connect.garmin.com account | 
| GARMIN_CRED_PATH | Relative path of where the script should store your Garmin OAUTH access tokens after logging in for the first time.  I just use `./.garminconnect` |
| PIHOLE_HOST | Hostname or IP of the Pi-hole on your network. `pi.hole` is the default |
| PIHOLE_API_TOKEN | Your Pi-Hole API Token can be obtained by going to your `Pi-hole's web interface` -> `Settings` -> `API` -> `Show API Token` |
| DAILY_STEP_GOAL | Set this to the number of steps you want to get before unblocking your URLs |
| DAILY_CALORIE_GOAL | Set this to the number of *active* calories you want to get before unblocking your URLs |
| POLLING_FREQ | How frequently to check garmin connect for updates to your daily health metrics | 