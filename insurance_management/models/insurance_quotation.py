# -*- coding: utf-8 -*-
import pdb
from odoo.tools.misc import file_open, formatLang
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date
from xlrd import open_workbook
import xlrd
import logging
from datetime import datetime, timedelta
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _,exceptions
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)
import io
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
try:
    from base64 import encodebytes
except ImportError:
    from base64 import encodestring as encodebytes
    _logger.debug('Cannot `import base64`.')



class insurance_quotation(models.Model):
    _name = 'insurance.quotation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'insurance_quotation'
    _rec_name = 'insurance_company_id'

    insurance_company_id = fields.Many2one('insurance.company',string='Company',required='1')
    date = fields.Date(string='Date')
    email = fields.Char(string='Email')
    state = fields.Selection([('draft','Draft'),('selected','Selected'),('cancel','Cancel')],string='state',default='draft')
    quotation_line_ids = fields.One2many('quotation.line','insurance_quotation_id',string='Quotation Lines')
    client_branch_id = fields.Many2one('client.branch',string='Client Branch')
    document_no = fields.Char(related='client_branch_id.document_no', string='Document No')
    quotation_file = fields.Binary(string='Upload File')
    total_tax = fields.Float(string='Total Vat',compute='get_total_rate_tax_amount')
    amount = fields.Float(string='Total After Vat',compute='get_total_rate_vat_amount')
    total_rate = fields.Float(string='Total Premium',compute='get_total_rate_vat_amount')
    select = fields.Boolean(string='Select')
    custom_benefits_ids = fields.One2many('customer.custom.benefit','insurance_quotation_id',string='Benefits')
    quotation_no = fields.Char(string='Quotation Number')
    total_lines = fields.Integer(string='Total Lines',compute='get_total_lines')
    @api.depends('quotation_line_ids')
    def get_total_lines(self):
        for rec in self:
            rec.total_lines = len(rec.quotation_line_ids)

    @api.model
    def create(self, vals):
        res = super(insurance_quotation, self).create(vals)
        for rec in res:
            if rec.insurance_company_id.auto_map_benefits_to_quotation == True:
                for benefit in rec.insurance_company_id.company_benefit_ids:
                    vals = {
                        'category_type' : benefit.category_type,
                        'benefit_id' : benefit.benefit_id.id,
                        'benefit_name' : benefit.benefit_id.name,
                        'name' : benefit.name,
                        'display_type' : benefit.display_type,
                        'sequence' : benefit.sequence,
                        'insurance_quotation_id' : rec.id,
                    }
                    custom_benefit = self.env['customer.custom.benefit'].create(vals)
        return res

    def get_total_rate_tax_amount(self):

        for rec in self:
            total_tax_amount = 0
            for line in rec.quotation_line_ids:
                total_tax_amount += line.rate*line.vat/100
            rec.total_tax = total_tax_amount
    def get_total_rate_vat_amount(self):
        for rec in self:
            rec.total_rate = sum(rec.quotation_line_ids.mapped('rate'))
            rec.amount = sum(rec.quotation_line_ids.mapped('total'))

    def download_export_template(self):
        client_quoite_template = self.env['ir.attachment'].search([('is_client_quoit_temp','=',True)],limit=1)
        if not client_quoite_template:
            file_temp = file_open(
                'insurance_management/data/Client Quotation Template.xlsx', "rb"
            ).read()
            encoded_file = base64.b64encode(file_temp)
            client_quoite_template = self.env['ir.attachment'].create({
                'type': 'binary',
                'name': "Client Medical Quotation Template"+'.xls',
                'datas': encoded_file,
                'is_client_quoit_temp': True,
                'description': 'Client Medical Quotation Template',
            })
        # wizard_data = self.env['download.attachment.wiz'].create({'attachment_id':client_quoite_template.id})
        return {
            'name': 'Download Template',
            'views': [
                (self.env.ref('insurance_management.view_attachment_form_ccc').id, 'form'),
            ],
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'res_id': client_quoite_template.id,
            'target': 'new',
        }


    def upload_quotation(self):
        active_id = self._context.get('active_id', False)
        self.write({'client_branch_id':active_id})

        wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.quotation_file))
        quotation_lines_vals_list = []
        for sheet in wb.sheets():
            for row in range(sheet.nrows):
                if row < 6:
                    continue
                else:
                    client_technical_id = sheet.cell(row, 0).value
                    member_id = sheet.cell(row, 1).value
                    dependent_id = sheet.cell(row, 2).value
                    member_name = sheet.cell(row, 3).value
                    member_name_arabic = sheet.cell(row, 4).value
                    dob = sheet.cell(row, 5).value
                    age = sheet.cell(row, 6).value
                    dob_hijra = sheet.cell(row, 7).value
                    member_type = sheet.cell(row, 8).value
                    gender = sheet.cell(row, 9).value
                    class_no = sheet.cell(row, 10).value
                    risk_no = sheet.cell(row, 11).value
                    nationality = sheet.cell(row, 12).value
                    staff_no = sheet.cell(row, 13).value
                    member_category = sheet.cell(row, 14).value
                    mobile1 = sheet.cell(row, 15).value
                    mobile2 = sheet.cell(row, 16).value
                    dep_code = sheet.cell(row, 17).value
                    sponser_id = sheet.cell(row, 18).value
                    occupation = sheet.cell(row, 19).value
                    marital_status = sheet.cell(row, 20).value
                    vat = sheet.cell(row, 21).value
                    rate = sheet.cell(row, 22).value
                    vals = {
                        'member_id': member_id,
                        'dependent_id': dependent_id,
                        'name': member_name,
                        'arabic_name': member_name_arabic,
                        # 'dob': str(dob),
                        'age': age,
                        # 'dob_hijra': dob_hijra,
                        # 'member_type': member_type,
                        'gender': gender,
                        # 'class_no': class_no,
                        'risk_no': risk_no,
                        'nationality': nationality,
                        'staff_no': staff_no,
                        'mobile1': mobile1,
                        'mobile2': mobile2,
                        'dep_no': dep_code,
                        'sponser_id': sponser_id,
                        # 'occupation': occupation,
                        'vat': vat,
                        'branch_id': self.client_branch_id.id,
                        'rate': rate,
                        # 'insurance_quotation_id': self.id,
                    }
                    if marital_status != '':
                        marital_status = self.env['member.relation'].search([('name', '=', marital_status)], limit=1)
                        if marital_status:
                            vals.update({'marital_status': marital_status.id})
                    member_category = self.env['member.category'].search([('name', '=', str(member_category))], limit=1)
                    if member_category:
                        vals.update({'member_category': member_category.id})
                    # nationality = self.env['res.country'].search([('name', '=', str(nationality))], limit=1)
                    # if nationality:
                    #     vals.update({'nationality': nationality.id})

                    company_member_type_standard = self.env['company.member.type.standard'].search([('name', '=', str(member_type))], limit=1)
                    if company_member_type_standard:
                        vals.update({'member_type': company_member_type_standard.member_type_standard_id.id})

                    company_class_standard = self.env['company.class.standard'].search([('name', '=', str(class_no))], limit=1)
                    if company_class_standard:
                        vals.update({'class_no': company_class_standard.class_standard_id.id})

                    client_id = self.env['client.basic.info'].search([('id','=',int(client_technical_id))])
                    if client_id:
                        vals.update({'client_id': client_id.id})
                    occupation = self.env['ins.occupation'].search([('name', '=', occupation)],limit=1)
                    if occupation:
                        vals.update({'occupation': occupation.id})

                    quotation_lines_vals_list.append((0, 0, vals))

        self.quotation_line_ids = quotation_lines_vals_list


class quotation_line(models.Model):
    _name = 'quotation.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'quotation_lines'

    # def _get_related_clients(self):
    #     active_id = self._context.get('active_id', False)
    #     pdb.set_trace()
    #     return self.env['client.basic.info'].search([('client_branch_id','=',active_id)]).mapped('id')


    insurance_quotation_id = fields.Many2one('insurance.quotation',string='Insurance Quotation')
    insurance_company_id = fields.Many2one(related='insurance_quotation_id.insurance_company_id', string='Company',
                                           store=True)
    client_branch_id = fields.Many2one(related='insurance_quotation_id.client_branch_id', string='Client Branch')
    related_client_ids = fields.Many2many('client.basic.info',string='Client IDS',compute='_get_related_clients')
    client_id = fields.Many2one('client.basic.info',string='Client ID')
    vat = fields.Float(string='VAT',default=15)
    total = fields.Float(string='Total',compute='get_q_line_total')
    rate = fields.Float(string='Premium')
    member_id = fields.Char(string='Member ID')
    dependent_id = fields.Char(string='Dependent ID')
    name = fields.Char(string='Member Name (En)', tracking=True)
    client_image = fields.Binary(string='Client Image')
    arabic_name = fields.Char(string='Member Name (Ar)', tracking=True)
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female')], string='Gender')
    dob = fields.Date(string='Birth Date')
    dob_hijra = fields.Char(string='Birth Date(Hijra)')
    age = fields.Float(string='Age', compute='get_member_age')
    member_type = fields.Many2one('member.type.standard',string='Member Type')
    class_no = fields.Many2one('class.name.standard',string='Class No')
    age_category = fields.Many2one('age.category.standard', string='Age Category')
    risk_no = fields.Char(string='Risk No')
    nationality = fields.Many2one('res.country', string='Nationality')
    staff_no = fields.Char(string='Staff No')
    # member_category = fields.Selection(
    #     [('Manager', 'Manager'), ('Staff', 'Staff'), ('Skilled Worker', 'Skilled Worker'),
    #      ('Supervisor', 'Supervisor')], string='Member Category')
    member_category = fields.Many2one('member.category', string='Member Category')
    mobile1 = fields.Char(string='Mobile No (1)')
    mobile2 = fields.Char(string='Mobile No (2)')
    dep_no = fields.Char(string='Dep Code')
    sponser_id = fields.Char(string='Sponser ID')
    occupation = fields.Many2one('ins.occupation',string='Occupation')
    # marital_status = fields.Selection(
    #     [('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed')],
    #     string='Relation')
    marital_status = fields.Many2one('member.relation', string='Relation')
    vip = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='VIP?')
    as_vip = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='AS VIP?')
    bank_id = fields.Many2one('res.bank', string='Bank')
    branch_id = fields.Many2one('client.branch', string='Branch ID')
    @api.depends('vat','rate')
    def get_q_line_total(self):
        for rec in self:
            total_percentage_amount = rec.rate * rec.vat / 100
            rec.total = rec.rate + total_percentage_amount

    @api.depends('dob')
    def get_member_age(self):
        for rec in self:
            if rec.dob:
                born = rec.dob
                today = date.today()
                rec.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                rec.age = 0

    @api.depends('client_branch_id')
    def _get_related_clients(self):
        for rec in self:
            rec.related_client_ids = rec.client_branch_id.client_ids.ids or False


class vehicle_quotation(models.Model):
    _name = 'vehicle.quotation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'vehicle_quotation'
    _rec_name = 'insurance_company_id'

    insurance_company_id = fields.Many2one('insurance.company',string='Company',required='1')
    date = fields.Date(string='Date')
    email = fields.Char(string='Email')
    state = fields.Selection([('draft','Draft'),('in_review','In Review'),('selected','Selected'),('cancel','Cancel')],string='state',default='draft')
    vehicle_quotation_line_ids = fields.One2many('vehicle.quotation.line','vehicle_quotation_id',string='Vehicle Quotation Lines')
    client_branch_id = fields.Many2one('client.branch',string='Client Branch')
    document_no = fields.Char(related='client_branch_id.document_no', string='Document No')
    quotation_file = fields.Binary(string='Upload File')
    total_vat = fields.Float(string='Total VAT',compute='get_total_rate_vat_amount')
    amount = fields.Float(string='Total After Vat', compute='get_total_rate_vat_amount')
    total_rate = fields.Float(string='Total Premium', compute='get_total_rate_vat_amount')
    select = fields.Boolean(string='Select')

    # ******************vehicle Covering Page*******************

    issuance_fee_car = fields.Float("Issuance Fee")
    personal_accident_driver = fields.Float("Personal Accident For Driver")
    personal_accident_for_passenger = fields.Float("Personal Accident For Passengers")
    car_hire = fields.Float("Car Hire")
    geo_ext = fields.Float("Geographical Extension")
    zero_dep = fields.Float("Zero Depreciation")
    towing_vehicle = fields.Float("Towing Vehicle")
    key_loss_thef_coverage = fields.Float('Coverage for key loss or theft')
    glass_coverage = fields.Float('Glass Coverage')
    personal_holding_in_vehicle = fields.Float('Personal holdings in vehicle')
    vehicle_custom_benefits_ids = fields.One2many('vehicle.custom.benefit', 'vehicle_quotation_id', string='Benefits')
    quotation_no = fields.Char(string='Quotation Number')

    total_lines = fields.Integer(string='Total Lines', compute='get_total_lines')

    def export_vehicle_quoit_template(self):
        vehicle_quoite_template = self.env['ir.attachment'].search([('is_vehicle_quoit_temp','=',True)],limit=1)
        if not vehicle_quoite_template:
            file_temp = file_open(
                'insurance_management/data/Vehicle Quotation Template.xlsx', "rb"
            ).read()
            encoded_file = base64.b64encode(file_temp)
            vehicle_quoite_template = self.env['ir.attachment'].create({
                'type': 'binary',
                'name': "Client Vehicle Quotation Template"+'.xls',
                'datas': encoded_file,
                'is_vehicle_quoit_temp': True,
                'description': 'Client Vehicle Quotation Template',
            })
        # wizard_data = self.env['download.attachment.wiz'].create({'attachment_id':client_quoite_template.id})
        return {
            'name': 'Download Template',
            'views': [
                (self.env.ref('insurance_management.view_attachment_form_ccc').id, 'form'),
            ],
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'res_id': vehicle_quoite_template.id,
            'target': 'new',
        }

    @api.depends('vehicle_quotation_line_ids')
    def get_total_lines(self):
        for rec in self:
            rec.total_lines = len(rec.vehicle_quotation_line_ids)

    def get_total_rate_vat_amount(self):
        for rec in self:
            rec.total_rate = sum(rec.vehicle_quotation_line_ids.mapped('rate'))
            rec.amount = sum(rec.vehicle_quotation_line_ids.mapped('total'))

            for rec in self:
                total_tax_amount = 0
                for line in rec.vehicle_quotation_line_ids:
                    total_tax_amount += line.rate * line.vat / 100
                rec.total_vat = total_tax_amount

    def get_total_rate(self):
        for rec in self:
            rec.total_rate = sum(rec.vehicle_quotation_line_ids.mapped('rate'))

    def upload_quotation(self):
        active_id = self._context.get('active_id', False)
        self.write({'client_branch_id': active_id})

        wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.quotation_file))
        quotation_lines_vals_list = []
        for sheet in wb.sheets():
            for row in range(sheet.nrows):
                if row < 6:
                    continue
                else:
                    vehicle_client_id = sheet.cell(row, 0).value
                    vehicle_type = sheet.cell(row, 1).value
                    plate_no = sheet.cell(row, 2).value
                    model = sheet.cell(row, 3).value
                    # pdb.set_trace()
                    chasis_no = sheet.cell(row, 4).value
                    capacity = sheet.cell(row, 5).value
                    driver_insurance = sheet.cell(row, 6).value
                    repair = sheet.cell(row, 7).value
                    value = sheet.cell(row, 8).value
                    owner_name = sheet.cell(row, 9).value
                    owner_id_no = sheet.cell(row, 10).value
                    custom_id = sheet.cell(row, 11).value
                    sequence_no = sheet.cell(row, 12).value
                    user_id_no = sheet.cell(row, 13).value
                    user_name = sheet.cell(row, 14).value
                    building_no = sheet.cell(row, 15).value
                    additional_no = sheet.cell(row, 16).value
                    street = sheet.cell(row, 17).value
                    city = sheet.cell(row, 18).value
                    unit_no = sheet.cell(row, 19).value
                    po_box = sheet.cell(row, 20).value
                    zip_code = sheet.cell(row, 21).value
                    neighborhead = sheet.cell(row, 22).value
                    mobile_no = sheet.cell(row, 23).value
                    exp_date_istemara_hijry = sheet.cell(row, 24).value
                    vehicle_color = sheet.cell(row, 25).value
                    gcc_covering = sheet.cell(row, 26).value
                    natural_peril_cover = sheet.cell(row, 27).value
                    dob_owner = sheet.cell(row, 28).value
                    nationality = sheet.cell(row, 29).value
                    vat = sheet.cell(row, 30).value
                    rate = sheet.cell(row, 31).value
                    vals = {
                            # 'vehicle_type': vehicle_type,
                            'plate_no': plate_no,
                            # 'model': model,
                            'chasis_no': chasis_no,
                            'capacity': capacity,
                            'driver_insurance': driver_insurance,
                            'covering_maintenance': repair,
                            # 'sum_insured': value,
                            'owner_name': owner_name,
                            'owner_id_no': owner_id_no,
                            'custom_id': custom_id,
                            'sequence_no': sequence_no,
                            'user_id_no': user_id_no,
                            'user_name': user_name,
                            'building_no': building_no,
                            'additional_no': additional_no,
                            'street': street,
                            # 'city': city,
                            'unit_no': unit_no,
                            'po_box': po_box,
                            'zip_code': zip_code,
                            'neighborhead': neighborhead,
                            'mobile_no': mobile_no,
                            # 'exp_date_istemara_hijry': exp_date_istemara_hijry,
                            'vehicle_color': vehicle_color,
                            'gcc_covering': gcc_covering,
                            'natural_peril_cover': natural_peril_cover,
                            # 'dob_owner': str(dob_owner),
                            # 'customer_branch_id': self.id,
                            'vat': vat,
                            'rate': rate,
                    }
                    nationality = self.env['res.country'].search([('name', '=', str(nationality))], limit=1)
                    if nationality:
                        vals.update({'nationality': nationality.id})

                    vehicle_client_id = self.env['client.vehicle.info'].search([('id', '=', int(vehicle_client_id))])

                    if vehicle_client_id:
                        vals.update({'vehicle_client_id': vehicle_client_id.id})

                    quotation_lines_vals_list.append((0, 0, vals))

        self.vehicle_quotation_line_ids = quotation_lines_vals_list

class vehicle_quotation_line(models.Model):
    _name = 'vehicle.quotation.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'vehicle_quotation_lines'


    vehicle_quotation_id = fields.Many2one('vehicle.quotation',string='Vehicle Quotation')
    insurance_company_id = fields.Many2one(related='vehicle_quotation_id.insurance_company_id', string='Company', store=True)
    client_branch_id = fields.Many2one(related='vehicle_quotation_id.client_branch_id', string='Client Branch')
    related_vehicle_client_ids = fields.Many2many('client.vehicle.info',string='Client IDS',compute='_get_related_vehicle_clients')
    vehicle_client_id = fields.Many2one('client.vehicle.info',string='Client ID')

    vat = fields.Float(string='VAT', default=15)
    total = fields.Float(string='Total', compute='_get_q_line_total')
    rate = fields.Float(string='Premium')

    vehicle_image = fields.Binary(string='Vehicle Image')
    vehicle_type = fields.Many2one('vehicle.type',"Vehicle Type")
    plate_no = fields.Char(string='Plate No. (En)')
    plate_no_ar = fields.Char(string='Plate No. (Ar)')
    model = fields.Selection([(str(num), str(num)) for num in range(1900, (datetime.now().year)+1 )],string="Vehicle Year")
    chasis_no = fields.Char(string='Chasis')
    capacity = fields.Integer(string='Capacity')
    driver_insurance = fields.Boolean(string='Driver Insurance')
    covering_maintenance = fields.Selection([('work_shop', 'Workshop'),('agency', 'Agency')], string="Covering Maintenance")
    # value = fields.Char(string='Value')
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
    city = fields.Many2one('res.country.state','City',domain="[('country_id', '=', country)]")
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
    dob_owner = fields.Date(string='DOB of Owner (AD)')
    nationality = fields.Many2one('res.country', string='Nationality')
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand', string='Vehicle Manufacturer')
    vehicle_model_id = fields.Many2one('fleet.vehicle.model', string='Vehicle Model' ,domain="[('brand_id', '=?', vehicle_make_id)]")
    sum_insured = fields.Float("Sum Insured")

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

    @api.depends('vat', 'rate')
    def _get_q_line_total(self):
        for rec in self:
            total_percentage_amount = rec.rate*rec.vat/100
            rec.total = rec.rate + total_percentage_amount


    # def get_member_age(self):
    #     for rec in self:
    #         if rec.dob:
    #             born = rec.dob
    #             today = date.today()
    #             rec.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    #         else:
    #             rec.age = 0

    @api.depends('client_branch_id')
    def _get_related_vehicle_clients(self):
        for rec in self:
            rec.related_vehicle_client_ids = rec.client_branch_id.client_vehicle_ids.ids or False
