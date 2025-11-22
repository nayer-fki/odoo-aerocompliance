# addons/aero_compliance/__manifest__.py
# -*- coding: utf-8 -*-
{
    "name": "AeroCompliance",
    "summary": "Airworthiness & Compliance for Aeronautics (AD/SB, LLP, Certificates)",
    "version": "17.0.1.0.0",
    "category": "Operations/Maintenance",
    "author": "Nayer",
    "website": "https://example.com",
    "license": "LGPL-3",
    "depends": ["base", "maintenance", "stock", "hr", "project", "account"],
    "data": [
        "security/ir.model.access.csv",
        # VIEWS (actions + vues)
        "views/aircraft_views.xml",
        "views/component_views.xml",
        "views/ad_sb_views.xml",
        "views/compliance_views.xml",
        # MENUS (en DERNIER)
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
}
