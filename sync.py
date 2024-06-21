import os
from datetime import datetime

import requests

from example import init_api, email, password


class Synchronizer:
    def __init__(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token

    @staticmethod
    def get_garmin_activities(start, limit):
        api = init_api(email, password)
        activities = api.get_activities(start, limit)
        for activity in activities:
            print(f"start time: {activity['startTimeGMT']}")
            d = datetime.strptime(activity["startTimeGMT"], "%Y-%m-%d %H:%M:%S")
            print(f"d: {d}")

        return activities

    def refresh_token(self):
        return # TODO

    def get_strava_activities(self, after):
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            url = f"https://www.strava.com/api/v3/athlete/activities?after={after}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
            activities = response.json()

            # Print the activities start time
            for activity in activities:
                print(f"Start time: {activity['start_date']}")
                d = datetime.strptime(activity["start_date"], "%Y-%m-%dT%H:%M:%SZ")
                print(f"d: {d}")

            return activities
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def set_strava_activity_name(self, activity_id, name):
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            data = {
                "name": name
            }
            url = f"https://www.strava.com/api/v3/activities/{activity_id}"
            response = requests.put(url, headers=headers, json=data)
            response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

            return
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return

    def sync_activity_name_from_garmin_to_strava(self, garmin_activities, strava_activities):
        for strava_activity in strava_activities:
            strava_start = datetime.strptime(strava_activity["start_date"], "%Y-%m-%dT%H:%M:%SZ")
            for garmin_activity in garmin_activities:
                garmin_start = datetime.strptime(garmin_activity["startTimeGMT"], "%Y-%m-%d %H:%M:%S")
                if strava_start == garmin_start:
                    garmin_name = garmin_activity["activityName"]
                    self.set_strava_activity_name(strava_activity["id"], garmin_name)
                    print(f"Found activity at {garmin_start}, synced name to {garmin_name}")
                    break

        return


access_token = os.getenv("SYNC_ACCESS_TOKEN")
refresh_token = os.getenv("SYNC_REFRESH_TOKEN")
sync = Synchronizer(access_token, refresh_token)
sync.set_strava_activity_name(11696146089, "hohiho")
