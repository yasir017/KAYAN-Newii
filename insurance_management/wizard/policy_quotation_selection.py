import pdb

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _,exceptions
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import file_open, formatLang
import pandas as pd
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

class PolicySelectionQuotation(models.TransientModel):
    _name = "policy.selection.quotation"
    _description = "policy.selection.quotation"


    client_id = fields.Many2one('client.branch',string='Client')
    medical_visibility_check = fields.Boolean(related='client_id.medical_visibility_check',
                                              string='Medical Visibility Check',
                                              compute='get_insurance_pages_visibility')
    vehicle_visibility_check = fields.Boolean(related='client_id.vehicle_visibility_check',
                                              string='Vehicle Visibility Check',
                                              compute='get_insurance_pages_visibility')

    medical_quotation_id = fields.Many2one('insurance.quotation',string='Quotation')
    medical_quotation_lines = fields.Many2many('quotation.line', string='Clients')

    vehicle_quotation_id = fields.Many2one('vehicle.quotation',string='Quotation')
    vehicle_quotation_lines = fields.Many2many('vehicle.quotation.line',string='Clients')



    def action_confirm(self):
        if self.medical_quotation_id:
            insurance_company_id = self.medical_quotation_id.insurance_company_id.id
        elif self.vehicle_quotation_id:
            insurance_company_id = self.vehicle_quotation_id.insurance_company_id.id
        policy = self.env['insurance.policy'].create({
            'partner_id': self.client_id.customer_id.id,
            'policy_type': 'policy',
            'insurance_company_id': insurance_company_id,
            'insurance_type_id': self.client_id.insurance_type_id.id,
            'insurance_sub_type_id': self.client_id.insurance_sub_type_id.id,
            'company_standard': self.client_id.company_standard,
            'type_of_business': self.client_id.type_of_business,
            'data_collect_id': self.client_id.id,
            'country_id': self.client_id.country.id,
            'fed_state_id': self.client_id.state_id.id,
        })
        self.client_id.policy_id = policy.id

        if self.client_id.insurance_type_id.ins_type_select == 'is_medical':
            quotation = self.medical_quotation_id
            for benefits in quotation.custom_benefits_ids:
                benficreate = self.env['policy.benefits'].create({
                    'policy_id': policy.id,
                    'name': benefits.name,
                    'benefit_name': benefits.benefit_name,
                    'category_type': benefits.category_type,
                    'benefit_id': benefits.benefit_id.id,
                    'benefit_value': benefits.benefit_value,
                    'display_type': benefits.display_type,
                    'sequence': benefits.sequence,
                    'included': benefits.included,
                    'vary': benefits.vary,
                    'from_value': benefits.from_value,
                    'to_value': benefits.to_value,
                    # 'description':benefits.description,
                })
            for client in self.medical_quotation_lines:
                if client.create_policy ==True:
                    employee_data = self.env['insurance.employee.data'].create({

                        'policy_id': policy.id,
                        # 'group_id':client.group_id,
                        'member_id': client.member_id,
                        'dependent_id': client.dependent_id,
                        'name': client.name,
                        'client_image': client.client_image,
                        'arabic_name': client.arabic_name,
                        'gender': client.gender,
                        'dob': client.dob,
                        'dob_hijra': client.dob_hijra,
                        'age': client.age,
                        'member_type': client.member_type.id,
                        'class_no': client.class_no.id,
                        'age_category': client.age_category.id,
                        'risk_no': client.risk_no,
                        'nationality': client.nationality.id,
                        'staff_no': client.staff_no,
                        'member_category': client.member_category.id,
                        'mobile1': client.mobile1,
                        'mobile2': client.mobile2,
                        'dep_no': client.dep_no,
                        'sponser_id': client.sponser_id,
                        'occupation': client.occupation.id,
                        'marital_status': client.marital_status.id,
                        # 'elm_relation':client.elm_relation,
                        'vip': client.vip,
                        'as_vip': client.as_vip,
                        'bank_id': client.bank_id.id,
                        'branch_id': client.branch_id.id,
                        'rate': client.rate,
                        'vat': client.vat,
                        'total': client.total
                    })


        elif self.client_id.insurance_type_id.ins_type_select == 'is_vehicle':
            quotation_vehicle = self.vehicle_quotation_id
            for benefits in quotation_vehicle.vehicle_custom_benefits_ids:
                benficreate = self.env['policy.benefits'].create({
                    'policy_id': policy.id,
                    'name': benefits.name,
                    'benefit_name': benefits.benefit_name,
                    'category_type': benefits.category_type,
                    'benefit_id': benefits.benefit_id.id,
                    'benefit_value': benefits.benefit_value,
                    'display_type': benefits.display_type,
                    'sequence': benefits.sequence,
                    'included': benefits.included,
                    'vary': benefits.vary,
                    'from_value': benefits.from_value,
                    'to_value': benefits.to_value,
                    # 'description':benefits.description,
                })

            for quo_line in self.vehicle_quotation_lines:
                if quo_line.create_policy==True:
                    vehicle_data = self.env['insurance.vehicle'].create({
                        'policy_id': policy.id,
                        'vehicle_type_id': quo_line.vehicle_type.id,
                        'plate_no': quo_line.plate_no,
                        'model_no': quo_line.model,
                        'chassis': quo_line.chasis_no,
                        'capacity': quo_line.capacity,
                        'driver_insurance': quo_line.driver_insurance,
                        'covering_maintenance': quo_line.covering_maintenance,
                        'value': quo_line.sum_insured,
                        'owener_name': quo_line.owner_name,
                        'owner_id': quo_line.owner_id_no,
                        'custom_id': quo_line.custom_id,
                        'seq_no': quo_line.sequence_no,
                        'user_id_no': quo_line.user_id_no,
                        'user_name': quo_line.user_name,
                        'building_no': quo_line.building_no,
                        'additional_no': quo_line.additional_no,
                        'street': quo_line.street,
                        'city': quo_line.city.id,
                        'unit_no': quo_line.unit_no,
                        'po_box': quo_line.po_box,
                        'zip_code': quo_line.zip_code,
                        'neighbour_head': quo_line.neighborhead,
                        'mobile_no': quo_line.mobile_no,
                        'istamara_expiry': quo_line.exp_date_istemara_hijry,
                        'vehicle_color': quo_line.vehicle_color,
                        'gcc_cover': quo_line.gcc_covering,
                        'natural_peril_cover': quo_line.natural_peril_cover,
                        'dob_owner': quo_line.dob_owner,
                        'nationality': quo_line.nationality.id,
                        'vehicle_make_id': quo_line.vehicle_make_id.id,
                        'vehicle_model_id': quo_line.vehicle_model_id.id,
                        'premium': quo_line.rate,
                        'vat': quo_line.vat
                    })
            policy.update({
                'issuance_fee_car': quotation_vehicle.issuance_fee_car,
                'personal_accident_driver': quotation_vehicle.personal_accident_driver,
                'personal_accident_for_passenger': quotation_vehicle.personal_accident_for_passenger,
                'car_hire': quotation_vehicle.car_hire,
                'geo_ext': quotation_vehicle.geo_ext,
                'zero_dep': quotation_vehicle.zero_dep,
                'towing_vehicle': quotation_vehicle.towing_vehicle,
                'key_loss_thef_coverage': quotation_vehicle.key_loss_thef_coverage,
                'glass_coverage': quotation_vehicle.glass_coverage,
                'personal_holding_in_vehicle': quotation_vehicle.personal_holding_in_vehicle
            })
        # if self.medical_visibility_check == True:
        #     self.insurance_quotation_id.select = True
        #     self.insurance_quotation_id.state = "selected"
        #     for line in self.client_id.insurance_quotation_ids.filtered(lambda b: b.id != self.insurance_quotation_id.id):
        #         line.state = 'cancel'
        # if self.vehicle_visibility_check == True:
        #     self.vehicle_quotation_id.select = True
        #     self.vehicle_quotation_id.state = "selected"
        #     for line in self.client_id.vehicle_quotation_ids.filtered(
        #             lambda b: b.id != self.vehicle_quotation_id.id):
        #         line.state = 'cancel'
        # # self.client_id.state = 'validate'
        # self.client_id.is_selected_quotation = True
