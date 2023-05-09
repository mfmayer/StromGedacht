import logging
import datetime
from datetime import timedelta
import requests
import json

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=10)

# Replace with your API URL
API_URL = (
    "https://api.stromgedacht.de/v1/states?zip={zip}&from={from_time}&to={to_time}"
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Stromgedacht Sensor platform."""
    zip_code = config["zip"]
    stromgedacht_api = StromgedachtAPI(zip_code)
    sensors = [
        StromgedachtSensor("Current State", stromgedacht_api),
        StromgedachtSensor("Minutes Until State >= 2", stromgedacht_api, True),
        StromgedachtSensor(
            "Minutes Until State Returns to 1 or 2", stromgedacht_api, False
        ),
    ]
    async_add_entities(sensors, True)


class StromgedachtSensor(Entity):
    """Stromgedacht Sensor."""

    def __init__(self, name, stromgedacht_api, count_minutes=None) -> None:
        """Initialize the sensor."""
        self._name = name
        self._state = None
        self._stromgedacht_api = stromgedacht_api
        self._count_minutes = count_minutes

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @Throttle(SCAN_INTERVAL)
    async def async_update(self):
        """Fetch new state data for the sensor."""
        await self.hass.async_add_executor_job(self._stromgedacht_api.update)
        if self._name == "Current State":
            self._state = self._stromgedacht_api.current_state
        elif self._count_minutes is not None:
            self._state = self._stromgedacht_api.count_minutes(self._count_minutes)


class StromgedachtAPI:
    """Get the latest data from Stromgedacht API."""

    def __init__(self, zip_code) -> None:
        self._zip = zip_code
        self._from = None
        self._to = None
        self._states = None
        self.current_state = None

    def update(self):
        """Update the data from the API."""
        now = datetime.datetime.now().isoformat()
        to = (datetime.datetime.now() + timedelta(days=2)).isoformat()
        try:
            url = API_URL.format(zip=self._zip, from_time=now, to_time=to)
            response = requests.get(url)
            data = json.loads(response.text)
            self._states = data["states"]
            self.current_state = self._states[0]["state"]
        except Exception as e:
            _LOGGER.error(f"Error fetching data from Stromgedacht API: {e}")
            self.current_state = None

    def count_minutes(self, until_state_ge_2):
        """Count the minutes based on the given condition."""
        minutes = 0
        for state_info in self._states:
            from_time = datetime.datetime.fromisoformat(state_info["from"])
            to_time = datetime.datetime.fromisoformat(state_info["to"])
            state = state_info["state"]

            if until_state_ge_2:
                if state >= 2:
                    break
            else:
                if state < 3:
                    break

            minutes += int((to_time - from_time).total_seconds() / 60)

        return minutes
