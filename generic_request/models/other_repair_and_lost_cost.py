import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.addons.generic_mixin.tools.x2m_agg_utils import read_counts_for_o2m

_logger = logging.getLogger(__name__)


class other_repair_cost(models.Model):
    _name = "other.repair.cost"
    _description = "other_repair_cost"


    name = fields.Char(string='Name',required=True)
    cost = fields.Float(string='Cost')
    request_id = fields.Many2one('request.request',string='Claim Request')

class lost_other_cost(models.Model):
    _name = "lost.other.cost"
    _description = "lost_other_cost"


    name = fields.Char(string='Name',required=True)
    cost = fields.Float(string='Cost')
    request_id = fields.Many2one('request.request',string='Claim Request')
