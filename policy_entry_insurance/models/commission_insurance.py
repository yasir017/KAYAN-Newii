from odoo import api, fields, models, _


class ComissionInsurance(models.Model):
    _name = 'insurance.commission'


    policy_id = fields.Many2one('insurance.policy',string="Policy ID")
    client_group = fields.Char("Customer")
    branch_id = fields.Many2one('insurance.branch',"Branch Group")
    start_date = fields.Date("Start Date")
    expiry_date = fields.Date("Expiry Date")
    issuence_date = fields.Date("Issuance Date")


