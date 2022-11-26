import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m

_logger = logging.getLogger(__name__)


class request_other_attachments(models.Model):
    _name = "request.other.attachments"
    _description = "request_other_attachments"


    name = fields.Char(string='Name',required=True)
    file = fields.Binary(string='File')
    request_id = fields.Many2one('request.request',string='Claim Request')
