# -*- coding: utf-8 -*-
from werkzeug import exceptions, url_decode
from werkzeug.datastructures import Headers
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from odoo.http import Controller, route, request
from odoo.tools import html_escape
from odoo.addons.web.controllers.main import _serialize_exception, content_disposition
from odoo.tools.safe_eval import safe_eval

import base64

class Binary(Controller):
	@route('/report/text', type='http', auth="public")
	def download_document(self,model,field,id,filename=None, **kw):
		Model = request.env[model]
		#invoice_number = Model.browse(int(id)).number
		invoice_number = id
		filecontent = base64.b64decode(Model.get_file_content(int(id)))
		if not filecontent:
			return request.not_found()
		else:
			if not filename:
				#filename = '%s.%s' % (invoice_number,'txt')
				filename = Model.get_file_name(int(id))
				return request.make_response(filecontent,
						[('Content-Type', 'application/octet-stream'),
						('Content-Disposition', content_disposition(filename))])