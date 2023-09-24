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

    @route([f"{BASE_URL}/categories/code/<code>",
            f"{BASE_URL}/categories/<int:category_id>/subcategories/code/<code>"], type='http', auth='none', methods=['GET'], csrf=False, cors="*")
    def categories_code_route(self, code, category_id=False):
        category = request.env['city.report.category'].sudo().search_read([('code', '=', code), ('parent_id','=', category_id)], ["name", "code", "id"], limit=1)
        if category:
            response_body = {
                "result": category[0],
                
            }
        else:
            raise Exception("Category not found")
        resp = Response(json.dumps(response_body), status=200)
        resp.headers['Content-Type'] = 'application/json'
        return resp
