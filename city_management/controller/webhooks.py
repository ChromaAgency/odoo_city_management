from odoo.http import request, Response, Controller, route
import logging
import json

_logger = logging.getLogger(__name__)
def create_report(data):
    mobile = data.get("mobile", None)  # Remove mobile if it exists
    partner = None
    neighbour = data.pop("neighbour", None)
    if not neighbour:
        raise ValueError("Neighbour data is required to create a report")
    if mobile:
        partner_vals = neighbour
        
        partner_vals.update({
                'mobile': mobile,
            })
        partner = request.env['res.partner'].sudo().search([('mobile', '=', mobile)], limit=1)
        if not partner:
            partner = request.env['res.partner'].sudo().create(partner_vals)
        else: 
            partner.write(partner_vals)
        data['neighbour_id'] = partner.id
    report = request.env['city.report'].sudo().create(data)
    return {
        "report_id": report.id,
        "report_name": report.name
    }

def update_report(report_id, write_data):
    report = request.env['city.report'].sudo().browse([report_id])
    report.write(write_data)
    return {
        "report_id": report.id,
        "report_name": report.name
    }


def webhook_update_report(data):
    report_id = data.pop("report_id")
    return update_report(int(report_id), data)

def webhook_create_report(data):
    return create_report(data)

webhooks = {
    "CREATE_REPORT": webhook_create_report,
    "UPDATE_REPORT": webhook_update_report,
    "LOG": lambda data: _logger.info(data)
}

def call_webhook_action(action, data):
    webhook = webhooks[action]
    try:
        response = webhook(data)
    except KeyError:
        _logger.error(f"Webhook failed on keyerror")
        raise
    return response


WEBHOOK_BASE_URL = '/city_management/webhooks'
class WebhookController(Controller):   

    @property
    def base_url(self):
        return request.env['ir.config_parameter'].sudo().get_param('web.base.url')
    
    @route(WEBHOOK_BASE_URL, type='http', auth='none', methods=['POST'], csrf=False, cors="*")
    def webhooks_route(self):
        try:
            data = json.loads(request.httprequest.data)
            try:
                action = data["action"]
                d = data["data"]
                if "category_id" in d:
                    d['category_id'] = int(d.pop("category_id"))
                if "subcategory_id" in d:
                    d['subcategory_id'] = int(d.pop("subcategory_id"))
                response = call_webhook_action(action, d)
            except KeyError:
                _logger.error(f"Webhook action {action} not found")
                return Response("Action not defined", status=500)
        except Exception as e:
            _logger.error(f"Error in webhook action: {e}")
            return Response(f"Error in webhook action: {e}", status=500)
        return Response(json.dumps(response), status=200)