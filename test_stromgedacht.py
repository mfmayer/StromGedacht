import json
from datetime import datetime, timedelta
from power_status import PowerStatus, get_status_times

# Ersetzen Sie diese durch Ihre eigene Postleitzahl und API-Antwort
ZIP_CODE = "12345"
SAMPLE_API_RESPONSE = {
    "states": [
        {
            "from": "2023-05-07T07:15:18.129Z",
            "to": "2023-05-07T07:15:18.129Z",
            "state": 1
        }
    ]
}

class MockApi:
    def fetch_data(self, zip_code, from_time, to_time):
        return SAMPLE_API_RESPONSE

class MockEntity:
    def __init__(self):
        self.data = None

    def update(self):
        self.data = SAMPLE_API_RESPONSE

def main():
    api = MockApi()
    power_status = PowerStatus(api, ZIP_CODE)
    power_status.update()
    
    print("Current Status:", power_status.state)
    
    time_until_stress, time_until_relax = get_status_times(power_status.data, 2)
    print("Time Until Next Stress Situation:", time_until_stress)
    print("Time Until Next Relaxed Situation:", time_until_relax)

if __name__ == "__main__":
    main()
