# -*- coding: utf-8 -*-

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env

from ..schemas import ReportResponse, ReportMessage

_logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/name/{name}", response_model=ReportResponse)
def get_report_by_name(
    name: str,
    env: Annotated[Environment, Depends(odoo_env)]
) -> ReportResponse:
    """
    Get report information by name/folio number.
    
    Args:
        name: Report name/folio
        env: Odoo environment
        
    Returns:
        Report information with current state and notes
    """
    CityReport = env['city.report'].sudo()
    report = CityReport.search_read(
        [('name', '=', name)],
        ["name", "category_id", "subcategory_id", "state", "note"],
        limit=1
    )
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with name '{name}' not found"
        )
    
    log = env['city.report.state.log'].sudo().search(
        [('report_id', '=', report[0]['id'])],
        limit=1
    )
    
    res = report[0]
    res.update({
        "state": dict(CityReport._fields['state']._description_selection(env)).get(res["state"]),
        "note": res["note"] if res["note"] else "Sin notas adicionales",
        "last_change_date": "",
        "last_change_time": "",
    })
    
    if log:
        log_create_date = log.create_date
        res.update({
            "last_change_date": log_create_date.strftime("%d/%m/%Y"),
            "last_change_time": log_create_date.strftime("%H:%M"),
        })
    
    return ReportResponse(result=res)


@router.get("/phone/{phone}", response_model=ReportMessage)
def get_reports_by_phone(
    phone: str,
    env: Annotated[Environment, Depends(odoo_env)]
) -> ReportMessage:
    """
    Get reports message by phone number.
    
    Args:
        phone: Phone number to search
        env: Odoo environment
        
    Returns:
        Formatted message with all reports for the phone number
    """
    CityReport = env['city.report'].sudo()
    
    def _get_report_message(report):
        log = env['city.report.state.log'].sudo().search(
            [('report_id', '=', report['id'])],
            limit=1
        )
        res = report
        res.update({
            "state": dict(CityReport._fields['state']._description_selection(env)).get(res["state"]),
            "note": res["note"] if res["note"] else "Sin notas adicionales",
            "last_change_date": "",
            "last_change_time": "",
        })
        if log:
            log_create_date = log.create_date
            res.update({
                "last_change_date": log_create_date.strftime("%d/%m/%Y"),
                "last_change_time": log_create_date.strftime("%H:%M"),
            })
        return f"El folio *{res['name']}* 📁 se encuentra en estado *{res['state']}* desde el *{res['last_change_date']}* a las *{res['last_change_time']}* *Nota:*{res['note']}"
    
    reports = CityReport.search_read(
        [('mobile', '=', phone)],
        ["name", "category_id", "subcategory_id", "state", "note"],
        limit=5
    )
    
    result = "\n\n".join(_get_report_message(report) for report in reports)
    
    return ReportMessage(result=result)
