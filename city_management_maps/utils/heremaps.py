from dataclasses import dataclass
import json

from .basemaps import BaseMaps
import logging
_logger = logging.getLogger(__name__)
@dataclass
class HereMapsV6(BaseMaps):
    apikey:str = None

    def _geocode_url(self, address,  *args, **kwargs):
        return "https://geocoder.ls.hereapi.com/6.2/geocode.json"
    
    def _geocode_params(self, address,  *args, **kwargs):
        # We could do a strategy to search with searchtext and with city and other stuff
        return {
            "apikey": self.apikey,
            "searchtext": address,
        }
    
    @property
    def _geocode_headers(self):
        return None
    
    def geocode_request(self, address, *args, **kwargs):
        geocode_response = super().geocode_request(address, *args, **kwargs)
        if geocode_response.status_code != 200:
            raise Exception("Geocode request failed")
        geocode_response_json = geocode_response.json()
        response_content = geocode_response_json["Response"]
        result = response_content['View'][0]['Result'][0]
        location = result['Location']
        _logger.info(location)
        position = location['DisplayPosition']
        address = location['Address']
        return {
            "latitude": position["Latitude"],
            "longitude": position["Longitude"],
            "display_name": address["Label"],
            "street": address.get("Street"),
            "street_number": address.get("HouseNumber"),
            "city": address.get("City"),
            "state": address.get("State"),
            "country": address.get("Country"),
            "zip_code": address.get("PostalCode"),
        }
        
        