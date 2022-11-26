import os
import json
import base64
import logging
from werkzeug.urls import url_quote

from odoo import http, tools, _
from odoo.tools import ustr
from odoo.tools.mimetypes import guess_mimetype
from odoo.http import request

from .controller_mixin import WSDControllerMixin

_logger = logging.getLogger(__name__)


class WSDHelpers(WSDControllerMixin, http.Controller):

    def _get_max_upload_size(self):
        """ Get configuration for max upload size
        """
        return request.env.user.company_id._get_request_max_upload_file_size()

    def _get_allowed_upload_file_types(self):
        """ Get configuration for allowed upload file types
        """
        return request.env.user.company_id._get_allowed_upload_file_types()

    def _check_file_has_allowed_type(self, data):
        allowed_upload_file_types = self._get_allowed_upload_file_types()

        if not allowed_upload_file_types:
            return True
        mimetype = guess_mimetype(data or b'')
        match = False
        f_type, f_subtype = mimetype.split('/')
        for allowed_type in allowed_upload_file_types:
            _type, subtype = allowed_type.split('/')
            if subtype == '*':
                if _type == f_type:
                    match = True
                    break
            else:
                if _type == f_type and subtype == f_subtype:
                    match = True
                    break
        if match:
            return True

        _logger.warning(
            'Unsupported file format %s,'
            ' attachment only supports %s',
            mimetype,
            ', '.join(allowed_upload_file_types),
        )
        raise ValueError(_('Unsupported file format!'))

    @http.route('/crnd_wsd/file_upload', type='http',
                auth='user', methods=['POST'], website=True)
    def wsd_upload_file(self, upload, alt='File', filename=None,
                        is_image=False, **post_data):
        attachment_data = {
            'description': alt,
            'name': filename or 'upload',
            'public': False,
        }

        if post_data.get('request_id'):
            try:
                attachment_data['res_id'] = int(post_data.get('request_id'))
            except (ValueError, TypeError):
                _logger.debug(
                    "Cannon convert request_id %r",
                    post_data.get('request_id'),
                    exc_info=True)
            else:
                attachment_data['res_model'] = 'request.request'

        # Check max filesize and return error if file is too big
        upload.seek(0, os.SEEK_END)
        file_size = upload.tell()
        max_size = self._get_max_upload_size()
        if max_size and file_size > max_size:
            _logger.warning(
                "File size is too big: %s > %s", file_size, max_size)
            return json.dumps({
                'status': 'FAIL',
                'success': False,
                'message': _(
                    "File size is too big!"),
            })
        upload.seek(0, os.SEEK_SET)

        try:
            data = upload.read()

            self._check_file_has_allowed_type(data)

            data_base64 = base64.b64encode(data)

            if is_image:
                data_base64 = tools.image_process(
                    data_base64, verify_resolution=True)

            attachment = request.env['ir.attachment'].sudo().create(dict(
                attachment_data,
                datas=data_base64,
            ))
        except Exception as e:
            _logger.exception("Failed to upload file to attachment")
            message = ustr(e)
            return json.dumps({
                'status': 'FAIL',
                'success': False,
                'message': message,
            })

        attachment.generate_access_token()
        if is_image:
            attachment_url = "%s?access_token=%s" % (
                url_quote("/web/image/%d/%s" % (
                    attachment.id,
                    attachment.name)),
                attachment.sudo().access_token,
            )
        else:
            attachment_url = "%s?access_token=%s&download" % (
                url_quote("/web/content/%d/%s" % (
                    attachment.id,
                    attachment.name)),
                attachment.sudo().access_token,
            )

        return json.dumps({
            'status': 'OK',
            'success': True,
            'attachment_url': attachment_url,
        })

    @http.route('/crnd_wsd/api/request/update-text', type='json',
                auth='user', methods=['POST'], website=True)
    def wsd_request_update_text(self, request_id, request_text):
        try:
            reqs = self._id_to_record('request.request', request_id)
            reqs.ensure_one()
        except Exception as exc:
            return {
                'error': _("Access denied"),
                'debug': ustr(exc),
            }

        if not reqs.can_change_request_text:
            return {
                'error': _("Access denied"),
            }

        try:
            reqs.request_text = request_text
        except Exception as exc:
            return {
                'error': _("Access denied"),
                'debug': ustr(exc),
            }

        return {
            'request_text': reqs.request_text,
        }

    @http.route('/crnd_wsd/api/request/do-action', type='json',
                auth='user', methods=['POST'], website=True)
    def wsd_request_actions(self, request_id, action_id, response_text=None):
        try:
            reqs = self._id_to_record('request.request', request_id)
            reqs.ensure_one()

            action_route = request.env['request.stage.route'].search([
                ('website_published', '=', True),
                ('stage_from_id', '=', reqs.sudo().stage_id.id),
                ('request_type_id', '=', reqs.sudo().type_id.id),
                ('id', '=', int(action_id)),
            ])
            action_route.ensure_one()
            action_route.check_access_rights('read')
            action_route.check_access_rule('read')
        except Exception as exc:
            return {
                'error': _("Access denied"),
                'debug': ustr(exc),
            }

        try:
            if (action_route.close and
                    action_route.require_response and response_text):
                reqs.response_text = response_text
            reqs.stage_id = action_route.stage_to_id
        except Exception as exc:
            return {
                'error': _("Access denied"),
                'debug': ustr(exc),
            }

        return {
            'status': 'ok',
            'extra_action': action_route.website_extra_action,
        }
