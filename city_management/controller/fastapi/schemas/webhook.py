# -*- coding: utf-8 -*-

from typing import Any, Dict
from pydantic import BaseModel, ConfigDict


class WebhookRequest(BaseModel):
    """Webhook request schema"""
    action: str
    data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class WebhookResponse(BaseModel):
    """Webhook response schema"""
    report_id: int
    report_name: str
