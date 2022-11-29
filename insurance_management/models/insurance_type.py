# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging



class insurance_type(models.Model):
    _name = 'insurance.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'insurance_type'

    name = fields.Char(string='Type Name')
    insurance_subtype_ids = fields.One2many('insurance.sub.type','insurance_type_id',string='Insurance Sub-Types')
    ins_type_select = fields.Selection([('is_medical','Medical'),('is_vehicle','Vehicle'),('is_marine','Marine'), ('other', 'Other')],string='Technical Type',required=True)
    # is_medical = fields.Boolean(string='Is Medical?')
    # is_vehicle = fields.Boolean(string='Is Vehicle?')
    list_required_docs_ids = fields.One2many('list.required.docs', 'insurance_type_id', string='Required Document List')

class insurance_sub_type(models.Model):
    _name = 'insurance.sub.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'insurance_sub_type'

    name = fields.Char(string='Name')
    code = fields.Integer(string='Code')
    sequence = fields.Integer(string='Sequence')
    insurance_type_id = fields.Many2one('insurance.type',string='Insurance Type Main')


class list_required_docs(models.Model):
    _name = 'list.required.docs'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'list.required.docs'

    name = fields.Char(string='Name')
    is_required = fields.Boolean(string='Is Required?')
    sequence = fields.Integer(string='Sequence')
    insurance_type_id = fields.Many2one('insurance.type',string='Insurance Type Main')
