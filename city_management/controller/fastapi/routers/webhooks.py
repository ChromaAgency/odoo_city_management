# -*- coding: utf-8 -*-

from typing import Annotated, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas import WebhookRequest, WebhookResponse

_logger = logging.getLogger(__name__)

router = APIRouter()


def create_report(env: Environment, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new report from webhook data"""
    mobile = data.get("mobile", None)
    neighbour = data.pop("neighbour", None)
    
    if not neighbour:
        raise ValueError("Neighbour data is required to create a report")
    
    if mobile:
        partner_vals = neighbour
        partner_vals.update({'phone': mobile})
        
        partner = env['res.partner'].sudo().search([('phone', '=', mobile)], limit=1)
        if not partner:
            partner = env['res.partner'].sudo().create(partner_vals)
        else:
            partner.write(partner_vals)
        
        data['neighbour_id'] = partner.id
    
    report = env['city.report'].sudo().create(data)
    return {
        "report_id": report.id,
        "report_name": report.name
    }


def update_report(env: Environment, report_id: int, write_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing report"""
    report = env['city.report'].sudo().browse([report_id])
    
    if not report.exists():
        raise ValueError(f"Report with ID {report_id} not found")
    
    report.write(write_data)
    return {
        "report_id": report.id,
        "report_name": report.name
    }


def webhook_create_report(env: Environment, data: Dict[str, Any]) -> Dict[str, Any]:
    """Webhook handler for creating a report"""
    return create_report(env, data)


def webhook_update_report(env: Environment, data: Dict[str, Any]) -> Dict[str, Any]:
    """Webhook handler for updating a report"""
    report_id = data.pop("report_id")
    return update_report(env, int(report_id), data)


def webhook_log(env: Environment, data: Dict[str, Any]) -> Dict[str, Any]:
    """Webhook handler for logging"""
    _logger.info(data)
    return {"status": "logged"}


# Webhook action mapping
WEBHOOK_ACTIONS = {
    "CREATE_REPORT": webhook_create_report,
    "UPDATE_REPORT": webhook_update_report,
    "LOG": webhook_log,
}


@router.post("", response_model=WebhookResponse)
def process_webhook(
    webhook: WebhookRequest,
    env: Annotated[Environment, Depends(odoo_env)]
) -> WebhookResponse:
    """
    Process webhook requests for city management.
    
    Args:
        webhook: Webhook request with action and data
        env: Odoo environment
        
    Returns:
        Webhook response with report information
    """
    try:
        action = webhook.action
        data = webhook.data
        
        if action not in WEBHOOK_ACTIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown webhook action: {action}"
            )
        
        # Process category and subcategory IDs
        if "category_id" in data and data.get('category_id'):
            data['category_id'] = int(data['category_id'])
        if "subcategory_id" in data and data.get('subcategory_id'):
            data['subcategory_id'] = int(data['subcategory_id'])
        
        # Execute webhook action
        handler = WEBHOOK_ACTIONS[action]
        response = handler(env, data)
        
        return WebhookResponse(**response)
        
    except HTTPException:
        raise
    except ValueError as e:
        _logger.error(f"Validation error in webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        _logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )
