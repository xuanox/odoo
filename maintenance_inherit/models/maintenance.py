# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    teamviewer_id = fields.Char('Id TeamViewer')
    teamviewer_password = fields.Char('Password Teamviewer')

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    maintenance_type = fields.Selection([('corrective', 'Corrective'), ('preventive', 'Preventive'), ('request', 'Request'), ('quotation', 'Quotation'),('installation', 'Installation')], string='Maintenance Type', default="corrective")
    tag_ids = fields.Many2many('maintenance.tag', string='Tags')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} ({})".format(record.name, record.id)))
        return result

class MaintenanceTag(models.Model):
    _name = 'maintenance.tag'
    _description = 'Maintenance Tags'
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer('Color')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
