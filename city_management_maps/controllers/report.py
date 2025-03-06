from odoo.http import request, Response, Controller, route
import logging
import json

from ..utils.basemaps import BaseMaps
from ..utils.maps import GEOCODER_STRATEGIES, HERE_APIKEY

_logger = logging.getLogger(__name__)

BASE_URL = '/city_management'
CHATBOT_OPTIONS_URL = f'{BASE_URL}/chatbot_options'
class GeocodeController(Controller):   

    
    @property
    def base_url(self):
        return request.env['ir.config_parameter'].sudo().get_param('web.base.url')

    @property
    def maps(self):
        geocoder_strategy = request.env["ir.config_parameter"].sudo().get_param("city_management_maps.geocoder_strategy", "heremaps")
        maps_constructor = GEOCODER_STRATEGIES[geocoder_strategy]
        apikey = request.env["ir.config_parameter"].sudo().get_param("city_management_maps.geocoder_apikey", HERE_APIKEY)
        maps:BaseMaps = maps_constructor(apikey=apikey)
        return maps

    @property
    def default_address(self):
        return request.env["ir.config_parameter"].sudo().get_param("city_management_maps.default_address", "Irapuato, Guanajuato, Mexico")


    @route(f"{BASE_URL}/geocode_address", type='http', auth='none', methods=['POST'], csrf=False, cors="*")
    def geocode_by_address(self):
        data = json.loads(request.httprequest.data)
        geocode_response = self.maps.geocode_request(f'{data["report_address"]}{self.default_address}')
        return Response(json.dumps({
            "result": geocode_response["display_name"]
        }), status=200)

    @route(f"{BASE_URL}/reverse_geocode", type='http', auth='none', methods=['POST'], csrf=False, cors="*")
    def reverse_geocode(self):
        data = json.loads(request.httprequest.data)
        geocode_response = self.maps.reverse_geocode_request(data["latitude"],data["longitude"])
        return Response(json.dumps({
            "result": geocode_response["display_name"]
        }), status=200)

    @route(f"{CHATBOT_OPTIONS_URL}/report/<int:report_id>/geocode_address", type='http', auth='none', methods=['GET'], csrf=False, cors="*")
    def geocode_get_address(self, report_id):
        report = request.env['city.report'].sudo().browse([int(report_id)]).read(["geocoding_display_name"])
        if report:
            response_body = {
                "result": report[0]["geocoding_display_name"],
                
            }
        else:
            raise Exception("Report not found")
        resp = Response(json.dumps(response_body), status=200)
        resp.headers['Content-Type'] = 'application/json'
        return resp
