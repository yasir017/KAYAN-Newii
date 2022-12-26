from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    policy_id = fields.Many2one('insurance.policy',"Internal Ref",)

    endorsment_id = fields.Many2one('insurance.policy',"Endoresment",)
    invoice_type = fields.Selection([('regular_inv','Regular Invoice'),('policy','Inception'),('endors','Endorsement'),('commission_inv','Commission Invoice'),('claim_inv','Claim Invoice'),('sale_commission','Salesperson Comission')],default='policy',string="Transaction Type")

    sales_person = fields.Many2one('hr.employee',string="Sales Person")
    policy_no = fields.Char("Policy No")
    insurance_co_ref = fields.Char('Insurance Co.reference',required=1)
    saleperson_id = fields.Many2one('sale.person.commission')
    @api.onchange('invoice_type')
    def onchange_inv_type(self):
        self.policy_no=''
        self.policy_id=False


    @api.onchange('policy_id')
    def onchange_policy(self):
        self.policy_no = self.policy_id.policy_no
    @api.onchange('endorsment_id')
    def _onchange_endors(self):
        self.policy_no = self.endorsment_id.policy_no
