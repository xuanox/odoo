# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2014-2018 emsa (<http://www.electronicamedica.com>).
#
##############################################################################

from odoo import api, fields, models, _


class EquipmentModality(models.Model):
    _inherit = 'equipment.modality'

    category_id=fields.Many2one('crm.lead.category', string='Sales Category')
