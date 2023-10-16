from dataclasses import dataclass
import requests

@dataclass
class BaseMaps:
    apikey:str = None

    def _reverse_geocode_url(self, *args, **kwargs):
        raise NotImplementedError("_reverse_geocode_url method must be implemented")

    def _reverse_geoceode_params(self, latitude, longitude, *args, **kwargs):
        raise NotImplementedError("_reverse_geocode_url method must be implemented")

    def _geocode_url(self, address, *args, **kwargs):
        raise NotImplementedError("_geocode_url method must be implemented")
    
    def _geocode_params(self, address,  *args, **kwargs):
        raise NotImplementedError("_geocode_params method must be implemented")

    @property
    def _geocode_headers(self):
        raise NotImplementedError("_geocode_headers method must be implemented")

    def geocode_request(self, address, *args, **kwargs):
        return requests.get(self._geocode_url(address, *args, **kwargs), params=self._geocode_params(address, *args, **kwargs), headers=self._geocode_headers)
    
    def reverse_geocode_request(self, latitude, longitude):
        return requests.get(self._reverse_geocode_url(), params=self._reverse_geoceode_params(latitude, longitude), headers=self._geocode_headers)
