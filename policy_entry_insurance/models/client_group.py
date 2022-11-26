from odoo import api, fields, models, _

class ClientGroup(models.Model):
    _name = 'client.group'
    _inherit = ['mail.thread', 'mail.activity.mixin']



    name = fields.Char('Customer')


    english_name = fields.Char('English Name')
    arabic_name = fields.Char('Arabic Name')
    department_ids = fields.Many2many('insurance.department',string='Insurance Department')
    insurance_id = fields.Char('Insurance ID')
    insurance_english_name = fields.Char("English Name")
    insurance_arabic_name = fields.Char("Insurance Arabic Name")
    trade_name = fields.Char('Trade Name')
    contact_dear = fields.Char("Contract Dear")
    contact_person = fields.Char('Contract Person')
    phone = fields.Char('Phone No')
    ext = fields.Char("Extension")
    fax_no = fields.Char("Fax No")
    mobile_no = fields.Char('Mobile No')
    email_adress = fields.Char("Email No")
    website=  fields.Char("website")
    city = fields.Char("City")
    region = fields.Many2one('insurance.region',"Region")
    affliated_co = fields.Char("Affiliated Co.")
    public = fields.Boolean("Public")
    bank_id = fields.Many2one('res.bank',"Bank")
    income_account_id = fields.Many2one('account.account','Comm Income Acc')
    recivable_acc = fields.Many2one('account.account','Comm Recievable Acc')
    other_income_account_id = fields.Many2one('account.account','Other Fees Income Acc')
    pre_paid_tax_acc = fields.Many2one('account.account','Pre Paid Tax Acc')
    billing_address = fields.Text("Billing address")



class Region(models.Model):
    _name = 'insurance.region'

    name = fields.Char("Name")