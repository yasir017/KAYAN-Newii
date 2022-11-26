from odoo import api, fields, models, _

class Branch(models.Model):
    _name = 'insurance.branch'

    name = fields.Char("Name")
