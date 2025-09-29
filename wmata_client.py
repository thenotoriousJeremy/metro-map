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
    
    def get_train_positions(self):
        """Get real-time train positions.
        
        Returns:
            list: List of train positions with their details
        """
        endpoint = f"{self.base_url}/TrainPositions/TrainPositions"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()["TrainPositions"]
    
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
