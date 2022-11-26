# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging



# class insurance_type(models.Model):
#     _name = 'insurance.type'
#     _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
#     _description = 'insurance_type'
#
#     request_category_id = fields.Many2one('request.category',string='Request Category')
#     # claim_ins_sub_type_ids = fields.One2many('claim.insurance.sub.type','claim_ins_type_id',string='Claim Insurance Sub Types')
#
#     @api.model
#     def create(self, vals):
#         res = super(insurance_type, self).create(vals)
#         for rec in res:
#             vals = {
#                 'name':rec.name,
#                 'code':rec.name,
#             }
#             self.env['request.category'].create(vals)
#         return res
#
#
# class claim_insurance_sub_type(models.Model):
#     _name = 'claim.insurance.sub.type'
#     _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
#     _description = 'claim_insurance_sub_type'
#
#     name = fields.Char(string='Name')
#     claim_ins_type_id = fields.Many2one('claim.insurance.type',string='Claim Insurance Type')
#     sequence = fields.Integer(string='Sequence')

# class RequestCategory(models.Model):
#     _inherit = "request.category"
#
#     claim_ins_type_id = fields.Many2one('claim.insurance.type',string='Claim Insurance Type')
#
#
# class RequestType(models.Model):
#     _inherit = "request.type"
#
#     claim_ins_sub_type_id = fields.Many2one('claim.insurance.sub.type', string='Claim Insurance Sub Type')

