
from odoo import models, fields, exceptions, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    govt_partner = fields.Many2one('res.partner',domain=[('supplier_rank','>',0)],string="Govt Partner",config_parameter="insurance_management.govt_partner")
    percentage = fields.Integer(string="Govt. Percentage",config_parameter="insurance_management.percentage")
    govt_bill_journal = fields.Many2one('account.journal',string="Journal",config_parameter="insurance_management.govt_bill_journal")

    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()
    #     params = self.env['ir.config_parameter'].sudo()
    #     res.update(
    #         percentage=params.get_param('percentage', default=False),
    #     )
    #     res.update(
    #         govt_partner=params.get_param('govt_partner', default=False),
    #     )
    #     res.update(
    #         govt_bill_journal=params.get_param('govt_bill_journal.id', default=False),
    #     )
    #     return res
    #
    #
    # def set_values(self):
    #     params = self.env['ir.config_parameter'].sudo()
    #     params.set_param('percentage', self.percentage)
    #     params.set_param('govt_partner', self.govt_partner)
    #     params.set_param('govt_bill_journal', self.govt_bill_journal)
    #     super(ResConfigSettings, self).set_values()