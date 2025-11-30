# -*- coding: utf-8 -*-

"""
City Management FastAPI Integration

This module provides a FastAPI-based REST API for the City Management system.

Endpoints:
- Reports: Manage city reports (view by name, phone)
- Categories: Get categories and subcategories by code
- Citizen Intentions: Create citizen intentions
- Webhooks: Handle webhook callbacks for report creation and updates

To use this API:
1. Install the 'fastapi' addon from OCA/rest-framework
2. Create a FastAPI endpoint in Odoo with app="city_management"
3. Configure the endpoint path (e.g., /api/city_management)
4. Access the interactive API docs at: http://your-server/api/city_management/docs
"""

# Import necessary components
from . import endpoints
