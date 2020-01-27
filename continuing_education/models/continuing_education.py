 # -*- coding: utf-8 -*-
 ###################################################################################
 #
 #    Electrónica Médica.
 #    Copyright (C) 2019-TODAY Electrónica Médica (<https://www.electronicamedica.com>).
 #
 #    Author: Aldhair Atencio (<https://www.electronicamedica.com>)
 #
 #    This program is free software: you can modify
 #    it under the terms of the GNU Affero General Public License (AGPL) as
 #    published by the Free Software Foundation, either version 3 of the
 #    License, or (at your option) any later version.
 #
 #    This program is distributed in the hope that it will be useful,
 #    but WITHOUT ANY WARRANTY; without even the implied warranty of
 #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 #    GNU Affero General Public License for more details.
 #
 #    You should have received a copy of the GNU Affero General Public License
 #    along with this program.  If not, see <https://www.gnu.org/licenses/>.
 #
 ###################################################################################

from datetime import date, datetime, timedelta
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class ContinuingEducationStage(models.Model):
    _name = 'continuing.education.stage'
    _description = 'Continuing Education Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Continuing Education Pipe')
    done = fields.Boolean('Request Done')

class ContinuingEducationType(models.Model):
    _name = 'continuing.education.type'
    _description = ' Continuing Education Type'
    _order = 'id'

    name = fields.Char(string="Type", required=True, translate=True)

class ContinuingEducation(models.Model):
    _name = 'continuing.education'
    _description = 'Continuing Education'
    _order = 'id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    #name = fields.Char(string="Asunto", required=True, translate=True)
    assigned_id = fields.Many2one('res.users', u'Assigned')
    user_id = fields.Many2one('res.users', string='Solicitado Por', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    type_id = fields.Many2one('continuing.education.type', u'Type')
    stage_id = fields.Many2one('continuing.education.stage', string='Stage')
    description=fields.Text('Description')
    observation=fields.Text('Observation')
