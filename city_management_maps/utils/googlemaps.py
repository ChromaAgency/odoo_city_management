from dataclasses import dataclass

from .basemaps import BaseMaps

@dataclass
class GoogleMaps(BaseMaps):
    
    def _geocode_url(self, address,  *args, **kwargs):
        return ""
    
    def _geocode_params(self, address,  *args, **kwargs):
        return {
            "apikey": self.apikey,
        }
    
    @property
    def _geocode_headers(self):
        return None
    