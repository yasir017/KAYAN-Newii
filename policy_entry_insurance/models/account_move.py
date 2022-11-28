from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    policy_id = fields.Many2one('insurance.policy',"Policy",domain="[('policy_type','=',invoice_type)]")
    invoice_type = fields.Selection([('regular_inv','Regular Invoice'),('policy','Policy'),('endors','Endorsement'),('commission_inv','Commission Invoice'),('claim_inv','Claim Invoice')],default='policy',string="Type")

    sales_person = fields.Many2one('hr.employee',string="Sales Person")
    policy_no = fields.Char("Policy No")
    insurance_co_ref = fields.Char('Insurance Co.reference')

