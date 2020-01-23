# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2018 emsa (<http://www.electronicamedica.com>).
#
##############################################################################

from odoo import tools
from odoo import api, fields, models, SUPERUSER_ID, _, exceptions
import time
import datetime as dt
import time, datetime
from datetime import date
from datetime import datetime
from dateutil import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import *
import logging
import math
from datetime import datetime, time
from pytz import timezone, UTC
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.translate import _

STATE_COLOR_SELECTION = [
    ('0', 'Red'),
    ('1', 'Green'),
    ('2', 'Blue'),
    ('3', 'Yellow'),
    ('4', 'Magenta'),
    ('5', 'Cyan'),
    ('6', 'Black'),
    ('7', 'White'),
    ('8', 'Orange'),
    ('9', 'SkyBlue')
]

class equipment_state(models.Model):
    """
    Model for Equipment states.
    """
    _name = 'equipment.state'
    _description = 'State of equipment'
    _order = "sequence"

    STATE_SCOPE_TEAM = [
        ('0', 'Finance'),
        ('1', 'Warehouse'),
        ('2', 'Manufacture'),
        ('3', 'Maintenance'),
        ('4', 'Accounting')
    ]

    name = fields.Char('State', size=64, required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order states.", default=1)
    state_color = fields.Selection(STATE_COLOR_SELECTION, 'State Color')
    team = fields.Selection(STATE_SCOPE_TEAM, 'Scope Team')

    def change_color(self):
        color = int(self.state_color) + 1
        if (color>9): color = 0
        return self.write({'state_color': str(color)})

class equipment_category(models.Model):
    _description = 'Equipment Tags'
    _name = 'equipment.category'

    name = fields.Char('Tag', required=True, translate=True)
    equipment_ids = fields.Many2many('equipment.equipment', id1='category_id', id2='equipment_id', string='Equipments')

class equipment_equipment(models.Model):
    _name = 'equipment.equipment'
    _description = 'Equipment'
    _inherit =  ['mail.thread', 'mail.activity.mixin']
    _order = "modality_id"

    def _read_group_state_ids(self, domain, read_group_order=None, access_rights_uid=None, team='3'):
        access_rights_uid = access_rights_uid or self.uid
        stage_obj = self.env['equipment.state']
        order = stage_obj._order
        # lame hack to allow reverting search, should just work in the trivial case
        if read_group_order == 'stage_id desc':
            order = "%s desc" % order
        # write the domain
        # - ('id', 'in', 'ids'): add columns that should be present
        # - OR ('team','=',team): add default columns that belongs team
        search_domain = []
        search_domain += ['|', ('team','=',team)]
        search_domain += [('id', 'in', ids)]
        stage_ids = stage_obj._search(search_domain, order=order, access_rights_uid=access_rights_uid)
        result = stage_obj.name_get(access_rights_uid, stage_ids)
        # restore order of the search
        result.sort(lambda x,y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))
        return result, {}

    def _read_group_finance_state_ids(self, domain, read_group_order=None, access_rights_uid=None):
        return self._read_group_state_ids(domain, read_group_order, access_rights_uid, '0')

    def _read_group_warehouse_state_ids(self, domain, read_group_order=None, access_rights_uid=None):
        return self._read_group_state_ids(domain, read_group_order, access_rights_uid, '1')

    def _read_group_manufacture_state_ids(self, domain, read_group_order=None, access_rights_uid=None):
        return self._read_group_state_ids(domain, read_group_order, access_rights_uid, '2')

    def _read_group_maintenance_state_ids(self, domain, read_group_order=None, access_rights_uid=None):
        return self._read_group_state_ids(domain, read_group_order, access_rights_uid, '3')

    def _read_group_accounting_state_ids(self, domain, read_group_order=None, access_rights_uid=None):
        return self._read_group_state_ids(domain, read_group_order, access_rights_uid, '4')

    CRITICALITY_SELECTION = [
        ('0', 'General'),
        ('1', 'Important'),
        ('2', 'Very important'),
        ('3', 'Critical')
    ]

    name = fields.Char('Equipment Name', size=64, required=True, translate=True)
    finance_state_id = fields.Many2one('equipment.state', 'State Finance', domain=[('team','=','0')])
    warehouse_state_id = fields.Many2one('equipment.state', 'State Warehouse', domain=[('team','=','1')])
    manufacture_state_id = fields.Many2one('equipment.state', 'State Manufacture', domain=[('team','=','2')])
    maintenance_state_id = fields.Many2one('equipment.state', 'State Maintenance', domain=[('team','=','3')], track_visibility='onchange')
    accounting_state_id = fields.Many2one('equipment.state', 'State Accounting', domain=[('team','=','4')])
    maintenance_state_color = fields.Selection(related='maintenance_state_id.state_color', selection=STATE_COLOR_SELECTION, string="Color", readonly=True)
    criticality = fields.Selection(CRITICALITY_SELECTION, 'Criticality')
    property_stock_equipment = fields.Many2one(
        'stock.location', "Equipment Location",
        company_dependent=True, domain=[('usage', 'like', 'equipment')],
        help="This location will be used as the destination location for installed parts during equipment life.")
    user_id = fields.Many2one('res.users', 'Assigned to', track_visibility='onchange')
    active = fields.Boolean('Active', default=True)
    equipment_number = fields.Char('Equipment Number', size=64, copy=False)
    model = fields.Char('Model', size=64)
    serial = fields.Char('Serial no.', size=64, required=True, track_visibility='onchange')
    n_active = fields.Char('Active no.', size=64)
    software_v = fields.Char('Software Versión.', size=64)
    hardware_v = fields.Char('Hardware Versión.', size=64)
    location = fields.Char('Location')
    provider_id = fields.Many2one('res.partner', 'Provider')
    vendor_id = fields.Many2one('res.partner', 'Commercial')
    manufacturer_id = fields.Many2one('res.partner', 'Manufacturer')
    start_date = fields.Date('Start Date')
    instalation_date = fields.Date('Instalation Date')
    purchase_date = fields.Date('Purchase Date')
    warranty_start_date = fields.Date('Warranty Start')
    warranty_end_date = fields.Date('Warranty End')
    dealer_warranty_start_date = fields.Date('Dealer Warranty Start')
    dealer_warranty_end_date = fields.Date('Dealer Warranty End')
    image = fields.Binary("Image")
    image_small = fields.Binary("Small-sized image")
    image_medium = fields.Binary("Medium-sized image")
    category_ids = fields.Many2many('equipment.category', id1='equipment_id', id2='category_id', string='Tags')

    brand_id=fields.Many2one('equipment.brand', string='Brand', required=True, track_visibility='onchange')
    zone_id=fields.Many2one('equipment.zone', string='Zone', required=True, track_visibility='onchange')
    client_id=fields.Many2one('res.partner', string='Client', required=True, track_visibility='onchange')
    model_id=fields.Many2one('equipment.model', string='Models', required=True, track_visibility='onchange')
    parent_id=fields.Many2one('equipment.equipment', string='Equipment Relation')
    modality_id=fields.Many2one('equipment.modality', string='Modality', required=True, track_visibility='onchange')

    software_ids=fields.One2many('equipment.software.list','equipment_id',u'Softwares')
    network_ids=fields.One2many('equipment.network','equipment_id',u'Networks')
    dicom_ids=fields.One2many('equipment.dicom','equipment_id',u'Dicom')
    child_ids=fields.One2many('equipment.equipment','parent_id',u'Accesory')
    history_state_ids=fields.One2many('equipment.history.state','equipment_id', string='State History')

    date_start = fields.Datetime('Start', copy=False, index=True, readonly=True)
    date_finished = fields.Datetime('End', copy=False, index=True, readonly=True)

    effective_start_date = fields.Date('Effective Start Date', default=fields.Date.context_today, required=True, help="Date at which the equipment became effective. This date will be used to compute Maintenance.")
    effective_date = fields.Datetime('Effective Date', default=datetime.today(), required=True, help="Date at which the equipment became effective. This date will be used to compute the Mean Time Between Failure.")
    expected_mtbf = fields.Integer(string='Expected MTBF', help='Expected Mean Time Between Failure')
    mtbf = fields.Integer(compute='_compute_state_history', string='MTBF', help='Mean Time Between Failure, computed based on done corrective maintenances.')
    mttr = fields.Integer(compute='_compute_state_history', string='MTTR', help='Mean Time To Repair')
    estimated_next_failure = fields.Datetime(compute='_compute_state_history', string='Estimated time before next failure (in days)', help='Computed as Latest Failure Date + MTBF')
    latest_failure_date = fields.Datetime(compute='_compute_state_history', string='Latest Failure Date')

    assign_date = fields.Date('Assigned Date', track_visibility='onchange')
    cost = fields.Float('Cost')

    _group_by_full = {
        'finance_state_id': _read_group_finance_state_ids,
        'warehouse_state_id': _read_group_warehouse_state_ids,
        'manufacture_state_id': _read_group_manufacture_state_ids,
        'maintenance_state_id': _read_group_maintenance_state_ids,
        'accounting_state_id': _read_group_accounting_state_ids,
    }

    @api.multi
    def _compute_state_history(self):
        for equipment in self:
            state_history = equipment.history_state_ids.filtered(lambda x: x.ticket_id != 0 and x.duration != 0)
            mttr_days = 0
            for state in state_history:
                if state.duration and state.date_end:
                    mttr_days += (state.date_end - state.date_start).days
            equipment.mttr = len(state_history) and (mttr_days / len(state_history)) or 0
            state = state_history.sorted(lambda x: x.date_start)
            if len(state) >= 1:
                equipment.mtbf = (state[-1].date_start - equipment.effective_date).days / len(state)
            equipment.latest_failure_date = state and state[-1].date_start or False
            if equipment.mtbf:
                equipment.estimated_next_failure = equipment.latest_failure_date + relativedelta(days=equipment.mtbf)
            else:
                equipment.estimated_next_failure = False

    # CRUD
    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        if vals.get('equipment_number','/')=='/':
            vals['equipment_number'] = self.env['ir.sequence'].next_by_code('equipment.equipment') or '/'
        return super(equipment_equipment, self).create(vals)

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        return super(equipment_equipment, self).write(vals)

    @api.model
    def _read_group_modality_ids(self, modalities, domain, order):
        """ Read group customization in order to display all the categories in
            the kanban view, even if they are empty.
        """
        modality_ids = modalities._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return modalities.browse(modality_ids)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} ({})".format(record.name, record.serial)))
        return result


class EquipmentBrand(models.Model):
    _name = 'equipment.brand'
    _description = 'Brand'
    _order = 'name asc'

    name=fields.Char('Brand',required=True)
    code=fields.Char('Reference Brand')
    manager_id=fields.Many2one('res.partner','Provider')
    description=fields.Text('Description')

class EquipmentSoftwareType(models.Model):
    _name = 'equipment.software.type'
    _description = 'Software Type'
    _order = 'name asc'

    name=fields.Char('Software Type',required=True)
    code=fields.Char('Reference Software Type')
    description=fields.Text('Description')

class EquipmentZone(models.Model):
    _name = 'equipment.zone'
    _description = 'Zone'
    _order = 'name asc'

    name=fields.Char('Zone',required=True)
    code=fields.Char('Reference de zone')
    manager_id=fields.Many2one('res.users','Responsible')
    description=fields.Text('Description')

class EquipmentDicomType(models.Model):
    _name = 'equipment.dicom.type'
    _description = 'Dicom Type'
    _order = 'name asc'

    name=fields.Char('Dicom Type',required=True)
    code=fields.Char('Reference Dicom Type')
    description=fields.Text('Description')

class EquipmentModel(models.Model):
    _name = 'equipment.model'
    _description = 'Model'
    _order = 'name asc'

    name=fields.Char('Model',required=True)
    code=fields.Char('Reference Model')
    brand_id=fields.Many2one('equipment.brand','Brand')
    description=fields.Text('Description')

class EquipmentSoftware(models.Model):
    _name = 'equipment.software'
    _description = 'Software'
    _order = 'name asc'

    name=fields.Char('Software',required=True)
    version=fields.Char('Version')
    software_type_id=fields.Many2one('equipment.software.type','Software Type')
    description=fields.Text('Description')

class EquipmentSoftwareList(models.Model):
    _name = 'equipment.software.list'
    _description = 'Software List'
    _order = 'name asc'

    name=fields.Char('License',required=True)
    software_id=fields.Many2one('equipment.software','Software')
    equipment_id=fields.Many2one('equipment.equipment','Equipment')
    description=fields.Text('Description')

class EquipmentNetwork(models.Model):
    _name = 'equipment.network'
    _description = 'Network'
    _order = 'name asc'

    name=fields.Char('IP',required=True)
    subred=fields.Char('SubRed',required=True)
    gateway=fields.Char('Gateway',required=True)
    dns1=fields.Char('Dns1')
    dns2=fields.Char('Dns2')
    mac_address=fields.Char('Mac Address')
    equipment_id=fields.Many2one('equipment.equipment','Equipment')
    description=fields.Text('Description')

class EquipmentDicom(models.Model):
    _name = 'equipment.dicom'
    _description = 'Dicom'
    _order = 'name asc'

    name=fields.Char('AeTitle',required=True)
    ip=fields.Char('Ip',required=True)
    port=fields.Char('Port',required=True)
    equipment_id=fields.Many2one('equipment.equipment','Equipment')
    dicom_type_id=fields.Many2one('equipment.dicom.type','Dicom Type')
    description=fields.Text('Description')

class EquipmentModality(models.Model):
    _name = 'equipment.modality'
    _description = 'Modality'
    _order = 'name asc'

    name = fields.Char('Modality Name', required=True, translate=True)
    color = fields.Integer('Color Index')
    note = fields.Text('Comments', translate=True)
    equipment_ids = fields.One2many('equipment.equipment', 'modality_id', string='Equipments', copy=False)

class EquipmentHistoryState(models.Model):
    _name = 'equipment.history.state'
    _description = 'Equipment History State'

    name = fields.Char('Refernce', required=True, translate=True)
    equipment_id = fields.Many2one('equipment.equipment', string='Equipment', required=True)
    equipment_state_id = fields.Many2one('equipment.state', string='Equipment State', domain=[('team','=','3')])
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True)
    date_start = fields.Datetime('Start Date', default=fields.Datetime.now, required=True)
    date_end = fields.Datetime('End Date')
    duration = fields.Float('Duration', compute='_compute_duration', store=True)
    user_id = fields.Many2one(
        'res.users', "User",
        default=lambda self: self.env.uid)

    @api.depends('date_end', 'date_start')
    def _compute_duration(self):
        for blocktime in self:
            if blocktime.date_end:
                d1 = fields.Datetime.from_string(blocktime.date_start)
                d2 = fields.Datetime.from_string(blocktime.date_end)
                diff = d2 - d1
                blocktime.duration = round(diff.total_seconds() / 60.0, 2)
            else:
                blocktime.duration = 0.0
