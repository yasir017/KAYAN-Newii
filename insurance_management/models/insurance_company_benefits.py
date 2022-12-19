# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging



class insurance_company_benefit(models.Model):
    _name = 'insurance.company.benefit'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'insurance_company_benefit'
    _rec_name = 'benefit_id'

    name = fields.Char()
    insurance_company_id = fields.Many2one('insurance.company',string='Insurance Company',readonly=False)
    category_type = fields.Selection([('vip','VIP'),('a+','A+'),('a','A'),('b','B'),('c','C')],string='Category Type')
    ins_type_select = fields.Selection([('is_medical', 'Medical'), ('is_vehicle', 'Vehicle'), ('is_marine', 'Marine'), ('other', 'Other')],
                                       string='Technical Type',required=True)
    benefit_id = fields.Many2one('benefit.name',string='Benefit',domain="[('ins_type_select','=',ins_type_select)]")
    benefit_value = fields.Char(string='Value')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)
    # client_branch_id = fields.Many2one('client.branch',string='Client Branch')


class benefit_name(models.Model):
    _name = 'benefit.name'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'benefit_name'

    name = fields.Char(string='Benefit Name', translate=True)
    ins_type_select = fields.Selection([('is_medical', 'Medical'), ('is_vehicle', 'Vehicle'), ('is_marine', 'Marine'), ('other', 'Other')],
                                       string='Technical Type',required=True)
