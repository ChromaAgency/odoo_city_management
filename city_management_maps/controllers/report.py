from odoo.http import request, Response, Controller, route
import logging
import json

from ..utils.basemaps import BaseMaps
from ..utils.maps import GEOCODER_STRATEGIES, HERE_APIKEY

_logger = logging.getLogger(__name__)

BASE_URL = '/city_management'
CHATBOT_OPTIONS_URL = f'{BASE_URL}/chatbot_options'
class CategoriesController(Controller):   

    
    @property
    def base_url(self):
        return request.env['ir.config_parameter'].sudo().get_param('web.base.url')

    @route(f"{BASE_URL}/geocode_address", type='http', auth='none', methods=['POST'], csrf=False, cors="*")
    def geocode_by_address(self):
        data = json.loads(request.httprequest.data)
        geocoder_strategy = self.env["ir.config_parameter"].sudo().get_param("city_management_maps.geocoder_strategy", "heremaps")
        maps_constructor = GEOCODER_STRATEGIES[geocoder_strategy]
        apikey = self.env["ir.config_parameter"].sudo().get_param("city_management_maps.geocoder_apikey", HERE_APIKEY)
        maps:BaseMaps = maps_constructor(apikey=apikey)
        geocode_response = maps.geocode_request(data["report_address"])
        return {
            "result": geocode_response["display_name"]
        }


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
