# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging



class incident_type(models.Model):
    _name = 'incident.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'incident_type'

    name = fields.Char(string='Name')

