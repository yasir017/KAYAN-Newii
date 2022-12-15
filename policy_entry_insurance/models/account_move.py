from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    policy_id = fields.Many2one('insurance.policy',"Policy",)

    endorsment_id = fields.Many2one('insurance.policy',"Endoresment",)
    invoice_type = fields.Selection([('regular_inv','Regular Invoice'),('policy','Inception'),('endors','Endorsement'),('commission_inv','Commission Invoice'),('claim_inv','Claim Invoice')],default='policy',string="Transaction Type")

    sales_person = fields.Many2one('hr.employee',string="Sales Person")
    policy_no = fields.Char("Internal Ref")
    insurance_co_ref = fields.Char('Insurance Co.reference')

    @api.onchange('invoice_type')
    def onchange_inv_type(self):
        self.policy_no=''
        self.policy_id=False

