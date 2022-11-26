

from odoo import api, fields, models, _

class InsuranceContract(models.Model):
    _name = 'insurance.contract'
    _description = "Insurance contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char('Contract ID')

    starting_date = fields.Date('Starting Date')
    expiry_date = fields.Date('Expiry Date')
    issuance_date = fields.Date('Issuance Date')
    file_path = fields.Binary('File Path')
    basic_line_ids = fields.One2many('basic.com.lines','contract_id',string="Basic And Complementray")

class BasicAndCompulsary(models.Model):
    _name = 'basic.com.lines'

    contract_id = fields.Many2one('insurance.contract','REL')
    business_class_id = fields.Many2one('business.class.config','Business Class')
    department_id = fields.Many2one('insurance.department','Department')
    basic_comission = fields.Float('Basic Commission')

class InsuranceDepartment(models.Model):
    _name = 'insurance.department'

    code = fields.Char('Department ID')
    name = fields.Char('English Name')
    arabic_name = fields.Char('Arabic Name')


