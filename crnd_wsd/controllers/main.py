import pdb
import base64
from urllib.parse import urlsplit, urlunsplit
import logging
import functools
import werkzeug

from odoo import _
from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo.exceptions import (
    UserError, AccessError, ValidationError
)

from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.portal.controllers.portal import CustomerPortal
from .controller_mixin import WSDControllerMixin

_logger = logging.getLogger(__name__)

GROUP_USER_ADVANCED = (
    'crnd_wsd.group_service_desk_website_user_advanced'
)

ITEMS_PER_PAGE = 20


# NOTE: here is name collision with request, so be careful, when use name
# `request`. To avoid this name collision use names `req` and `reqs` for
# `request.request` records

def can_read_request(record):
    """
    This function check has user access to record.
    :param record: record
    :return: True or False
    """
    try:
        record = record.with_user(http.request.env.user)
        record.check_access_rights('read')
        record.check_access_rule('read')
    except AccessError:
        return False
    return True


def get_redirect():
    """
    This function returns quoted redirect parameter based on current page.
    It is used to redirect user on Login or Signup pages.

    For example, current URL is
    'http://localhost:11069/requests/new/step/category?service_id=1'

    >>> get_redirect()
    ... redirect=%2Frequests%2Fnew%2Fstep%2Fcategory%3Fservice_id%3D1

    Result of this function could be used to redirect user to
    login page and redirect to same page after login. For example:

    >>> redirect_url = "/web/login?%s" % get_redirect()
    >>> redirect_url
    ... "/web/login?redirect=
    ... %2Frequests%2Fnew%2Fstep%2Fcategory%3Fservice_id%3D1

    Note, that 'redirect' param has quoted value that allows to keep
    query parametrs.
    """
    full_url = http.request.httprequest.url
    s = urlsplit(full_url)
    url = urlunsplit(['', '', s.path, s.query, s.fragment])
    return werkzeug.urls.url_encode({'redirect': url})


def guard_access(func):
    """
    This is a decorator function. It is used to redirect public users
    to Login page if the 'request_wsd_public_ui_visibility' field is set
    to 'redirect' in the settings. Once logged in, users will be redirected
    back to the targeted page.

    Use it to decorate functions with '@http.route' decorator, on the
    required routes. When a user trying to access specified route, he will
    be checked by @guard_access conditions first.

    How to use: place '@guard_access' after '@http.route' decorator, before
    decorated function. For example:
    >>>@http.route(["/requests/new"], type='http', auth="public",
    ...            methods=['GET'], website=True)
    ...@guard_access
    ...def request_new(self, **kwargs):
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not http.request.website.is_public_user():
            return func(*args, **kwargs)
        if (request.env.user.company_id.request_wsd_public_ui_visibility ==
                'redirect'):
            url = "/web/login?%s" % get_redirect()
            return http.request.redirect(url)
        return func(*args, **kwargs)
    return wrapper


class WebsiteRequest(WSDControllerMixin, http.Controller):
    def _requests_get_request_domain_base(self, search, kind_id=None, **post):
        domain = [
            '|',
            ('website_id', '=', False),
            ('website_id', '=', http.request.website.id),
        ]
        if search:
            domain += [
                '|', '|', '|', ('name', 'ilike', search),
                ('category_id.name', 'ilike', search),
                ('type_id.name', 'ilike', search),
                ('request_text', 'ilike', search)]

        kind = self._id_to_record('request.kind', kind_id, no_raise=True)
        if kind:
            domain = expression.AND([
                domain,
                [('kind_id', '=', kind.id)],
            ])

        return domain

    def _requests_get_request_domains(self, search, **post):
        domain = self._requests_get_request_domain_base(search, **post)

        return {
            'all': domain,
            'open': domain + [('closed', '=', False)],
            'closed': domain + [('closed', '=', True)],
            'my': domain + [
                ('closed', '=', False),
                '|', '|',
                ('user_id', '=', http.request.env.user.id),
                ('created_by_id', '=', http.request.env.user.id),
                ('author_id', '=', http.request.env.user.partner_id.id),
            ],
        }

    def _requests_list_get_extra_context(self, req_status, search, **post):
        selected_request_kind = self._id_to_record(
            'request.kind', post.get('kind_id'), no_raise=True)
        request_kinds = http.request.env['request.kind'].search([
            ('show_as_website_filter', '=', True),
            ('request_ids.id', '!=', False),
        ])

        return {
            'request_kinds': request_kinds,
            'selected_request_kind': selected_request_kind,
        }

    def _request_page_get_extra_context(self, req_id, **post):
        # We have to  pass additional params to template to be able to use
        # chatter for partners authenticated via access token
        res = {}
        if post.get('pid'):
            res['pid'] = post['pid']
        if post.get('hash'):
            res['hash'] = post['hash']
        if post.get('token'):
            res['token'] = post['token']
        elif post.get('access_token'):
            res['token'] = post['access_token']
        return res

    @http.route(['/requests',
                 '/requests/<string:req_status>',
                 '/requests/<string:req_status>/page/<int:page>'],
                type='http', auth="public", website=True)
    @guard_access
    def requests(self, req_status='my', page=0, search="", **post):
        if req_status not in ('my', 'open', 'closed', 'all'):
            return http.request.not_found()

        Request = http.request.env['request.request']

        url = '/requests/' + req_status
        keep = QueryURL(
            url, [], search=search, **post)
        domains = self._requests_get_request_domains(search, **post)

        req_count = {
            'all': Request.search_count(domains['all']),
            'open': Request.search_count(domains['open']),
            'closed': Request.search_count(domains['closed']),
            'my': Request.search_count(domains['my']),
        }

        # make pager
        pager = http.request.website.pager(
            url=url,
            total=req_count[req_status],
            page=page,
            step=ITEMS_PER_PAGE,
            url_args=dict(
                post, search=search),
        )

        # search the count to display, according to the pager data
        reqs = http.request.env['request.request'].search(
            domains[req_status], limit=ITEMS_PER_PAGE, offset=pager['offset'])
        values = {
            'search': search,
            'reqs': reqs.sudo(),
            'pager': pager,
            'default_url': url,
            'req_status': req_status,
            'req_count': req_count,
            'keep': keep,
            'get_redirect': get_redirect,
        }

        values.update(self._requests_list_get_extra_context(
            req_status=req_status, search=search, **post
        ))
        return http.request.render(
            'crnd_wsd.wsd_requests', values)

    def _request_get_available_routes(self, req, **post):
        Route = http.request.env['request.stage.route']
        result = Route.browse()

        if http.request.website.is_public_user():
            return result

        user = http.request.env.user
        group_ids = user.sudo().groups_id.ids
        action_routes = Route.search(expression.AND([
            [('request_type_id', '=', req.sudo().type_id.id)],
            [('stage_from_id', '=', req.sudo().stage_id.id)],
            [('website_published', '=', True)],
            expression.OR([
                [('allowed_user_ids', '=', False)],
                [('allowed_user_ids', '=', user.id)],
            ]),
            expression.OR([
                [('allowed_group_ids', '=', False)],
                [('allowed_group_ids', 'in', group_ids)],
            ]),
        ]))

        for route in action_routes:
            try:
                route._ensure_can_move(req)
            except AccessError:  # pylint: disable=except-pass
                pass
            except ValidationError:  # pylint: disable=except-pass
                pass
            else:
                result += route
        return result

    @http.route(["/requests/request/<int:req_id>"],
                type='http', auth="public", website=True)
    def request(self, req_id, **kw):
        req = self._id_to_record(
            'request.request', req_id,
            access_token=kw.get('access_token'))
        if req.website_id and req.website_id != http.request.website:
            raise http.request.not_found()

        action_routes = self._request_get_available_routes(req, **kw)

        disable_new_comments = (
            req.closed and req.sudo().type_id.website_comments_closed
        )

        values = {
            'req': req.sudo(),
            'action_routes': action_routes.sudo(),
            'can_change_request_text': (
                False if http.request.website.is_public_user()
                else req.can_change_request_text),
            'disable_composer': disable_new_comments,
            'can_read_request': can_read_request,
            'show_congrats_msg': kw.get('show_congrats_msg', False),
        }
        values.update(self._request_page_get_extra_context(req_id, **kw))

        return http.request.render(
            "crnd_wsd.wsd_request", values)

    @http.route(["/requests/new"], type='http', auth="public",
                methods=['GET'], website=True)
    @guard_access
    def request_new(self, **kwargs):
        # May be overridden to change start step
        return http.request.redirect(QueryURL(
            '/requests/new/step/category', [])(**kwargs))

    def _request_new_get_public_categs_domain(self, category_id=None, **post):
        if http.request.env.user.has_group(GROUP_USER_ADVANCED):
            return []
        return [
            '&', ('website_published', '=', True),
            '|', ('website_ids', '=', False),
            ('website_ids', 'in', http.request.website.id)]

    def _request_new_get_public_categs(self, category_id=None, **post):
        domain = self._request_new_get_public_categs_domain(
            category_id=category_id, **post)
        categs = http.request.env['request.category'].search(domain)
        result = categs.filtered(
            lambda r: self._request_new_get_public_types(
                category_id=r.id, **post))
        return result

    @http.route(["/requests/new/step/category"], type='http', auth="public",
                methods=['GET', 'POST'], website=True)
    @guard_access
    def request_new_select_category(self, category_id=None, **kwargs):
        keep = QueryURL('', [], category_id=category_id, **kwargs)
        req_category = self._id_to_record('request.category', category_id)
        if http.request.httprequest.method == 'POST' and req_category:
            return http.request.redirect(keep(
                '/requests/new/step/type',
                category_id=req_category.id, **kwargs))

        public_categories = self._request_new_get_public_categs(
            category_id=category_id, **kwargs).filtered(
                lambda r: self._request_new_get_public_types(
                    category_id=r.id, **kwargs))

        if len(public_categories) <= 1 and not http.request.session.debug:
            return http.request.redirect(keep(
                '/requests/new/step/type',
                category_id=public_categories.id, **kwargs))

        values = {
            'req_categories': public_categories,
            'req_category_sel': req_category,
            'keep': keep,
            'get_redirect': get_redirect,
        }

        return http.request.render(
            "crnd_wsd.wsd_requests_new_select_category", values)

    def _request_new_get_public_types_domain(self, type_id=None,
                                             category_id=None, **kwargs):
        domain = []
        if not http.request.env.user.has_group(GROUP_USER_ADVANCED):
            domain += [('website_published', '=', True)]

        if category_id:
            domain += [('category_ids.id', '=', category_id)]
        else:
            domain += [('category_ids', '=', False)]

        domain += [
            '|', ('website_ids', '=', False),
            ('website_ids', 'in', http.request.website.id)]
        return domain

    def _request_new_get_public_types(self, type_id=None, category_id=None,
                                      **kwargs):
        domain = self._request_new_get_public_types_domain(
            type_id=type_id, category_id=category_id, **kwargs)

        return http.request.env['request.type'].search(domain)

    @http.route(["/requests/new/step/type"], type='http', auth="public",
                methods=['GET', 'POST'], website=True)
    @guard_access
    def request_new_select_type(self, type_id=None, category_id=None,
                                **kwargs):
        keep = QueryURL('', [], type_id=type_id, category_id=category_id,
                        **kwargs)
        req_type = self._id_to_record('request.type', type_id)
        req_category = self._id_to_record('request.category', category_id)
        if http.request.httprequest.method == 'POST' and req_type:
            return http.request.redirect(keep(
                '/requests/new/step/data', type_id=req_type.id,
                category_id=req_category.id, **kwargs))

        public_types = self._request_new_get_public_types(
            type_id=type_id, category_id=req_category.id, **kwargs)

        if len(public_types) == 1 and not http.request.session.debug:
            return http.request.redirect(keep(
                '/requests/new/step/data', type_id=public_types.id,
                category_id=req_category.id, **kwargs))

        values = {
            'req_types': public_types,
            'req_type_sel': req_type,
            'req_category': req_category,
            'keep': keep,
            'get_redirect': get_redirect,
        }

        return http.request.render(
            "crnd_wsd.wsd_requests_new_select_type", values)

    def _request_new_process_data(self, req_type, req_category=False,
                                  req_text=None, **post):
        return {
            'req_type': req_type,
            'req_category': req_category,
            'req_text': req_text,
        }

    def _request_new_validate_data(self, req_type, req_category,
                                   req_text, data, **post):
        errors = {}
        if not req_text or req_text == '<p><br></p>':
            errors.update({
                'request_text': {
                    'error_text': _(
                        "Request text is empty!")}})

        max_text_size = request.env.user.company_id.request_limit_max_text_size
        if max_text_size and len(req_text) > max_text_size:
            errors.update({
                'request_text': {
                    'error_text': _(
                        "Request text is too long!")}})
        if http.request.website.is_request_create_public():
            if not data.get('author_id') and not data.get('email_from'):
                errors['request_author_email'] = {
                    'error_text': _(
                        "Please, specify your email address!"),
                }

        if http.request.website.is_request_author_phone_required():
            if not data.get('author_phone'):
                errors.update({
                    'request_author_phone': {
                        'error_text': _(
                            "Please, specify your phone number!")}})
        return errors

    def _request_new_prepare_data(self, req_type, req_category,
                                  req_text, **post):
        channel_website = http.request.env.ref(
            'generic_request.request_channel_website')
        res = {
            'category_id': req_category and req_category.id,
            'type_id': req_type.id,
            'request_text': req_text,
            'channel_id': channel_website.id,
            'website_id': http.request.website.id,
        }
        company = http.request.env.user.company_id
        if http.request.website.is_request_create_public():
            res['created_by_id'] = http.request.env.ref('base.user_root').id
            is_create = company.request_mail_create_author_contact_from_email
            author_id = http.request.env[
                'request.request'
            ].sudo()._get_or_create_partner_from_email(
                post.get('request_author_email'),
                force_create=is_create,
            )
            if author_id:
                res['author_id'] = author_id
            else:
                res['author_id'] = False
                author_name, author_email = http.request.env[
                    'res.partner'
                ]._parse_partner_name(post.get('request_author_email'))
                res['email_from'] = author_email
                res['author_name'] = author_name

            # TODO: Maybe need add validation for phone number?
            author_phone = post.get('request_author_phone')
            if author_phone:
                res['author_phone'] = author_phone
        return res

    @http.route(["/requests/new/step/data"],
                type='http', auth="public",
                methods=['GET', 'POST'], website=True)
    @guard_access
    def request_new_fill_data(self, type_id=None, category_id=None,
                              req_text=None, **kwargs):
        # hr_costs_file = base64.b64encode(hr_costs_file.read())

        # my_file = base64.encodebytes(kwargs.get('Raheel'))
        if 'claim_form' in kwargs:
            claim_form = kwargs.get('claim_form')
            claim_form_file = base64.b64encode(claim_form.read())
        if 'trafic_najm_report' in kwargs:
            trafic_najm_report = kwargs.get('trafic_najm_report')
            trafic_najm_report_file = base64.b64encode(trafic_najm_report.read())
        if 'civil_defence_report' in kwargs:
            civil_defence_report = kwargs.get('civil_defence_report')
            civil_defence_report_file = base64.b64encode(civil_defence_report.read())
        if 'driver_licence_copy' in kwargs:
            driver_licence_copy = kwargs.get('driver_licence_copy')
            driver_licence_copy_file = base64.b64encode(driver_licence_copy.read())
        if 'vehicle_registration_copy' in kwargs:
            vehicle_registration_copy = kwargs.get('vehicle_registration_copy')
            vehicle_registration_copy_file = base64.b64encode(vehicle_registration_copy.read())
        if 'id_copy' in kwargs:
            id_copy = kwargs.get('id_copy')
            id_copy_file = base64.b64encode(id_copy.read())
        if 'sketch_accident' in kwargs:
            sketch_accident = kwargs.get('sketch_accident')
            sketch_accident_file = base64.b64encode(sketch_accident.read())
        if 'permission_to_repair' in kwargs:
            permission_to_repair = kwargs.get('permission_to_repair')
            permission_to_repair_file = base64.b64encode(permission_to_repair.read())
        if 'basher_report' in kwargs:
            basher_report = kwargs.get('basher_report')
            basher_report_file = base64.b64encode(basher_report.read())



        # pylint: disable=too-many-locals
        req_type = self._id_to_record('request.type', type_id)

        if not req_type:
            return http.request.redirect(QueryURL(
                '/requests/new/step/type', [])(
                    type_id=type_id, category_id=category_id, **kwargs))

        req_category = self._id_to_record('request.category', category_id)

        values = self._request_new_process_data(
            req_type, req_category, req_text=req_text, **kwargs)
        values['get_redirect'] = get_redirect
        values['validation_errors'] = {}

        if http.request.httprequest.method == 'POST':
            req_data = self._request_new_prepare_data(
                req_type, req_category, req_text, **kwargs)

            validation_errors = self._request_new_validate_data(
                req_type, req_category, req_text, req_data, **kwargs)

            if not validation_errors:
                Request = http.request.env['request.request']
                if http.request.website.is_request_create_public():
                    # If it is allowed to create request for public users and
                    # current user is public user, then we have to use sudo
                    # to handle access rights issues
                    Request = Request.with_user(SUPERUSER_ID)
                try:
                    # Try to create request with savepoint, to avoid
                    # duplication of requests, when there were error triggered
                    # by automated action after request created
                    with http.request.env.cr.savepoint():
                        req_data.update({
                            'claim_form': claim_form_file,
                            'trafic_najm_report': trafic_najm_report_file,
                            'civil_defence_report': civil_defence_report_file,
                            'driver_licence_copy': driver_licence_copy_file,
                            'vehicle_registration_copy': vehicle_registration_copy_file,
                            'id_copy': id_copy_file,
                            'sketch_accident': sketch_accident_file,
                            'permission_to_repair': permission_to_repair_file,
                            'basher_report': basher_report_file,
                        })

                        req = Request.create(req_data)
                        req._request_bind_attachments()
                except (UserError, AccessError, ValidationError) as exc:
                    error_msg = "\n".join(
                        str(a) for a in exc.args if a
                    )
                    validation_errors.update({'error': {
                        'error_text': error_msg}})
                except Exception:
                    _logger.error(
                        "Error caught during request creation", exc_info=True)
                    validation_errors.update({'error': {
                        'error_text':
                            _("Unknown server error. See server logs.")}})
                else:
                    # Decide where to redirect user after request was created
                    redirect_after_request_created = (
                        http.request.website
                        .request_redirect_after_created_on_website
                    )
                    redirect_params = {}
                    if redirect_after_request_created == 'req_page':
                        redirect_url = "/requests/request/%s" % req.id
                        redirect_params['show_congrats_msg'] = True
                    else:
                        redirect_url = "/requests/congrats/%s" % req.id

                    if http.request.website.is_request_create_public():
                        redirect_params.update({
                            'access_token': req._portal_ensure_token(),
                        })

                    if redirect_params:
                        redirect_url += "?" + werkzeug.urls.url_encode(
                            redirect_params)
                    return http.request.redirect(redirect_url)

            values['validation_errors'] = validation_errors
            values.update(req_data)
        return http.request.render(
            "crnd_wsd.wsd_requests_new_request_data", values)

    @http.route(["/requests/congrats/<int:req_id>"],
                type='http', auth="public", website=True)
    def request_congrat(self, req_id, access_token=None, **kw):
        keep = QueryURL('', [], access_token=access_token, **kw)
        req = self._id_to_record(
            'request.request', req_id,
            access_token=access_token)
        if req.website_id and req.website_id != http.request.website:
            raise http.request.not_found()

        return http.request.render(
            "crnd_wsd.wsd_requests_new_congratulation",
            {
                'req': req,
                'keep': keep,
            }
        )


class RequestCustomerPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(
            RequestCustomerPortal, self)._prepare_portal_layout_values()
        user = http.request.env.user
        values['request_count'] = request.env['request.request'].search_count(
            ['|', '|', ('created_by_id', '=', user.id),
             ('user_id', '=', user.id),
             ('partner_id', 'child_of',
              user.partner_id.commercial_partner_id.id)])
        return values
