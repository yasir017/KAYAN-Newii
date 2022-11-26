# -*- coding: utf-8 -*-
import pdb
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging
from datetime import datetime, timedelta



class client_vehicle_info(models.Model):
    _name = 'client.vehicle.info'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'client_vehicle_info'
    _rec_name = 'owner_name'

    vehicle_image = fields.Binary(string='Vehicle Image')
    vehicle_type = fields.Char(string='Vehicle Type')
    plate_no = fields.Char(string='Plate No. (En)')
    plate_no_ar = fields.Char(string='Plate No. (Ar)')
    model = fields.Selection([(str(num), str(num)) for num in range(1900, (datetime.now().year)+1 )],string="Vehicle Year")
    chasis_no = fields.Char(string='Chasis')
    capacity = fields.Char(string='Capacity')
    driver_insurance = fields.Char(string='Driver Insurance')
    covering_maintenance = fields.Selection([('work_shop', 'Workshop'),('agency', 'Agency')], string="Covering Maintenance")
    value = fields.Char(string='Value')
    owner_name = fields.Char(string='Owner Name')
    owner_id_no = fields.Char(string='Owner ID No')
    custom_id = fields.Char(string='Custom ID')
    sequence_no = fields.Char(string='Sequence No')
    user_id_no = fields.Char(string='User ID No')
    user_name = fields.Char(string='User Name')
    building_no = fields.Char(string='Building No')
    additional_no = fields.Char(string='Additional No')
    street = fields.Char(string='Street')
    city = fields.Char(string='City')
    unit_no = fields.Char(string='Unit No')
    po_box = fields.Char(string='PO. BOX')
    zip_code = fields.Char(string='Zip Code')
    neighborhead = fields.Char(string='Neighborhead')
    mobile_no = fields.Char(string='Mobile No')
    exp_date_istemara_hijry = fields.Date(string='Expiry Date of Istemara (Hijry)')
    vehicle_color = fields.Char(string='Vehicle Color')
    gcc_covering = fields.Char(string='GCC Covering')
    natural_peril_cover = fields.Char(string='Natural Peril Cover')
    dob_owner = fields.Char(string='DOB of Owner (AD)')
    nationality = fields.Many2one('res.country',string='Nationality')
    customer_branch_id = fields.Many2one('client.branch', string='Customer Branch ID')
    document_no = fields.Char(related='customer_branch_id.document_no',string='Document No')
    state = fields.Selection(related='customer_branch_id.state',store=True)
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand',string='Vehicle Make')
    vehicle_model_id = fields.Many2one('fleet.vehicle.model',string='Vehicle Model')
