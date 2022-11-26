# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging



class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    is_medical = fields.Boolean(string='Is Medical?')
    is_vehicle = fields.Boolean(string='Is Vehicle?')
    insurance_company_id = fields.Many2one('insurance.company', string='Insurance Company')
