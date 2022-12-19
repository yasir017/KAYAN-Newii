# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging


class member_category(models.Model):
    _name = 'member.category'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'member_category'

    name = fields.Char(string='Member Category Name', translate=True)


class member_relation(models.Model):
    _name = 'member.relation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'member_relation'

    name = fields.Char(string='Member Relation Name', translate=True)
