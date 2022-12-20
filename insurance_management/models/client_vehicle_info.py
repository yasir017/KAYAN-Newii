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
    vehicle_type = fields.Many2one('vehicle.type',"Vehicle Type")
    plate_no = fields.Char(string='Plate No. (En)',placeholder="1234 A-B-C")
    plate_no_ar = fields.Char(string='Plate No. (Ar)')
    model = fields.Selection([(str(num), str(num)) for num in range(1900, (datetime.now().year)+1 )],string="Vehicle Year")
    chasis_no = fields.Char(string='Chasis')
    capacity = fields.Integer(string='Capacity')
    driver_insurance = fields.Boolean(string='Driver Insurance')
    covering_maintenance = fields.Selection([('work_shop', 'Workshop'),('agency', 'Agency')], string="Covering Maintenance")
    value = fields.Char(string='Sum Insured')
    owner_name = fields.Char(string='Owner Name')
    owner_id_no = fields.Char(string='Owner ID No')
    custom_id = fields.Char(string='Custom ID')
    sequence_no = fields.Char(string='Sequence No')
    user_id_no = fields.Char(string='User ID No')
    user_name = fields.Char(string='User Name')
    building_no = fields.Char(string='Building No')
    additional_no = fields.Char(string='Additional No')
    street = fields.Char(string='Street')
    country = fields.Many2one('res.country', 'Country')
    city = fields.Many2one('res.country.state',string='City')
    unit_no = fields.Char(string='Unit No')
    po_box = fields.Char(string='PO. BOX')
    zip_code = fields.Char(string='Zip Code')
    neighborhead = fields.Char(string='Neighborhead')
    mobile_no = fields.Char(string='Mobile No')
    exp_date_istemara_hijry = fields.Date(string='Expiry Date of Istemara (Hijry)')
    exp_date_en = fields.Date(string='Expiry Date EN.')
    vehicle_color = fields.Char(string='Vehicle Color')
    gcc_covering = fields.Boolean(string='GCC Covering')
    natural_peril_cover = fields.Boolean(string='Natural Peril Cover')
    dob_owner = fields.Char(string='DOB of Owner (AD)')
    nationality = fields.Many2one('res.country',string='Nationality')
    customer_branch_id = fields.Many2one('client.branch', string='Customer Branch ID')
    customer_id = fields.Many2one(related='customer_branch_id.customer_id',store=True)
    document_no = fields.Char(related='customer_branch_id.document_no',string='Document No',store=True)
    state = fields.Selection(related='customer_branch_id.state',store=True)
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand',string='Vehicle Manufacturer')
    vehicle_model_id = fields.Many2one('fleet.vehicle.model',string='Vehicle Model',domain="[('brand_id', '=?', vehicle_make_id)]")
    note = fields.Text(string='Note')

    @api.onchange('vehicle_make_id')
    def set_model_wrt_vehicle_make_id(self):
        for rec in self:
            if rec.vehicle_model_id:
                if rec.vehicle_model_id.brand_id.id != rec.vehicle_make_id.id:
                    rec.vehicle_model_id = False

    @api.onchange('vehicle_model_id')
    def set_make_wrt_vehicle_model_id(self):
        for rec in self:
            rec.vehicle_make_id = rec.vehicle_model_id.brand_id.id

    @api.onchange('country')
    def set_city_wrt_country(self):
        for rec in self:
            if rec.city:
                if rec.city.id not in rec.country.state_ids.ids:
                    rec.city = False

    @api.onchange('city')
    def set_country_wrt_state_id(self):
        for rec in self:
            if rec.city:
                if not rec.country:
                    rec.country = rec.city.country_id.id
                elif rec.country.id != rec.city.country_id.id:
                    rec.country = rec.city.country_id.id

    @api.model
    def create(self, vals):
        res = super(client_vehicle_info, self).create(vals)
        for rec in res:
            if rec.plate_no:
                # 1234 A-B-C
                int_ap = rec.plate_no.split(" ", 1)
                integer_part = int_ap[0]
                if len(integer_part) != 4:
                    raise ValidationError("The Plate No. is not According to given Format!")
                integer_part_list = list(integer_part)
                for a in integer_part_list:
                    if a not in ['1','2','3','4','5','6','7','8','9','0']:
                        raise ValidationError("The Plate No. is not According to given Format!")


                string_part = int_ap[1]
                string_part_list = string_part.split('-')
                if len(string_part_list) != 3:
                    raise ValidationError("The Plate No. is not According to given Format!")
                for s in string_part_list:
                    if not s.isalpha():
                        raise ValidationError("The Plate No. is not According to given Format!")
                    elif not s.isupper():
                        raise ValidationError("The Plate No. is not According to given Format Alphabet must be in capital letters!")
        return res
