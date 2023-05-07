import requests
import logging
from datetime import timedelta, datetime
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

# Configuration constants
CONF_ZIP = "zip"
CONF_NEXT_HOURS = "next_hours"

# Default values for optional configuration
DEFAULT_NEXT_HOURS = 2

# Throttle time for API calls
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=10)

# API URL format
URL = "https://api.stromgedacht.de/status?zip={}&from={}&to={}"

# Setup the platform


def setup_platform(hass, config, add_entities, discovery_info=None):
    zip_code = config[CONF_ZIP]
    next_hours = config.get(CONF_NEXT_HOURS, DEFAULT_NEXT_HOURS)
    power_status = PowerStatus(zip_code, next_hours)

    # Add the sensor entities
    add_entities([
        PowerStatusCurrent(power_status),
        PowerStatusNextHours(power_status, next_hours),
        PowerStatusTimeUntilStress(power_status, next_hours),
        PowerStatusTimeUntilRelax(power_status, next_hours)
    ])

# PowerStatus class to handle API calls and data


class PowerStatus:
    def __init__(self, zip_code, next_hours):
        self.zip_code = zip_code
        self.next_hours = next_hours
        self.data = None

    # Throttled update to make API calls
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        now = datetime.utcnow()
        to_time = now + timedelta(hours=48)
        response = requests.get(URL.format(
            self.zip_code, now.isoformat(), to_time.isoformat()))

        if response.status_code == 200:
            self.data = response.json()
        else:
            _LOGGER.error("Unable to fetch data from API")

# Sensor entity for current status


class PowerStatusCurrent(Entity):
    def __init__(self, power_status):
        self.power_status = power_status
        self._state = None

    @property
    def name(self):
        return "Current Status"

    @property
    def state(self):
        return self._state

    def update(self):
        self.power_status.update()
        now = datetime.utcnow()

        for state in self.power_status.data["states"]:
            from_time = datetime.fromisoformat(state["from"][:-1])
            to_time = datetime.fromisoformat(state["to"][:-1])
            if from_time <= now <= to_time:
                self._state = state["state"]
                break

# Sensor entity for highest status in the next hours


class PowerStatusNextHours(Entity):
    def __init__(self, power_status, next_hours):
        self.power_status = power_status
        self.next_hours = next_hours
        self._state = None

    @property
    def name(self):
        return f"Highest Status in Next {self.next_hours} Hours"

    @property
    def state(self):
        return self._state

    def update(self):
        self.power_status.update()
        now = datetime.utcnow()

        highest_status = 1
        for state in self.power_status.data["states"]:
            from_time = datetime.fromisoformat(state["from"][:-1])
            to_time = datetime.fromisoformat(state["to"][:-1])
            if now < from_time < now + timedelta(hours=self.next_hours):
                highest_status = max(highest_status, state["state"])

        self._state = highest_status

# Utility function to get status times


def get_status_times(status_data, next_hours):
    now = datetime.utcnow()
    max_time = now + timedelta(hours=next_hours)
    time_until_stress = timedelta(hours=48).total_seconds()
    time_until_relax = timedelta(hours=48).total_seconds()

    for state in status_data["states"]:
        from_time = datetime.fromisoformat(state["from"][:-1])
        to_time = datetime.fromisoformat(state["to"][:-1])

        if state["state"] in (3, 4) and now < from_time:
            time_until_stress = min(
                time_until_stress, (from_time - now).total_seconds())
        elif state["state"] in (1, 2) and now < from_time:
            time_until_relax = min(
                time_until_relax, (from_time - now).total_seconds())

    return time_until_stress, time_until_relax

# Sensor entity for time until next stress situation


class PowerStatusTimeUntilStress(Entity):
    def __init__(self, power_status, next_hours):
        self.power_status = power_status
        self.next_hours = next_hours
        self._state = None

    @property
    def name(self):
        return "Time Until Next Stress Situation"

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return "s"

    def update(self):
        self.power_status.update()
        time_until_stress, _ = get_status_times(
            self.power_status.data, self.next_hours)
        self._state = time_until_stress

# Sensor entity for time until next relaxed situation


class PowerStatusTimeUntilRelax(Entity):
    def __init__(self, power_status, next_hours):
        self.power_status = power_status
        self.next_hours = next_hours
        self._state = None

    @property
    def name(self):
        return "Time Until Next Relaxed Situation"

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return "s"

    def update(self):
        self.power_status.update()
        _, time_until_relax = get_status_times(
            self.power_status.data, self.next_hours)
        self._state = time_until_relax
