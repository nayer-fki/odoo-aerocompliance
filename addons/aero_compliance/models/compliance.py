# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AeroCompliance(models.Model):
    _name = "aero.compliance"
    _description = "Compliance Task / Record"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_planned asc, id asc"

    name = fields.Char("Title", required=True, default="Compliance Task", tracking=True)
    aircraft_id = fields.Many2one(
        "aero.aircraft", string="Aircraft", tracking=True
    )
    component_id = fields.Many2one(
        "aero.component", string="Component", tracking=True,
        domain="[('aircraft_id', '=', aircraft_id)]"
    )
    ad_sb_id = fields.Many2one("aero.ad_sb", string="AD/SB", tracking=True)

    date_planned = fields.Date("Planned Date", tracking=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
        index=True,
    )

    technician_id = fields.Many2one("hr.employee", string="Technician", tracking=True)
    qa_user_id = fields.Many2one("res.users", string="QA Approver", tracking=True)

    evidence = fields.Binary("Evidence (CRS)")
    evidence_filename = fields.Char("Evidence Filename")

    # --------- Actions ---------
    def action_start(self):
        for rec in self:
            if rec.state == "draft":
                rec.state = "in_progress"
        return True

    def action_done(self):
        for rec in self:
            if rec.state in ("draft", "in_progress"):
                rec.state = "done"
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "done":
                rec.state = "cancel"
        return True

    # --------- Constraints ---------
    @api.constrains("aircraft_id", "component_id")
    def _check_aircraft_or_component(self):
        for rec in self:
            # لازم إمّا aircraft **أو** component (واحد فقط)
            if bool(rec.aircraft_id) == bool(rec.component_id):
                raise ValidationError(
                    _(
                        "Select exactly one target: either an Aircraft or a Component."
                    )
                )

    # --------- Cron placeholder (يمشي مع data/cron.xml) ---------
    def _cron_remind_due(self):
        """Placeholder آمن: يكتب لوج فقط. نجمو لاحقًا نضيفوا Activities."""
        due = self.search([("state", "!=", "done"), ("date_planned", "!=", False)])
        _logger.info("[AeroCompliance] Cron check: %s records with a planned date.", len(due))
        return True
