# at top
import logging, time, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class WMATAClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get("WMATA_API_KEY")
        if not self.api_key:
            raise ValueError("WMATA_API_KEY environment variable not set")

        self.base_url = "https://api.wmata.com"
        self.headers = {"api_key": self.api_key, "Accept": "application/json"}

        # Robust session with retries/backoff for timeouts/502/503/504
        retries = Retry(
            total=4,
            connect=4,
            read=4,
            status=4,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.timeout = 20  # seconds

    def get_all_station_predictions(self):
        url = f"{self.base_url}/StationPrediction.svc/json/GetPrediction/All"
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return data.get("Trains", [])
