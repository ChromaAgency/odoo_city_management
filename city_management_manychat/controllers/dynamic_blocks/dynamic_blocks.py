from odoo.http import request, Response, Controller, route
from .utils import DynamicBlockV2, Message, Button, SetFieldValueAction, QuickReply, Content
import json
import logging

_logger = logging.getLogger(__name__)


DYNAMIC_BLOCK_BASE_URL = '/city_management/dynamic_block'


class DynamicBlockController(Controller):

    @property
    def base_url(self):
        return request.env['ir.config_parameter'].sudo().get_param('web.base.url')

    @route(f"{DYNAMIC_BLOCK_BASE_URL}/categories", type='http', auth='none', methods=['GET'], csrf=False, cors="*")
    def categories_dynamic_block_route(self, **kwargs):
        categories = request.env['city.report.category'].sudo().search_read(
            [('parent_id', '=', False)], ['name', 'id'],limit=3)
        content = Content(type="telegram")
        message = Message(type="text", text="Elige por favor")
        for category in categories:
            button = Button(type="node", caption=category["name"], target="Category selected", actions=[
                            SetFieldValueAction(action="set_field_value", field_name="selected_category_id", value=category["id"])])
            message.add_button(button)
        content.add_message(message)
        dynamic_block = DynamicBlockV2(content).build()
        resp = Response(json.dumps(dynamic_block), status=200)
        resp.headers['Content-Type'] = 'application/json'
        return resp

    @route(f"{DYNAMIC_BLOCK_BASE_URL}/categories/<int:category_id>/subcategories", type='http', auth='none', methods=['GET'], csrf=False, cors="*")
    def subcategories_dynamic_block_route(self, category_id):
        categories = request.env['city.report.category'].sudo().search_read(
            [('parent_id', '=', category_id)], ['name', 'id'])
        content = Content(type="telegram")
        message = Message(type="text", text="Elige por favor")
        for category in categories:
            button = Button(type="node", caption=category["name"], target="SubCategory selected", actions=[
                            SetFieldValueAction(action="set_field_value", field_name="selected_subcategory_id", value=category["id"])])
            message.add_button(button)
        content.add_message(message)
        dynamic_block = DynamicBlockV2(content).build()
        resp = Response(json.dumps(dynamic_block), status=200)
        resp.headers['Content-Type'] = 'application/json'
        return resp
