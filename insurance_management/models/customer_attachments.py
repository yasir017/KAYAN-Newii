# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging



class customer_attachment(models.Model):
    _name = 'customer.attachment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'customer_attachment'

    name = fields.Many2one('list.required.docs',string='Name',required='1',domain="[('id','in',list_required_docs_ids)]")
    is_required = fields.Boolean(related='name.is_required',string='Is Required?')
    list_required_docs_ids = fields.One2many(related='client_branch_id.insurance_type_id.list_required_docs_ids')
    file = fields.Binary(string='File')
    # image_file = fields.Binary(string='File')
    # other_file = fields.Binary(string='File')
    file_type = fields.Selection(
        [('pdf', 'PDF'), ('image', 'Image'), ('other', 'Other')], string='File Type')
    state = fields.Selection(
        [('attached', 'Attached'), ('not_attached', 'Not-Attached')], string='Status',compute='get_attachment_status')
    client_branch_id = fields.Many2one('client.branch', string='Client Branch')
    policy_id = fields.Many2one('insurance.policy','Policy ID')
    @api.depends('file')
    def get_attachment_status(self):
        for rec in self:
            if rec.file:
                rec.state = 'attached'
            else:
                rec.state = 'not_attached'
