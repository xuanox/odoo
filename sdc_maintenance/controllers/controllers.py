# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo import tools
from odoo.tools.translate import _


class OpenMaintenance(http.Controller):
    @http.route('/intervention', type='http', auth='user', website=True)
    def navigate_to_intervention_page(self):
        user = http.request.env.context.get('uid')
        parent = request.env.user.parent_id.id
        intervention_ids = http.request.env['maintenance.intervention'].sudo().search([('x_client.id','=',parent)])
        return http.request.render('sdc_maintenance.intervention_page', {'intervention_ids': intervention_ids})
    
    @http.route('/pm', type='http', auth='user', website=True)
    def navigate_to_pm_page(self):
        user = http.request.env.context.get('uid')
        pm_ids = http.request.env['maintenance.request'].sudo().search([('technician_user_id','=',user),('maintenance_type','=','preventive')])
        return http.request.render('sdc_maintenance.pm_page', {'pm_ids': pm_ids})
    
    @http.route('/cm', type='http', auth='user', website=True)
    def navigate_to_cm_page(self):
        user = http.request.env.context.get('uid')
        cm_ids = http.request.env['maintenance.request'].sudo().search([('technician_user_id','=',user),('maintenance_type','=','corrective')])
        return http.request.render('sdc_maintenance.cm_page', {'cm_ids': cm_ids})  
    
    @http.route('/wo', type='http', auth='user', website=True)
    def navigate_to_wo_page(self):
        user = http.request.env.context.get('uid')
        wo_ids = http.request.env['maintenance.order'].sudo().search([('technician_id','=',user)])
        return http.request.render('sdc_maintenance.wo_page', {'wo_ids': wo_ids})
    
    #data post
    MANDATORY_BILLING_FIELDS = ["motif","equipment_id"]
    @http.route('/intervention/request/success', type='http', auth='public', website=True)
    def navigate_to_success_page(self):
        return http.request.render('sdc_maintenance.succes_page', {})

    @http.route('/intervention/request/error', type='http', auth='public', website=True)
    def navigate_to_error_page(self):
        return http.request.render('sdc_maintenance.error_page', {})
           
    @http.route(['/intervention/request'], type='http', auth='user', website=True)
    def register(self, redirect=None, **post):    
        user = http.request.env.context.get('uid')
        parent = request.env.user.parent_id.id
        equipments = request.env['maintenance.equipment'].sudo().search([('x_studio_cliente.id','=',parent)])
        zones = request.env['maintenance.zone'].sudo().search([])
        partners = request.env['res.partner'].sudo().search([])
        categories = request.env['maintenance.equipment.category'].sudo().search([])
        failures = request.env['maintenance.failure'].sudo().search([])
        priorities = ['0', '1','2','3']
        equip_states = ['start', 'stop']
    
        values = {
            'error': {},
            'error_message': []
        }
    
        if post:
            error, error_message = self._form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if error:  
                return request.redirect('/intervention/request/error')
            if not error:
                self._process_registration(post)
                return request.redirect('/intervention/request/success')

        values = {
            'equipments' : equipments,
            'priorities' : priorities,
            'equip_states' : equip_states,
            'zones' : zones,
            'partners' : partners,
            'categories' : categories,
            'failures' : failures,
            'user': user,
            'parent': parent,
            
        }    
        return request.render("sdc_maintenance.request", values)
    
    
    def _process_registration(self, post):
        request.env['maintenance.intervention'].sudo().create({
            'category_id' : post.get('category_id'),
            'equipment_id': post.get('equipment_id'),
            'motif': post.get('motif'),
            'priority': post.get('priority'),
            'failure_type': post.get('failure_type'),
            'partner': post.get('partner_id'),
            'zone_id': post.get('zone_id'),
            'state_machine': post.get('state_id'),
            
    })
    

    def _form_validate(self, data):
        error = dict()
        error_message = []

        # Validation
        for field_name in self.MANDATORY_BILLING_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message
    
