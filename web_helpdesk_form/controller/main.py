# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
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


    @http.route(['/intervention/request'], type='http', auth='public', website=True)
    def register(self, redirect=None, **post):
        partner_name = request.env.user.partner_id.name
        partner_email = request.env.user.partner_id.email
        user = request.env.user.id
        parent = request.env.user.parent_id.id
        parent_name = request.env.user.parent_id.name
        equipments = request.env['equipment.equipment'].sudo().search([('client_id.id','=',parent)])
        values = {
            'equipments' : equipments,
            'user': user,
            'create_uid': user,
            'parent': parent,
            'parent_name': parent_name
            }
        return request.render("web_helpdesk_form.request", values)


    def _process_registration(self, post):
        request.env['helpdesk'].sudo().create({
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
