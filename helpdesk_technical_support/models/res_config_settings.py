# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_mailgateway = fields.Boolean(string='New Ticket Notification', config_parameter='helpdesk.use_mailgateway')
    new_ticket_notification_mail = fields.Char(string='New Ticket Notification Mail')
