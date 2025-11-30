# -*- coding: utf-8 -*-

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class NeighbourInfo(BaseModel):
    """Neighbour information schema"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    marital_status: Optional[str] = None
    dependent_children: Optional[int] = None
    satisfaction_level: Optional[str] = None
    expressed_feelings: Optional[str] = None
    willingness_for_volunteering: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class Report(BaseModel):
    """Report information schema"""
    name: str
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    state: str
    note: Optional[str] = "Sin notas adicionales"
    last_change_date: Optional[str] = ""
    last_change_time: Optional[str] = ""

    model_config = ConfigDict(from_attributes=True)


class ReportResponse(BaseModel):
    """Report response wrapper"""
    result: Report


class ReportMessage(BaseModel):
    """Report message for phone lookup"""
    result: str


class ReportUpsert(BaseModel):
    """Schema for creating a report"""
    mobile: Optional[str] = None
    report_address: Optional[str] = None
    report_latitude: Optional[str] = None
    report_longitude: Optional[str] = None
    note: Optional[str] = None
    user_attachment_link: Optional[str] = None
    subcategory_id: Optional[int] = None
    category_id: Optional[int] = None
    state: Optional[str] = "draft"
    company_id: Optional[int] = None
    neighbour: Optional[NeighbourInfo] = None
    id: Optional[int] = None  # For updates

    model_config = ConfigDict(from_attributes=True, exclude_none=True)


