from odoo import models, fields, api
from odoo.osv import expression

from odoo.addons.crnd_web_m2o_info_widget import helper_get_many2one_info_data


class ResPartner(models.Model):
    _inherit = 'res.partner'

    request_by_partner_ids = fields.One2many(
        'request.request', 'partner_id',
        readonly=True, copy=False)
    request_by_author_ids = fields.One2many(
        'request.request', 'author_id',
        readonly=True, copy=False)
    request_ids = fields.Many2many(
        'request.request',
        'request_request_partner_author_rel',
        'partner_id', 'request_id',
        readonly=True, copy=False, store=True,
        compute='_compute_request_data')
    request_count = fields.Integer(
        'Requests', compute='_compute_request_data',
        store=True, readonly=True)

    @api.depends('request_by_partner_ids', 'request_by_author_ids')
    def _compute_request_data(self):
        for record in self:
            record.request_ids = (
                record.request_by_partner_ids + record.request_by_author_ids)
            record.request_count = len(record.request_ids)

    def action_show_related_requests(self):
        self.ensure_one()
        return self.env['generic.mixin.get.action'].get_action_by_xmlid(
            'generic_request.action_request_window',
            domain=expression.OR([
                [('partner_id', 'in', self.ids)],
                [('author_id', 'in', self.ids)],
            ]),
            context=dict(
                self.env.context,
                default_partner_id=self.commercial_partner_id.id,
                default_author_id=self.id,
            ))

    def _request_helper_m2o_info_get_fields(self):
        """ Find list of fields, that have to be displayed as partner info
            on request form view in 'm2o_info' fields.

            Could be overridden by third-party modules.
        """
        return [
            'name', 'commercial_company_name', 'website',
            'email', 'phone', 'mobile'
        ]

    def request_helper_m2o_info(self):
        """ Technical method, that is used to perepear data for
            m2o_info fields.
        """
        return helper_get_many2one_info_data(
            self,
            self._request_helper_m2o_info_get_fields())
