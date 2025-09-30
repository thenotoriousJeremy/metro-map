import os
import requests
from dotenv import load_dotenv

class WMATAClient:
    """Client for accessing WMATA's real-time train positions API."""
    
    def __init__(self):
        """Initialize the WMATA API client."""
        load_dotenv()
        self.api_key = os.getenv('WMATA_API_KEY')
        if not self.api_key:
            raise ValueError("WMATA_API_KEY environment variable not set")
        
        self.base_url = "https://api.wmata.com"
        self.headers = {
            "api_key": self.api_key,
            "Accept": "application/json"
        }
    def get_all_station_predictions(self):
        """
        Get next-train predictions for ALL stations in one call.
        Returns a list of dicts with at least: LocationCode (station), Line (RD/BL/YL/OR/GR/SV).
        """
        endpoint = f"{self.base_url}/StationPrediction.svc/json/GetPrediction/All"
        response = requests.get(endpoint, headers=self.headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Typical shape: {"Trains": [ {...}, ... ]}
        return data.get("Trains", [])

    def get_train_positions(self):
        """Get real-time train positions."""
        endpoint = f"{self.base_url}/TrainPositions/TrainPositions"
        params = {"contentType": "json"}  # REQUIRED or WMATA returns 404
        response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        # Defensive: WMATA sometimes nests the key differently; default to []
        return data.get("TrainPositions", data.get("trainPositions", []))
    
    def get_trains_at_station(self, station_code):
        """Get trains at a specific station.
        
        Args:
            station_code (str): WMATA station code
            
        Returns:
            list: List of trains at the specified station
        """
        endpoint = f"{self.base_url}/StationPrediction.svc/json/GetPrediction/{station_code}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()["Trains"]
