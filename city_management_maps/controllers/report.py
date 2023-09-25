from odoo.http import request, Response, Controller, route
import logging
import json

_logger = logging.getLogger(__name__)

BASE_URL = '/city_management'
CHATBOT_OPTIONS_URL = f'{BASE_URL}/chatbot_options'
class CategoriesController(Controller):   

    
    @property
    def base_url(self):
        return request.env['ir.config_parameter'].sudo().get_param('web.base.url')

    @route(f"{CHATBOT_OPTIONS_URL}/report/<int:report_id>/geocode_address", type='http', auth='none', methods=['GET'], csrf=False, cors="*")
    def geocode_get_address(self, name, category_id=False):
        report = request.env['city.report'].sudo().search_read([('name', '=', name)], ["geocoding_display_name"], limit=1)
        if report:
            response_body = {
                "result": report[0]["geocoding_display_name"],
                
            }
        else:
            raise Exception("Report not found")
        resp = Response(json.dumps(response_body), status=200)
        resp.headers['Content-Type'] = 'application/json'
        return resp
