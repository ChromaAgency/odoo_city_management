
from .heremaps import HereMapsV6
from .googlemaps import GoogleMaps

GEOCODER_STRATEGIES = {
    "heremaps": HereMapsV6,
    "google": GoogleMaps,
}
GMAPS_APIKEY = "AIzaSyAHFy7TrD_oP4iNpYCUUFaY1zNxILLiyDI"
HERE_APIKEY = "xfzfeKOx1N-e9REDAG28EVOS7XWfLUUFe78aGBJUiiY"