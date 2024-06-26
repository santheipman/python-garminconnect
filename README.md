# Activity Name Sync

Sync activity names from Garmin to Strava.

# Install

Before installation, please read through the https://github.com/cyberjunky/python-garminconnect repo and https://developers.strava.com/docs/authentication/ to understand how Garmin and Strava authentication work, respectively.

**Step 1**. Clone the repo
```bash
git clone https://github.com/santheipman/python-garminconnect.git
```

**Step 2**. Install the dependencies
```bash
cd python-garminconnect
python3 -m venv venv
pip3 install -r requirements-dev.txt
```

**Step 3**. Register your application in order to use it to access/modify your data on Strava: https://developers.strava.com/docs/getting-started/#account

**Step 4**. Create `.env` file and paste your `client_id` and `client_secret` from Step 3 into it. The `.env` looks like this
```
GARSYNC_CLIENT_ID=your_client_id
GARSYNC_CLIENT_SECRET=your_client_secret
```

**Step 5**. Open this link in your browser to authorize your application to read and write your data on Strava. Remember to use your `client_id` in the link.
```
http://www.strava.com/oauth/authorize?client_id=your_client_id&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:write,activity:read_all
```

**Step 6**. After Step 5, you will be redirected to another url. Copy the `code` from that url and replace `your_code` in request the access token
```bash
curl -X POST https://www.strava.com/oauth/token \
  -F client_id=your_client_id \
  -F client_secret=your_client_secret \
  -F code=your_code \
  -F grant_type=authorization_code
```

**Step 7**. Paste the response from Step 6 into `~/.strava_token` file.

**Step 8**. Login into Garmin by running
```bash
python3 login_garmin.py
```

# Usage
Run
```bash
python3 sync.py
```

# Run periodically
You can utilize [crontab](https://www.doabledanny.com/cron-jobs-on-mac) to schedule to script to run periodically. 

Run `crontab -e` and add this line to run the script at every 15 minutes. Remember to specify your `SCRIPT_PATH`.

```
*/15 * * * * export GARSYNC_SCRIPT_PATH=~/dev/personal/python-garminconnect && export GARSYNC_LOG_FILE=sync_log.txt  && $GARSYNC_SCRIPT_PATH/sync.sh >> $GARSYNC_SCRIPT_PATH/$GARSYNC_LOG_FILE 2>&1 && python3 $GARSYNC_SCRIPT_PATH/trim_log.py
```
