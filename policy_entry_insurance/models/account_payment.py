
from odoo import api, fields, models, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    tax_payment = fields.Boolean("Tax Payment")