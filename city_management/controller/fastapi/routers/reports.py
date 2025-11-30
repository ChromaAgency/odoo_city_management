# -*- coding: utf-8 -*-

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from odoo.api import Environment
from odoo.addons.fastapi.dependencies import odoo_env
from ..schemas.report import Report, ReportUpsert

from ..schemas import ReportResponse, ReportMessage

_logger = logging.getLogger(__name__)

router = APIRouter()

def _get_report(env, report):
        CityReport = env['city.report'].sudo()
        log = False
        if report_id := report.id:
            log = env['city.report.state.log'].sudo().search(
                [('report_id', '=', report_id)],
                limit=1
            )
            res = {}
            res.update({
                "state": dict(CityReport._fields['state']._description_selection(env)).get(report.state),
                "note": report.note if report.note else "Sin notas adicionales",
                "last_change_date": "",
                "last_change_time": "",
            })
        if log:
            log_create_date = log.create_date
            res.update({
                "last_change_date": log_create_date.strftime("%d/%m/%Y"),
                "last_change_time": log_create_date.strftime("%H:%M"),
            })
        return Report(
        name=report.name,
        category_id=report.category_id.id if report.category_id else None,
        subcategory_id=report.subcategory_id.id if report.subcategory_id else None,
        state=res['state'],
        note=res['note'] or "Sin notas adicionales",
        last_change_date=res['last_change_date'],
        last_change_time=res['last_change_time'],
    )

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
    report = CityReport.search(
        [('name', '=', name)],
        limit=1
    )
    
    
    return ReportResponse(result=_get_report(env, report))


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
        res = _get_report(env, report)
        return f"El folio *{res.name}* 📁 se encuentra en estado *{res.state}* desde el *{res.last_change_date}* a las *{res.last_change_time}* *Nota:*{res.note}"
    
    reports = CityReport.search(
        [('mobile', '=', phone)],
        limit=5
    )
    
    result = "\n\n".join(_get_report_message(report) for report in reports)
    
    return ReportMessage(result=result)


@router.post("", response_model=ReportResponse, responses={404: {"model": str}})
def upsert_report(report:ReportUpsert, 
    env: Annotated[Environment, Depends(odoo_env)]
                  ):
    """
    Create or update a report based on the provided data.
    
    Args:
        report: Report data for creation or update
    Returns:
        Message indicating the result of the operation
    """
   
    neighbour = report.neighbour
    # if not neighbour:
    #     raise ValueError("Neighbour data is required to create a report")
    
    report_data = report.model_dump(exclude={'id', 'neighbour'})
    if report.mobile:
        partner_vals = neighbour.model_dump()   
        partner_vals.update({'phone': report.mobile})
        
        partner = env['res.partner'].sudo().search([('phone', '=', report.mobile)], limit=1)
        if not partner:
            partner = env['res.partner'].sudo().create(partner_vals)
        else:
            partner.write(partner_vals)
        
        neighbour_id = partner.id
        report_data['neighbour_id'] = neighbour_id

    if not report.id:
        report_rec = env['city.report'].sudo().create(report_data)
    else:
        report_rec = env['city.report'].sudo().browse([report.id])
        if not report_rec.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {report.id} not found"
            )
        report_rec.write(report_data)
    
    return ReportResponse(result=_get_report(env, report_rec))