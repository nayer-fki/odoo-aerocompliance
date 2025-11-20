#models/ad_sb.py
# -*- coding: utf-8 -*-
from odoo import models, fields


class AeroAdSb(models.Model):
    _name = "aero.ad_sb"
    _description = "Airworthiness Directive / Service Bulletin"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name asc, id asc"

    # Reference principale (AD / SB number)
    name = fields.Char("Reference", required=True, index=True, tracking=True)

    authority = fields.Selection(
        [
            ("easa", "EASA"),
            ("faa", "FAA"),
            ("other", "Other"),
        ],
        string="Issuing Authority",
        default="easa",
        required=True,
        tracking=True,
    )

    applicability = fields.Selection(
        [
            ("aircraft", "Aircraft"),
            ("component", "Component"),
        ],
        string="Applicability",
        default="aircraft",
        required=True,
        tracking=True,
    )

    description = fields.Text("Description / Applicability Details")

    # Conditions d'échéance (simplifiées)
    due_hours = fields.Float("Due at Hours", digits=(10, 2))
    due_cycles = fields.Integer("Due at Cycles")
    due_date = fields.Date("Due Date")

    status = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="open",
        tracking=True,
    )

    attachment = fields.Binary("Attachment")
    attachment_filename = fields.Char("Attachment Filename")

    _sql_constraints = [
        ("uniq_ad_sb_ref", "unique(name)", "This AD/SB reference already exists."),
    ]
