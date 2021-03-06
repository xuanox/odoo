# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models


class TechnicalSupportOrder(models.Model):
    _inherit = "technical_support.order"
    tracking_fields = ['state', 'user_id']

class TechnicalSupportRequest(models.Model):
    _inherit = "technical_support.request"
    tracking_fields = ['state', 'user_id']

class Part(models.Model):
    _inherit = "part.order"
    tracking_fields = ['state', 'user_id']


class RegulatoryTechnicalFileCreation(models.Model):
    _inherit = "regulatory.technical.file.creation"
    tracking_fields = ['state', 'user_id']

class RegulatoryTechnicalFileModification (models.Model):
    _inherit = "regulatory.technical.file.modification"
    tracking_fields = ['state', 'user_id']

class RegulatoryTechnicalFileRegistry(models.Model):
    _inherit = "regulatory.technical.file.registry"
    tracking_fields = ['state', 'user_id']

class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"
    tracking_fields = ['stage_id', 'user_id']
