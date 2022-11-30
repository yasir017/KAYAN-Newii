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
    is_client_quoit_temp = fields.Boolean(string='Is C Quoit temp?')
    is_vehicle_quoit_temp = fields.Boolean(string='Is Vehicle Quoit temp?')
    is_medical_info_temp = fields.Boolean(string='Is Medical Info temp?')
    is_vehicle_info_temp = fields.Boolean(string='Is Vehicle Info temp?')
    insurance_company_id = fields.Many2one('insurance.company', string='Insurance Company')
