# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo import tools
from odoo.tools.translate import _
from odoo.addons.website_form.controllers.main import WebsiteForm


class WebsiteForm(WebsiteForm):

    @http.route('''/helpdesk/<model("helpdesk.team", "[('use_website_helpdesk_form','=',True)]"):team>/submit''', type='http', auth="public", website=True)
    def web_helpdesk_form(self, team, **kwargs):
        if not team.active or not team.website_published:
            return request.render("website_helpdesk.not_published_any_team")
        default_values = {}
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            default_values['name'] = request.env.user.partner_id.name
            default_values['email'] = request.env.user.partner_id.email
        return request.render("web_helpdesk_form.ticket_submit", {'team': team, 'default_values': default_values})

    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        if request.params.get('partner_email'):
            Partner = request.env['res.partner'].sudo().search([('email', '=', kwargs.get('partner_email'))], limit=1)
            if Partner:
                request.params['partner_id'] = Partner.id
        return super(WebsiteForm, self).website_form(model_name, **kwargs)

    #data post
    MANDATORY_BILLING_FIELDS = ["name"]
    @http.route('/intervention/request/success', type='http', auth='user', website=True)
    def navigate_to_success_page(self):
        user = http.request.env.context.get('uid')
        parent = request.env.user.parent_id.id
        parent_name = request.env.user.parent_id.name
        values = {
            'user': user,
            'parent': parent,
            'parent_name': parent_name,
        }
        return http.request.render('web_helpdesk_form.succes_page', values)

    @http.route('/intervention/request/error', type='http', auth='user', website=True)
    def navigate_to_error_page(self):
        user = http.request.env.context.get('uid')
        parent = request.env.user.parent_id.id
        parent_name = request.env.user.parent_id.name
        values = {
            'user': user,
            'parent': parent,
            'parent_name': parent_name,
        }
        return http.request.render('web_helpdesk_form.error_page', values)

    @http.route(['/intervention/request'], type='http', auth='user', website=True)
    def register(self, redirect=None, **post):
        team_id = request.env['helpdesk.team'].sudo().search([('id','=',post.get('equipment_id.team_id.id'))])
        partner_name = request.env.user.partner_id.name
        partner_email = request.env.user.partner_id.email
        user = request.env.user.id
        parent = request.env.user.parent_id.id
        parent_name = request.env.user.parent_id.name
        equipments = request.env['equipment.equipment'].sudo().search([('client_id.id','=',parent)])
        ticket_type = request.env['helpdesk.ticket.type'].sudo().search([])
        equipment_states = request.env['equipment.state'].sudo().search([('team','=',3)])

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
            'ticket_type' : ticket_type,
            'equipment_states' : equipment_states,
            'user': user,
            'create_uid': user,
            'parent': parent,
            'parent_name': parent_name,
            'partner_name': partner_name,
            'partner_email': partner_email,
            'team_id': team_id,
            }
        return request.render("web_helpdesk_form.request", values)


    def _process_registration(self, post):
        equipment_id = post.get('equipment_id')
        equipments = request.env['equipment.equipment'].sudo().search([('id','=',equipment_id)])
        request.env['helpdesk.ticket'].sudo().create({
            'name' : post.get('name'),
            'equipment_id': post.get('equipment_id'),
            'ticket_type_id': post.get('ticket_type_id'),
            'description': post.get('description'),
            'create_uid':post.get('user'),
            'partner_id':request.env.user.partner_id.id,
            'team_id': equipments.team_id.id,
        })
        equipments = request.env['equipment.equipment'].browse(post.get('equipment_id'))
        equipments.write({'maintenance_state_id': post.get('equipment_state_id')})


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
