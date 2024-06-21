import json
import time
from dataclasses import dataclass
import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

from example import init_api, email, password

strava_token_filepath = os.path.expanduser('~/.strava_token')


@dataclass
class StravaToken:
    access_token: str
    refresh_token: str
    expires_at: int


def load_strava_token() -> StravaToken:
    try:
        with open(strava_token_filepath, 'r') as f:
            token_data = json.load(f)
            token = StravaToken(
                access_token=token_data['access_token'],
                refresh_token=token_data['refresh_token'],
                expires_at=token_data['expires_at']
            )
            print(f"Token loaded from {strava_token_filepath}")
            return token
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File not found at {strava_token_filepath}")


class Synchronizer:
    def __init__(self, token: StravaToken):
        self.token = token

    @staticmethod
    def get_garmin_activities(start: int, limit: int) -> list[dict]:
        api = init_api(email, password)

        return api.get_activities(start, limit)

    def save_strava_token(self):
        with open(strava_token_filepath, 'w') as f:
            json.dump({
                'access_token': self.token.access_token,
                'refresh_token': self.token.refresh_token,
                'expires_at': self.token.expires_at
            }, f)
        print(f"Token saved to {strava_token_filepath}")

    def check_refresh_access_token(self):
        if time.time() < self.token.expires_at - 20:
            return

        try:
            data = {
                'client_id': os.getenv("GARSYNC_CLIENT_ID"),
                'client_secret': os.getenv("GARSYNC_CLIENT_SECRET"),
                'refresh_token': self.token.refresh_token,
                'grant_type': 'refresh_token'
            }

            response = requests.post("https://www.strava.com/oauth/token", data=data)
            response.raise_for_status()
            response_json = response.json()
            self.token = StravaToken(response_json["access_token"], response_json["refresh_token"],
                                     response_json["expires_at"])
            self.save_strava_token()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

    def get_strava_activities(self, after: int) -> list[dict]:
        try:
            self.check_refresh_access_token()

            headers = {
                "Authorization": f"Bearer {self.token.access_token}"
            }
            url = f"https://www.strava.com/api/v3/athlete/activities?after={after}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
            return response.json()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

    def set_strava_activity_name(self, activity_id: str, name: str):
        try:
            self.check_refresh_access_token()

            headers = {
                "Authorization": f"Bearer {self.token.access_token}",
                "Content-Type": "application/json"
            }
            data = {
                "name": name,
                "description":
                    "Activity name is sync-ed from Garmin by https://github.com/santheipman/python-garminconnect"
            }
            url = f"https://www.strava.com/api/v3/activities/{activity_id}"
            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

            return
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

    def sync_activity_name_from_garmin_to_strava(self, garmin_activities: list[dict], strava_activities: list[dict]):
        for strava_activity in strava_activities:
            strava_start = datetime.strptime(strava_activity["start_date"], "%Y-%m-%dT%H:%M:%SZ")
            strava_name = strava_activity["name"]
            for garmin_activity in garmin_activities:
                garmin_start = datetime.strptime(garmin_activity["startTimeGMT"], "%Y-%m-%d %H:%M:%S")
                garmin_name = garmin_activity["activityName"]
                if strava_start == garmin_start and strava_name != garmin_name:
                    self.set_strava_activity_name(strava_activity["id"], garmin_name)
                    print(
                        f"Activity at {garmin_start}: changed Strava activity name from {strava_name} to {garmin_name}"
                    )
                    break


load_dotenv()

sync = Synchronizer(load_strava_token())

after_time = int((datetime.now() - timedelta(days=4)).timestamp())

sync.sync_activity_name_from_garmin_to_strava(
    garmin_activities=sync.get_garmin_activities(0, 4),
    strava_activities=sync.get_strava_activities(after=after_time)
)
