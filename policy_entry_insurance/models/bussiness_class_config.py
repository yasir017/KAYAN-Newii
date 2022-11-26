
from odoo import api, fields, models, _

class BusinessClassConfig(models.Model):
    _name = 'business.class.config'

    name = fields.Char('Class English Name')
    arabic_name = fields.Char("Class Arabic Name")
    code = fields.Char("Code")
    class_id  = fields.Char("Class ID")
    account_no = fields.Char('Account NO')
    # class_id  = fields.Integer('Class ID')


class CategoryLines(models.Model):
    _name = 'insurance.category'

    name = fields.Char("Category English Name")
    code = fields.Char('Category ID')
    arabic_name = fields.Char('Category Arabic Name')

