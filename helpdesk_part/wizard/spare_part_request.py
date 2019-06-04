# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2018 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class Part(models.TransientModel):
    _inherit = 'part.order'

class PartLine(models.TransientModel):
    _inherit = 'part.line'
