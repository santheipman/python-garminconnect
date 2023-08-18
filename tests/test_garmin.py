import pytest

import garminconnect


DATE = "2023-07-01"


@pytest.fixture(scope="session")
def garmin():
    return garminconnect.Garmin("email", "password")


@pytest.mark.vcr
def test_stats(garmin):
    garmin.login()
    stats = garmin.get_stats(DATE)
    assert "totalKilocalories" in stats
    assert "activeKilocalories" in stats


@pytest.mark.vcr
def test_user_summary(garmin):
    garmin.login()
    user_summary = garmin.get_user_summary(DATE)
    assert "totalKilocalories" in user_summary
    assert "activeKilocalories" in user_summary


@pytest.mark.vcr
def test_steps_data(garmin):
    garmin.login()
    steps_data = garmin.get_steps_data(DATE)[0]
    assert "steps" in steps_data


@pytest.mark.vcr
def test_floors(garmin):
    garmin.login()
    floors_data = garmin.get_floors(DATE)
    assert "floorValuesArray" in floors_data


@pytest.mark.vcr
def test_daily_steps(garmin):
    garmin.login()
    daily_steps = garmin.get_daily_steps(DATE, DATE)[0]
    assert "calendarDate" in daily_steps
    assert "totalSteps" in daily_steps
    assert "stepGoal" in daily_steps


@pytest.mark.vcr
def test_heart_rates(garmin):
    garmin.login()
    heart_rates = garmin.get_heart_rates(DATE)
    assert "calendarDate" in heart_rates
    assert "restingHeartRate" in heart_rates


@pytest.mark.vcr
def test_stats_and_body(garmin):
    garmin.login()
    stats_and_body = garmin.get_stats_and_body(DATE)
    assert "calendarDate" in stats_and_body
    assert "metabolicAge" in stats_and_body


@pytest.mark.vcr
def test_body_composition(garmin):
    garmin.login()
    body_composition = garmin.get_body_composition(DATE)
    assert "totalAverage" in body_composition
    assert "metabolicAge" in body_composition["totalAverage"]


@pytest.mark.vcr
def test_body_battery(garmin):
    garmin.login()
    body_battery = garmin.get_body_battery(DATE)[0]
    assert "date" in body_battery
    assert "charged" in body_battery
