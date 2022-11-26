from odoo import api, fields, models, _

class ProductProduct(models.Model):
    _inherit = 'product.product'

    insurance_product = fields.Boolean('Insurance Product')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    insurance_product = fields.Boolean('Policy Product')