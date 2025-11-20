# addons/aero_compliance/models/aircraft.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AeroAircraft(models.Model):
    _name = "aero.aircraft"
    _description = "Aircraft"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name asc"

    # ✅ Tail Number ما يتعاودش
    _sql_constraints = [
        (
            "aero_aircraft_name_unique",
            "unique(name)",
            "Tail Number must be unique!",
        ),
    ]

    # Identification
    name = fields.Char(
        string="Tail Number",
        required=True,
        tracking=True,
        index=True,
    )
    type = fields.Char(
        string="Type/Model",
        tracking=True,
    )
    entry_into_service = fields.Date(
        string="Entry Into Service",
        tracking=True,
    )

    # Utilisation globale
    total_hours = fields.Float(
        string="Total Flight Hours",
        digits=(10, 2),
        tracking=True,
    )
    total_cycles = fields.Integer(
        string="Total Cycles",
        tracking=True,
    )

    # Relation avec les composants
    component_ids = fields.One2many(
        comodel_name="aero.component",
        inverse_name="aircraft_id",
        string="Components",
    )

    # Nombre de compliance liés
    compliance_count = fields.Integer(
        string="Compliance Count",
        compute="_compute_compliance_count",
        store=True,
    )

    @api.depends("component_ids")
    def _compute_compliance_count(self):
        Compliance = self.env["aero.compliance"]
        for rec in self:
            rec.compliance_count = Compliance.search_count(
                [("aircraft_id", "=", rec.id)]
            )

    def action_open_compliance(self):
        self.ensure_one()
        return {
            "name": _("Compliance"),
            "type": "ir.actions.act_window",
            "res_model": "aero.compliance",
            "view_mode": "tree,form",
            "domain": [("aircraft_id", "=", self.id)],
            "target": "current",
        }

    def action_add_aircraft(self):
        """
        زر Add Aircraft:
        يفتح فورم جديد فاضي (ما يعمّرش نفس الداتا).
        """
        return {
            "type": "ir.actions.act_window",
            "name": _("New Aircraft"),
            "res_model": "aero.aircraft",
            "view_mode": "form",
            "target": "current",
            "context": {},  # نخليه فاضي باش الكل يرجع بلانك
        }
