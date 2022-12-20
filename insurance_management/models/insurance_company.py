# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging



class insurance_company(models.Model):
    _name = 'insurance.company'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'Insurance company'
    _rec_name = 'ins_company_partner_id'

    ins_company_partner_id = fields.Many2one('res.partner', string='Insurance Company Partner',required=True)
    name = fields.Char(string='Name')
    country = fields.Many2one(related='ins_company_partner_id.country_id',string='Country')
    city = fields.Many2one(related='ins_company_partner_id.state_id',string='City')
    website = fields.Char(related='ins_company_partner_id.website',string='Website')
    mobile = fields.Char(related='ins_company_partner_id.mobile',string='Mobile')
    email = fields.Char(related='ins_company_partner_id.email',string='Email')
    arabic_name = fields.Char(string='Arabic Name')
    branch_name = fields.Char(string='Company(Branch)')
    location = fields.Char(string='Location')
    company_benefit_ids = fields.One2many('insurance.company.benefit','insurance_company_id',string='Benefits')
    trade_name = fields.Char('Trade Name')
    contact_dear = fields.Char("Contract Dear")
    contact_person = fields.Char('Contract Person')
    phone = fields.Char('Phone No')
    ext = fields.Char("Extension")
    fax_no = fields.Char("Fax No")
    # mobile_no = fields.Char('Mobile No')
    # email_adress = fields.Char("Email No")
    # website = fields.Char("website")
    # city = fields.Char("City")
    region = fields.Many2one('insurance.region', "Region")
    affliated_co = fields.Char("Affiliated Co.")
    public = fields.Boolean("Public")
    bank_id = fields.Many2one('res.bank', "Bank")
    income_account_id = fields.Many2one('account.account', 'Comm Income Acc')
    recivable_acc = fields.Many2one('account.account', 'Comm Recievable Acc')
    other_income_account_id = fields.Many2one('account.account', 'Other Fees Income Acc')
    pre_paid_tax_acc = fields.Many2one('account.account', 'Pre Paid Tax Acc')
    billing_address = fields.Text("Billing address")

    department_ids = fields.Many2many('insurance.department', string='Insurance Department')
    policy_id = fields.Many2one('insurance.policy', string="Policy ID")
    client_group = fields.Char("Customer")
    branch_id = fields.Many2one('insurance.branch', "Branch Group")
    name_contract = fields.Char('Contract ID')
    starting_date = fields.Date('Starting Date')
    expiry_date = fields.Date('Expiry Date')
    issuance_date = fields.Date('Issuance Date')
    file_path = fields.Binary('File Path')
    # basic_line_ids = fields.One2many('basic.com.lines', 'client_id', string="Basic And Complementray")
    company_class_standard_ids = fields.One2many('company.class.standard','insurance_company_id',string='Company Class Type Standards',ondelete='cascade')
    company_member_standard_ids = fields.One2many('company.member.type.standard','insurance_company_id',string='Company Member Type Standards',ondelete='cascade')
    company_age_catogory_standard_ids = fields.One2many('company.age.category.standard','insurance_company_id',string='Company Age Category Standards',ondelete='cascade')
    auto_map_benefits_to_quotation = fields.Boolean(string='Auto Map Benefits to Quotation')

    @api.model
    def create(self, vals):
        res = super(insurance_company, self).create(vals)
        for rec in res:
            rec.ins_company_partner_id.is_insurance_company = True
            rec.ins_company_partner_id.supplier_rank = 1
            rec.name = rec.ins_company_partner_id.name
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_insurance_company = fields.Boolean(string='Is Insurance Company?')


class InsuranceContract(models.Model):
    _inherit = 'insurance.contract'

    insurance_company_id = fields.Many2one('insurance.company', "Insurance Company")

class company_class_standard(models.Model):
    _name = 'company.class.standard'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'company_class_standard'

    name = fields.Char(string='Name',required=True)
    # standard_type = fields.Selection([('sme', 'SME'), ('corporate', 'Corporate')
    #                                   ], string='Standard For', required=True)
    class_standard_id = fields.Many2one('class.name.standard',string='Broker Standard',required=True)
    insurance_company_id = fields.Many2one('insurance.company',string='Insurance Company')


class company_member_type_standard(models.Model):
    _name = 'company.member.type.standard'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'company_member_type_standard'

    name = fields.Char(string='Name',required=True)
    # standard_type = fields.Selection([('sme', 'SME'), ('corporate', 'Corporate')
    #                                   ], string='Standard For', required=True)
    member_type_standard_id = fields.Many2one('member.type.standard',string='Member Type Standard',required=True)
    insurance_company_id = fields.Many2one('insurance.company',string='Insurance Company')

class company_age_category_standard(models.Model):
    _name = 'company.age.category.standard'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'company_age_category_standard'

    name = fields.Char(string='Name',required=True)
    # standard_type = fields.Selection([('sme', 'SME'), ('corporate', 'Corporate')
    #                                   ], string='Standard For', required=True)
    age_category_standard_id = fields.Many2one('age.category.standard',string='Member Type Standard',required=True)
    insurance_company_id = fields.Many2one('insurance.company',string='Insurance Company')