from odoo.http import request, Response, Controller, route
import logging
import json

_logger = logging.getLogger(__name__)
def create_report(data):
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
        data = json.loads(request.httprequest.data)
        action = data["action"]
        d = data["data"]
        try:
            response = call_webhook_action(action, d)
        except KeyError:
            _logger.error(f"Webhook action {action} not found")
            return Response("Action not defined", status=500)
        return Response(json.dumps(response), status=200)