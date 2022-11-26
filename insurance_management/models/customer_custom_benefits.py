# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging



class customer_custom_benefit(models.Model):
    _name = 'customer.custom.benefit'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'customer_custom_benefit'

    name = fields.Char()
    benefit_name = fields.Char(store=True)
    insurance_company_id = fields.Many2one(related='insurance_quotation_id.insurance_company_id',string='Insurance Company')
    category_type = fields.Selection([('vip','VIP'),('a+','A+'),('a','A'),('b','B'),('c','C')],string='Category Type')
    benefit_id = fields.Many2one('benefit.name',string='Benefit')
    benefit_value = fields.Char(string='Value')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)
    client_branch_id = fields.Many2one('client.branch',string='Client Branch')
    insurance_quotation_id = fields.Many2one('insurance.quotation',string='Insurance Quotation')

    # excluded_included = fields.Selection([('excluded','Excluded'),('included','Included')],string='Excluded/Included')
    # fixed_vary = fields.Selection([('fixed','Fixed'),('vary','Vary')],string='Fixed/Vary')

    included = fields.Boolean(string='Included?')
    vary = fields.Boolean(string='Is Vary?')
    from_value = fields.Float(string='From Value')
    to_value = fields.Float(string='To Value')

    @api.onchange('benefit_id')
    def custom_benefit_name(self):
        self.benefit_name = self.benefit_id.name
