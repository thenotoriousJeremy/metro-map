# wmata_client.py
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv


def _load_dotenv_robust() -> None:
    """
    Load .env from both CWD and this file's directory to be robust under systemd.
    Later values override earlier ones.
    """
    try:
        # Try project working directory first (if running manually)
        load_dotenv()
        # Then ensure we also load alongside this file (if systemd sets a different CWD)
        here = Path(__file__).parent.resolve()
        load_dotenv(dotenv_path=here / ".env")
    except Exception as e:
        logging.warning("Failed to load .env: %s", e)


class WMATAClient:
    """
    Minimal WMATA API client with retry/backoff.
    Reads WMATA_API_KEY from environment/.env unless provided explicitly.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.wmata.com",
        timeout: int = 20,
        total_retries: int = 4,
        backoff_factor: float = 1.5,
    ) -> None:
        _load_dotenv_robust()
        self.api_key = api_key or os.environ.get("WMATA_API_KEY")
        if not self.api_key:
            raise ValueError("WMATA_API_KEY environment variable not set")

        self.base_url = base_url.rstrip("/")
        self.timeout = int(timeout)

        # Build a session with sensible retries for flakiness/timeouts
        self.session = requests.Session()
        self.session.headers.update({
            "api_key": self.api_key,
            "Accept": "application/json",
        })
        retry = Retry(
            total=total_retries,
            connect=total_retries,
            read=total_retries,
            status=total_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    # --------------------
    # Internal HTTP helper
    # --------------------
    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        GET {base_url}/{path} with retries and a reasonable timeout.
        Raises for non-2xx.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.get(url, params=params or {}, timeout=self.timeout)
        resp.raise_for_status()
        # Some WMATA endpoints return empty body on HEAD/edge cases — we only use GET here
        try:
            return resp.json()
        except ValueError:
            # Not JSON; return raw text for debugging
            return resp.text

    # ---------------------------
    # Train positions (systemwide)
    # ---------------------------
    def get_train_positions(self) -> List[Dict[str, Any]]:
        """
        Real-time train positions. NOTE: many entries are between stations and have StationCode=None.
        WMATA expects contentType=json; without it, they may 404.
        Returns list of dicts under key "TrainPositions".
        """
        data = self._get("TrainPositions/TrainPositions", params={"contentType": "json"})
        if isinstance(data, dict):
            # Try multiple casings defensively
            return data.get("TrainPositions") or data.get("trainPositions") or []
        return []

    # -----------------------------------------
    # Next-train predictions (ALL stations)
    # -----------------------------------------
    def get_all_station_predictions(self) -> List[Dict[str, Any]]:
        """
        Get next-train predictions for ALL stations in one call.
        Returns list under "Trains".
        """
        data = self._get("StationPrediction.svc/json/GetPrediction/All")
        if isinstance(data, dict):
            return data.get("Trains") or data.get("trains") or []
        return []

    # -----------------------------------------
    # Next-train predictions for ONE station
    # -----------------------------------------
    def get_trains_at_station(self, station_code: str) -> List[Dict[str, Any]]:
        """
        Get next-train predictions for a single station by code (e.g., 'A01').
        Returns list under "Trains".
        """
        if not station_code:
            return []
        path = f"StationPrediction.svc/json/GetPrediction/{station_code}"
        data = self._get(path)
        if isinstance(data, dict):
            return data.get("Trains") or data.get("trains") or []
        return []

    def __repr__(self) -> str:
        key_show = self.api_key[:4] + "..." if self.api_key else "<none>"
        return f"<WMATAClient base_url={self.base_url} api_key={key_show}>"
