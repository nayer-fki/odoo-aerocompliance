# addons/aero_compliance/models/component.py
# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class AeroComponent(models.Model):
    _name = "aero.component"
    _description = "Aircraft Component"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "display_name"
    _order = "pn asc, sn asc, id asc"

    # ✅ ممنوع نفس الـ PN + SN يتعاودوا
    _sql_constraints = [
        (
            "aero_component_pn_sn_unique",
            "unique(pn, sn)",
            "A component with this Part Number and Serial Number already exists.",
        ),
    ]

    # Identité
    pn = fields.Char("Part Number", required=True, index=True, tracking=True)
    sn = fields.Char("Serial Number", index=True, tracking=True)
    display_name = fields.Char(
        string="Component",
        compute="_compute_display_name",
        store=True,
        readonly=True,
    )

    # Montage
    aircraft_id = fields.Many2one(
        "aero.aircraft",
        string="Installed On",
        tracking=True,
    )
    install_date = fields.Date("Install Date")

    # Compteurs
    hours_since_new = fields.Float(
        "Hours Since New",
        digits=(10, 2),
        default=0.0,
    )
    cycles_since_new = fields.Integer(
        "Cycles Since New",
        default=0,
    )
    llp_limit_hours = fields.Float(
        "Life Limit (Hours)",
        digits=(10, 2),
        default=0.0,
    )
    llp_limit_cycles = fields.Integer(
        "Life Limit (Cycles)",
        default=0,
    )

    # Pièces jointes
    certificate = fields.Binary("Certificate (Form 1 / 8130-3)")
    certificate_filename = fields.Char("Certificate Filename")

    # === LLP Monitoring ===
    remaining_hours = fields.Float(
        "Remaining Hours",
        compute="_compute_remaining_life",
        store=True,
    )
    remaining_cycles = fields.Integer(
        "Remaining Cycles",
        compute="_compute_remaining_life",
        store=True,
    )
    status = fields.Selection(
        [
            ("serviceable", "Serviceable 🟢"),
            ("warning", "Warning 🟡"),
            ("expired", "Expired 🔴"),
        ],
        string="Status",
        compute="_compute_remaining_life",
        store=True,
    )

    @api.depends("pn", "sn")
    def _compute_display_name(self):
        for r in self:
            pn = r.pn or ""
            sn = r.sn or ""
            if pn and sn:
                r.display_name = f"{pn} / {sn}"
            else:
                r.display_name = pn or sn or "Component"

    @api.depends(
        "hours_since_new",
        "cycles_since_new",
        "llp_limit_hours",
        "llp_limit_cycles",
    )
    def _compute_remaining_life(self):
        """
        remaining = max(limit - used, 0)
        status:
          - expired إذا واحد من الباقي وصل 0
          - warning إذا أقل من 10%
          - serviceable otherwise
        """
        for r in self:
            # Heures
            if r.llp_limit_hours and r.llp_limit_hours > 0:
                rem_h = max(r.llp_limit_hours - (r.hours_since_new or 0.0), 0.0)
            else:
                rem_h = 0.0

            # Cycles
            if r.llp_limit_cycles and r.llp_limit_cycles > 0:
                rem_c = max(r.llp_limit_cycles - (r.cycles_since_new or 0), 0)
            else:
                rem_c = 0

            r.remaining_hours = rem_h
            r.remaining_cycles = rem_c

            if r.llp_limit_hours or r.llp_limit_cycles:
                expired = (r.llp_limit_hours and rem_h <= 0) or (
                    r.llp_limit_cycles and rem_c <= 0
                )
                if expired:
                    r.status = "expired"
                else:
                    warn_h = (
                        r.llp_limit_hours
                        and r.llp_limit_hours > 0
                        and rem_h <= 0.1 * r.llp_limit_hours
                    )
                    warn_c = (
                        r.llp_limit_cycles
                        and r.llp_limit_cycles > 0
                        and rem_c <= int(0.1 * r.llp_limit_cycles)
                    )
                    r.status = "warning" if (warn_h or warn_c) else "serviceable"
            else:
                r.status = "serviceable"

    def action_new_component(self):
        """
        زر Add Component:
        يفتح فورم جديد، نفس الـ Aircraft (لو موجود)،
        وباقي الشامب كلهم فاضين.
        """
        self.ensure_one()
        return {
            "name": _("New Component"),
            "type": "ir.actions.act_window",
            "res_model": "aero.component",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_aircraft_id": self.aircraft_id.id or False,
            },
        }
