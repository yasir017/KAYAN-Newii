# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging

class company_standard_type(models.Model):
    _name = 'company.standard.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'company_standard_type'

    name = fields.Char(string='Name')

class class_name_standard(models.Model):
    _name = 'class.name.standard'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'class_name_standard'

    name = fields.Char(string='Name',required=True)
    # standard_type = fields.Many2many('company.standard.type',string='Standard For',required=True)


class member_type_standard(models.Model):
    _name = 'member.type.standard'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'member_type_standard'

    name = fields.Char(string='Name',required=True)
    # standard_type = fields.Many2many('company.standard.type',string='Standard For',required=True)


class age_category_standard(models.Model):
    _name = 'age.category.standard'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'age_category_standard'

    name = fields.Char(string='Name',required=True)
    # standard_type = fields.Many2many('company.standard.type',string='Standard For',required=True)