from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date


class EmpData(models.Model):
    _inherit = 'insurance.employee.data'

    member_type = fields.Many2one('member.type.standard', string='Member Type')
    class_no = fields.Many2one('class.name.standard', string='Class No')
    age_category = fields.Many2one('age.category.standard', string='Age Category')
    occupation = fields.Many2one('ins.occupation', string='Occupation')
    branch_id = fields.Many2one('client.branch', string='Branch ID')