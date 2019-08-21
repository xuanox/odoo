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
        parent_name = request.env.user.parent_id.name
        intervention_ids = http.request.env['helpdesk.ticket'].sudo().search([('client_id.id','=',parent)])
        values = {
            'user': user,
            'create_uid': user,
            'parent': parent,
            'parent_name': parent_name,
            'intervention_ids': intervention_ids,
        }
        return http.request.render('helpdesk_technical_support.intervention_page', values)

    @http.route('/pm', type='http', auth='user', website=True)
    def navigate_to_pm_page(self):
        user = http.request.env.context.get('uid')
        parent = request.env.user.parent_id.id
        parent_name = request.env.user.parent_id.name
        pm_ids = http.request.env['helpdesk.ticket'].sudo().search([('client_id.id','=',parent)])
        values = {
            'user': user,
            'parent': parent,
            'parent_name': parent_name,
            'pm_ids': pm_ids,
        }
        return http.request.render('helpdesk_technical_support.pm_page', values)

    @http.route('/cm', type='http', auth='user', website=True)
    def navigate_to_cm_page(self):
        user = http.request.env.context.get('uid')
        parent = request.env.user.parent_id.id
        parent_name = request.env.user.parent_id.name
        cm_ids = http.request.env['helpdesk.ticket'].sudo().search([('client_id.id','=',parent)])
        values = {
            'user': user,
            'parent': parent,
            'parent_name': parent_name,
            'cm_ids': cm_ids,
        }
        return http.request.render('helpdesk_technical_support.cm_page', values)

    @http.route('/wo', type='http', auth='user', website=True)
    def navigate_to_wo_page(self):
        user = http.request.env.context.get('uid')
        parent = request.env.user.parent_id.id
        parent_name = request.env.user.parent_id.name
        wo_ids = http.request.env['helpdesk.ticket'].sudo().search([('client_id.id','=',parent)])
        return http.request.render('helpdesk_technical_support.wo_page', {'wo_ids': wo_ids})

    MANDATORY_BILLING_FIELDS = ["motif","equipment_id"]
    @http.route('/intervention/request/success', type='http', auth='public', website=True)
    def navigate_to_success_page(self):
        user = http.request.env.context.get('uid')
        parent = request.env.user.parent_id.id
        parent_name = request.env.user.parent_id.name
        values = {
            'user': user,
            'parent': parent,
            'parent_name': parent_name,
        }
        return http.request.render('helpdesk_technical_support.succes_page', values)

    @http.route('/intervention/request/error', type='http', auth='public', website=True)
    def navigate_to_error_page(self):
        user = http.request.env.context.get('uid')
        parent = request.env.user.parent_id.id
        parent_name = request.env.user.parent_id.name
        values = {
            'user': user,
            'parent': parent,
            'parent_name': parent_name,
        }
        return http.request.render('helpdesk_technical_support.error_page', values)

    @http.route(['/intervention/request'], type='http', auth='user', website=True)
    def register(self, redirect=None, **post):
        user = request.env.user.id
        parent = request.env.user.parent_id.id
        parent_name = request.env.user.parent_id.name
        equipments = request.env['equipment.equipment'].sudo().search([('client_id.id','=',parent)])
        equip_states = request.env['asset.state'].sudo().search([('team','=',3)])
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
            'equip_states' : equip_states,
            'user': user,
            'create_uid': user,
            'parent': parent,
            'parent_name': parent_name,

        }
        return request.render("helpdesk_technical_support.request", values)


    def _process_registration(self, post):
        request.env['helpdesk.ticket'].sudo().create({
            'equipment_id': post.get('equipment_id'),
            'description': post.get('motif'),
            'name': post.get('name'),
            'create_uid':post.get('user'),
    })


    def _form_validate(self, data):
        error = dict()
        error_message = []


        for field_name in self.MANDATORY_BILLING_FIELDS:
            if not data.get(field_name):
                error[field_name] = 'missing'


        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        return error, error_message
