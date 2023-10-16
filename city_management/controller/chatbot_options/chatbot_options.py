from odoo.http import request, Response, Controller, route
import logging
import json

_logger = logging.getLogger(__name__)

BASE_URL = '/city_management'
CHATBOT_OPTIONS_URL = f'{BASE_URL}/chatbot_options'
class ChatBotOptions(Controller):   
    
    @property
    def base_url(self):
        return request.env['ir.config_parameter'].sudo().get_param('web.base.url')

    @route(f"{CHATBOT_OPTIONS_URL}/categories", type='http', auth='none', methods=['GET'], csrf=False, cors="*")
    def categories_route(self):
        categories = request.env['city.report.category'].sudo().search_read([('parent_id', '=', False)], ["name", "code"])
        categories.sort(key=lambda category: int(category['code']))
        response_body = {
            "result": "\n".join(f"▶️ {category['code']} - {category['name']}" for category in categories),
            "filters":{
                "maxOption":max(int(category['code']) for category in categories),
                "minOption":min(int(category['code']) for category in categories),
            }
            
        }
        resp = Response(json.dumps(response_body), status=200)
        resp.headers['Content-Type'] = 'application/json'
        return resp
    
    @route(f"{CHATBOT_OPTIONS_URL}/categories/<int:category_id>/subcategories", type='http', auth='none', methods=['GET'], csrf=False, cors="*")
    def subcategories_route(self, category_id):
        categories = request.env['city.report.category'].sudo().search_read([('parent_id', '=', category_id)], ["name", "code"])
        categories.sort(key=lambda category: int(category['code']))
        response_body = {
            "result": "\n".join(f"▶️ {category['code']} - {category['name']}\n" for category in categories),
            "filters":{
                "maxOption":max(int(category['code']) for category in categories),
                "minOption":min(int(category['code']) for category in categories),
            }
        }
        resp = Response(json.dumps(response_body), status=200)
        resp.headers['Content-Type'] = 'application/json'
        return resp
