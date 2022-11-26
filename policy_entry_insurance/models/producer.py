from odoo import api, fields, models, _


class ProducerComission(models.Model):
    _name = 'insurance.producer'

    policy_id = fields.Many2one('insurance.policy', 'REL')
    employee_id = fields.Many2one('hr.employee','Employee')
    amount = fields.Float("Amount")
    percentage = fields.Float('Percentage')

