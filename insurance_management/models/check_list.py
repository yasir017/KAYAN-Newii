# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging



class client_checklist(models.Model):
    _name = 'client.checklist'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'client_checklist'
    _rec_name = 'check_list'

    check_list = fields.Html(string='Check List')

