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

class claim_required_docs(models.Model):
    _name = 'claim.required.docs'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'claim_required_docs'

    name = fields.Selection([('Claim Form', 'Claim Form'),
                             ('Trafic & Najm Report', 'Trafic & Najm Report'),
                             ('Civil Defence Report', 'Civil Defence Report'),
                             ('Driver Licence Copy', 'Driver Licence Copy'),
                             ('Vehicle Registration Copy', 'Vehicle Registration Copy'),
                             ('Sketch Accident', 'Sketch Accident'),
                             ('Permission to Repair', 'Permission to Repair'),
                             ('Basher Report', 'Basher Report'),
                             ('Copy of ID', 'Copy of ID'),
                             ], string="Covering Maintenance")

# class claim_docs_name(models.Model):
#     _name = 'claim.docs.name'
#     _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
#     _description = 'claim_docs_name'
#
#     name = fields.Char(string='Name')
