from odoo.api import model
from odoo.models import Model
from odoo.fields import Char, Text, Integer, Date, Selection, Many2one, One2many, Boolean
from odoo.exceptions import UserError
from odoo import api, fields, models, _
import random
import string
import logging

from ..utils.basemaps import BaseMaps

from ..utils.heremaps import HereMapsV6
from ..utils.googlemaps import GoogleMaps
_logger = logging.getLogger(__name__)


GEOCODER_STRATEGIES = {
    "heremaps": HereMapsV6,
    "google": GoogleMaps,
}
GMAPS_APIKEY = "AIzaSyAHFy7TrD_oP4iNpYCUUFaY1zNxILLiyDI"
HERE_APIKEY = "xfzfeKOx1N-e9REDAG28EVOS7XWfLUUFe78aGBJUiiY"
class CityReport(Model):
    _inherit = "city.report"

    geocoding_display_name = Char(string=_("Geocoding Display Name"), copy=False)
    geocoding_street = Char(string=_("Geocoding Street"), copy=False)
    geocoding_street_number = Char(string=_("Geocoding Street"), copy=False)
    geocoding_city = Char(string=_("Geocoding City"), copy=False)
    geocoding_state = Char(string=_("Geocoding State"), copy=False)
    geocoding_country = Char(string=_("Geocoding State"), copy=False)

    def geocode_report_location(self):
        geocoder_strategy = self.env["ir.config_parameter"].sudo().get_param("city_management_maps.geocoder_strategy", "heremaps")
        maps_constructor = GEOCODER_STRATEGIES[geocoder_strategy]
        apikey = self.env["ir.config_parameter"].sudo().get_param("city_management_maps.geocoder_apikey", HERE_APIKEY)
        maps:BaseMaps = maps_constructor(apikey=apikey)
        for rec in self:
            if not self.report_address:
                raise UserError(_("Report address is required to geocode."))
            geocode_response = maps.geocode_request(rec.report_address)
            rec.write({
                "geocoding_display_name": geocode_response["display_name"],
                "geocoding_street": geocode_response["street"],
                "geocoding_street_number": geocode_response["street_number"],
                "geocoding_city": geocode_response["city"],
                "geocoding_state": geocode_response["state"],
                "geocoding_country": geocode_response["country"],
                "report_latitude": geocode_response["latitude"],
                "report_longitude": geocode_response["longitude"],
            })

    def write(self, vals):
        _ = super().write(vals)
        if "report_address" in vals:
            self.geocode_report_location()
        return _