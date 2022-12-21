# -*- coding: utf-8 -*-
import pdb
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
from odoo.tools.misc import file_open, formatLang
from hijri_converter import Hijri, Gregorian
from hijri_converter import convert
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



class client_branch(models.Model):
    _name = 'client.branch'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'client_branch'
    _rec_name = 'customer_id'

    def _default_get_todos_list(self):
        check_list = self.env['client.checklist'].search([])
        if check_list:
            return check_list[0].check_list

    # def _get_default_country(self):
    #     self.env['res.country'].search([('country','=',)])
    # def _default_get_client_ifo_temp(self):
    #     file_temp = file_open(
    #         'insurance_management/data/temp_client_info.xlsx', "rb"
    #     ).read()
    #     encoded_file = base64.b64encode(file_temp)
    #     return encoded_file
    # def _default_get_vehicle_ifo_temp(self):
    #     file_temp = file_open(
    #         'insurance_management/data/vehicle_info_template.xlsx', "rb"
    #     ).read()
    #     encoded_file = base64.b64encode(file_temp)
    #     return encoded_file

    document_no = fields.Char(string='Document No')
    customer_id = fields.Many2one('res.partner',string='Customer',required='1')
    insurance_type_id = fields.Many2one('insurance.type',string='Insurance Type',required='1')
    insurance_sub_type_id = fields.Many2one('insurance.sub.type',string='Insurance Sub Type',domain="[('insurance_type_id','=',insurance_type_id)]")
    sales_employee = fields.Many2one('hr.employee',string='Sales Employee')
    supervisor = fields.Many2one('hr.employee',string='Supervisor')
    country = fields.Many2one('res.country', string='Country')
    state_id = fields.Many2one("res.country.state", string='Branch', ondelete='restrict',
                               domain="[('country_id', '=?', country)]")
    client_ids = fields.One2many('client.basic.info','branch_id',string='Clients')
    client_vehicle_ids = fields.One2many('client.vehicle.info','customer_branch_id',string='Vehicle Details')
    todos_list = fields.Html(string="To Do's", default=_default_get_todos_list)
    state = fields.Selection([('gather_info','Gather Info'),
                              ('review','Review'),
                              ('sent_to_insurance','Sent to Vendor'),
                              ('sent_to_customer','Sent to Customer'),('policy_issuance','Policy Issuance'),('validate','Validate'),
                              ('cancel','Cancel')],string='state',default='gather_info', tracking=True)
    import_client_file = fields.Binary(string='Upload Clients Data (.xls')
    # template_client_info_file = fields.Binary(string='Client Info Template',default=_default_get_client_ifo_temp)
    # template_vehicle_info_file = fields.Binary(string='Vehicle Info Template',default=_default_get_vehicle_ifo_temp)
    insurance_sent_attachment_ids = fields.Many2many('ir.attachment',string="Insurance Sent Attachment")
    insurance_quotation_ids = fields.One2many('insurance.quotation','client_branch_id',string='Medical Quotations')
    vehicle_quotation_ids = fields.One2many('vehicle.quotation','client_branch_id',string='Vehicle Quotations')
    # company_benefit_ids = fields.Many2many('insurance.company.benefit',string='Company Benefits')
    medical_visibility_check = fields.Boolean(string='Medical Visibility Check',compute='get_insurance_pages_visibility')
    vehicle_visibility_check = fields.Boolean(string='Vehicle Visibility Check',compute='get_insurance_pages_visibility')
    customer_attachment_ids = fields.One2many('customer.attachment','client_branch_id',string='Customer Attachments',ondelete='cascade')
    company_standard = fields.Selection([('sme','SME'),('corporate','Corporate')
                                         ],string='Company Standard')
    type_of_business = fields.Selection([('renewal','Renewal'),('new_business','New Business')
                                         ],string='Type of Business')
    renewal_policy_id = fields.Many2one('insurance.policy',string='Renewal Policy No')
    list_required_docs_ids = fields.One2many(related='insurance_type_id.list_required_docs_ids')
    total_clients_number = fields.Integer(string='Total Lines',compute='get_total_clients')
    total_document_number = fields.Integer(string='Total Documents',compute='get_total_documents')
    total_medical_quotation = fields.Integer(string='Medical Quotations',compute='get_total_medical_quotation')
    total_vehicle_quotation = fields.Integer(string='Vehicle Quotations',compute='get_total_vehicle_quotation')
    total_medical_line = fields.Integer(string='Medical Lines',compute='get_total_medical_lines')
    total_vehicle_detail = fields.Integer(string='Total Lines',compute='get_total_vehicle_detail')
    total_vehicle_line = fields.Integer(string='Total Vehicle Lines',compute='get_total_vehicle_line')
    is_selected_quotation = fields.Boolean(string='Is Quotation Selected?')
    # policy_id = fields.Many2one('insurance.policy','Policy')
    # crm_lead_id = fields.Many2one('crm.lead',string='CRM Lead',copy=False)

    def vendor_finishing(self):
        self.state = 'policy_issuance'

    def unlink(self):
        for rec in self:
            if rec.state == "validate":
                raise ValidationError("You can not delete record which is Validate State!")
        res = super(client_branch, self).unlink()
        return res

    @api.onchange('insurance_type_id')
    def set_ins_type_wrt_sub_type(self):
        for rec in self:
            if rec.insurance_sub_type_id:
                if rec.insurance_sub_type_id.id not in rec.insurance_type_id.insurance_subtype_ids.ids:
                    rec.insurance_sub_type_id = False

    @api.onchange('insurance_sub_type_id')
    def set_subtype_wrt_ins_type(self):
        for rec in self:
            if rec.insurance_sub_type_id:
                if not rec.insurance_type_id:
                    rec.insurance_type_id = rec.insurance_sub_type_id.insurance_type_id.id
                elif rec.insurance_type_id.id != rec.insurance_type_id.id:
                    rec.insurance_type_id = rec.insurance_sub_type_id.insurance_type_id.id

    @api.onchange('country')
    def set_city_wrt_country(self):
        for rec in self:
            if rec.state_id:
                if rec.state_id.id not in rec.country.state_ids.ids:
                    rec.state_id = False

    @api.onchange('state_id')
    def set_country_wrt_state_id(self):
        for rec in self:
            if rec.state_id:
                if not rec.country:
                    rec.country = rec.state_id.country_id.id
                elif rec.country.id != rec.state_id.country_id.id:
                    rec.country = rec.state_id.country_id.id

    def export_client_info_file_template(self):
        medical_info_template = self.env['ir.attachment'].search([('is_medical_info_temp','=',True)],limit=1)
        if not medical_info_template:
            file_temp = file_open(
                'insurance_management/data/temp_client_info.xlsx', "rb"
            ).read()
            encoded_file = base64.b64encode(file_temp)
            medical_info_template = self.env['ir.attachment'].create({
                'type': 'binary',
                'name': "Medical Information Template"+'.xls',
                'datas': encoded_file,
                'is_medical_info_temp': True,
                'description': 'Medical Information Template',
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
            'res_id': medical_info_template.id,
            'target': 'new',
        }

    def export_vehicle_info_file_template(self):
        vehicle_info_template = self.env['ir.attachment'].search([('is_vehicle_info_temp','=',True)],limit=1)
        if not vehicle_info_template:
            file_temp = file_open(
                'insurance_management/data/vehicle_info_template.xlsx', "rb"
            ).read()
            encoded_file = base64.b64encode(file_temp)
            vehicle_info_template = self.env['ir.attachment'].create({
                'type': 'binary',
                'name': "Client Vehicle Information Template"+'.xls',
                'datas': encoded_file,
                'is_vehicle_info_temp': True,
                'description': 'Client Vehicle Information Template',
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
            'res_id': vehicle_info_template.id,
            'target': 'new',
        }

    def action_open_benefits_wizard(self):
        action = self.env['ir.actions.act_window']._for_xml_id('insurance_management.action_comparison_benefit_wizard')

        action['context']={'default_client_id':self.id}
        # ctx = dict(self.env.context)
        # ctx.pop('active_id', None)
        # ctx['active_ids'] = self.ids
        # ctx['active_model'] = 'client.branch'
        # action['context'] = ctx
        return action


    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Client Information'),
            'template': 'insurance_management/data/temp_client_info.xlsx'
        }]

    policy_id = fields.Many2one('insurance.policy',"Policy",copy=False)
    count_policy = fields.Integer("Count Policy",compute='_count_total_policy',store=True)


    @api.depends('policy_id')
    def _count_total_policy(self):
        for rec in self:
            rec.count_policy=len(rec.policy_id)

    def action_create_policy(self):
        context = {'default_client_id': self.id}
        if self.medical_visibility_check == True:
            if any(self.insurance_quotation_ids.filtered(lambda b: b.select == True)):
                medical_selected_quotation = self.insurance_quotation_ids.filtered(lambda b: b.select == True)
                context.update({'default_medical_quotation_id': medical_selected_quotation[0].id,'default_medical_quotation_lines': medical_selected_quotation[0].quotation_line_ids.ids})
        if self.vehicle_visibility_check == True:
            if any(self.vehicle_quotation_ids.filtered(lambda b: b.select == True)):
                vehicle_selected_quotation = self.vehicle_quotation_ids.filtered(lambda b: b.select == True)
                context.update({'default_vehicle_quotation_id': vehicle_selected_quotation[0].id,'default_vehicle_quotation_lines': vehicle_selected_quotation[0].vehicle_quotation_line_ids.ids})

        return {
            'name': 'Select Clients for Policy',
            'views': [
                (self.env.ref('insurance_management.form_policy_selection_quotation_wizard_view').id, 'form'),
            ],
            'type': 'ir.actions.act_window',
            'res_model': 'policy.selection.quotation',
            'view_mode': 'form',
            'context': context,
            'target': 'new',
        }





    def action_policy_view(self):
         return {
                'name': 'policy',
                'type': 'ir.actions.act_window',
                'res_model': 'insurance.policy',
                'view_mode': 'tree,form',
                'domain': [('id', '=', self.policy_id.id)],
            }
    @api.onchange('insurance_type_id')
    def map_doc_list(self):
        doc_name_list = []
        self.customer_attachment_ids = False
        for line in self.insurance_type_id.list_required_docs_ids:
            vals = {
                'name': line.id,
            }
            doc_name_list.append((0, 0, vals))
        self.customer_attachment_ids = doc_name_list

    def validate(self):
        self.state = 'validate'

    def reset_to_draft(self):
        self.state = 'sent_to_customer'

    def action_open_medical_quotation_lines(self):
        medical_line_ids = []
        for line in self.insurance_quotation_ids:
            for q_line in line.quotation_line_ids:
                medical_line_ids.append(q_line.id)
        return {
            'name': 'Medical Quotation Lines',
            'type': 'ir.actions.act_window',
            'res_model': 'quotation.line',
            'view_mode': 'tree,form,pivot',
            'domain': [('id', 'in', medical_line_ids)],
        }

    def action_open_vehicle_quote_line(self):
        vehicle_line_ids = []
        for line in self.vehicle_quotation_ids:
            for q_line in line.vehicle_quotation_line_ids:
                vehicle_line_ids.append(q_line.id)
        return {
            'name': 'Vehicle Quotation Lines',
            'type': 'ir.actions.act_window',
            'res_model': 'vehicle.quotation.line',
            'view_mode': 'tree,form,pivot',
            'domain': [('id', 'in', vehicle_line_ids)],
        }

    def action_open_vehicle_quotation(self):
        return {
            'name': 'Vehicle Quotations',
            'type': 'ir.actions.act_window',
            'res_model': 'vehicle.quotation',
            'view_mode': 'tree,form,pivot',
            'domain': [('id', 'in', self.vehicle_quotation_ids.ids)],
        }
    def action_open_vehicle_detail(self):
        return {
            'name': 'Vehicle Details',
            'type': 'ir.actions.act_window',
            'res_model': 'client.vehicle.info',
            'views': [[self.env.ref('insurance_management.client_vehicle_info_smart_button_view_tree').id, 'list'],
                      [self.env.ref('insurance_management.client_vehicle_info_smart_button_view_form').id, 'form']],
            'view_mode': 'tree,form,pivot',
            'context': {
                'default_customer_branch_id': self.id,
            },
            'domain': [('id', 'in', self.client_vehicle_ids.ids)],
        }

    def action_open_client_details(self):
        return {
            'name': 'Client Details',
            'type': 'ir.actions.act_window',
            'res_model': 'client.basic.info',
            'views': [[self.env.ref('insurance_management.client_basic_info_smart_button_view_tree').id, 'list'],
                      [self.env.ref('insurance_management.client_basic_info_smart_button_view_form').id, 'form']],
            'view_mode': 'tree,form,pivot',
            'context': {
                'default_branch_id': self.id,
            },
            'domain': [('id', 'in', self.client_ids.ids)],
        }

    def action_open_medical_quotation(self):
        return {
            'name': 'Medical Quotations',
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.quotation',
            'view_mode': 'tree,form,pivot',
            'domain': [('id', 'in', self.insurance_quotation_ids.ids)],
        }

    @api.depends('vehicle_quotation_ids.vehicle_quotation_line_ids')
    def get_total_vehicle_line(self):
        for rec in self:
            total_vehicle_lines = 0
            for line in rec.vehicle_quotation_ids:
                total_vehicle_lines += len(line.vehicle_quotation_line_ids)
            rec.total_vehicle_line = total_vehicle_lines or 0
    @api.depends('insurance_quotation_ids.quotation_line_ids')
    def get_total_medical_lines(self):
        for rec in self:
            total_medical_lines = 0
            for line in rec.insurance_quotation_ids:
                total_medical_lines += len(line.quotation_line_ids)
            rec.total_medical_line = total_medical_lines or 0

    @api.depends('client_vehicle_ids')
    def get_total_vehicle_detail(self):
        for rec in self:
            rec.total_vehicle_detail = len(rec.client_vehicle_ids)

    @api.depends('vehicle_quotation_ids')
    def get_total_vehicle_quotation(self):
        for rec in self:
            rec.total_vehicle_quotation = len(rec.vehicle_quotation_ids)

    @api.depends('insurance_quotation_ids')
    def get_total_medical_quotation(self):
        for rec in self:
            rec.total_medical_quotation = len(rec.insurance_quotation_ids)

    def action_open_client_documents(self):
        return {
            'name': _('Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'kanban',
            'context': {
                'default_res_id': self.id,
                'default_res_model': self._name,
                'default_folder_id': self.env.ref('insurance_management.documents_client_data_folder').id,
                'default_tag_ids': [(6, 0, [self.env.ref('insurance_management.documents_document_data_tag').id] or [])],
            },
            'domain': [('res_id', '=', self.id),('res_model', '=', self._name)],
        }

    def action_open_crm(self):
        return {
            'name': _('CRM Lead'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'tree,form',
            'context': {
                'default_client_branch_id': self.id,
                'default_partner_id': self.customer_id.id,
            },
            'domain': [('client_branch_id', '=', self.id)],
        }
    def action_open_task(self):
        return {
            'name': "Task",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.task',
            # 'views': [(False, 'form')],
            'context': {
                'default_client_branch_id': self.id,
                'default_partner_id': self.customer_id.id,
            },
            'domain': [('client_branch_id', '=', self.id)],
        }

    def get_total_documents(self):
        for rec in self:
            rec.total_document_number = len(self.env['documents.document'].search([('res_id', '=', self.id),('res_model', '=', self._name)]))
    @api.depends('client_ids')
    def get_total_clients(self):
        for rec in self:
            rec.total_clients_number = len(rec.client_ids)

    def already_received_quotation(self):
        for rec in self:
            rec.state = 'sent_to_insurance'

    @api.model
    def create(self, vals):
        vals['document_no'] = self.env['ir.sequence'].next_by_code('client.info.seq')
        res = super(client_branch, self).create(vals)
        return res


    @api.depends('insurance_type_id')
    def get_insurance_pages_visibility(self):
        for rec in self:
            if rec.insurance_type_id.ins_type_select == 'is_medical':
                rec.medical_visibility_check = True
            else:
                rec.medical_visibility_check = False
            if rec.insurance_type_id.ins_type_select == 'is_vehicle':
                rec.vehicle_visibility_check = True
            else:
                rec.vehicle_visibility_check = False


    def import_client_file_data(self):
        if self.insurance_type_id.ins_type_select == 'is_medical':
            # for line in self.client_ids:
            #     print(line.dob)
            wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.import_client_file))
            sheet = wb.sheets()[0]
            for row in range(sheet.nrows):
                    if row == 0:
                        continue
                    if row == 1:
                        continue
                    else:
                        member_id = sheet.cell(row, 0).value
                        dependent_id = sheet.cell(row, 1).value
                        member_name = sheet.cell(row, 2).value
                        member_name_arabic = sheet.cell(row, 3).value
                        dob = sheet.cell(row, 4).value
                        age = sheet.cell(row, 5).value
                        dob_hijra = sheet.cell(row, 6).value
                        member_type = sheet.cell(row, 7).value
                        gender = sheet.cell(row, 8).value
                        class_no = sheet.cell(row, 9).value
                        risk_no = sheet.cell(row, 10).value
                        nationality = sheet.cell(row, 11).value
                        staff_no = sheet.cell(row, 12).value
                        member_category = sheet.cell(row, 13).value
                        mobile1 = sheet.cell(row, 14).value
                        mobile2 = sheet.cell(row, 15).value
                        dep_code = sheet.cell(row, 16).value
                        sponser_id = sheet.cell(row, 17).value
                        occupation = sheet.cell(row, 18).value
                        marital_status = sheet.cell(row, 19).value
                        # elm_relation = sheet.cell(row, 20).value
                        print(member_name)

                        vals = {
                            'member_id': member_id if member_id != '' else '',
                            'dependent_id': dependent_id if dependent_id != '' else '',
                            'name': member_name if member_name != '' else '',
                            'arabic_name': member_name_arabic if member_name_arabic != '' else '',
                            # 'dob': dob,
                            'age': age if age != '' else '',
                            # 'dob_hijra': dob_hijra,
                            # 'member_type': member_type,
                            'gender': gender if gender != '' else '',
                            # 'class_no': class_no,
                            'risk_no': risk_no if risk_no != '' else '',
                            # 'nationality': nationality if nationality != '' else '',
                            'staff_no': staff_no if staff_no != '' else '',
                            'mobile1': mobile1 if mobile1 != '' else '',
                            'mobile2': mobile2 if mobile2 != '' else '',
                            'dep_no': dep_code if dep_code != '' else '',
                            'sponser_id': sponser_id if sponser_id != '' else '',
                            # 'occupation': occupation if occupation != '' else '',
                            # 'elm_relation': elm_relation,
                            'branch_id': self.id,
                        }
                        if marital_status != '':
                            marital_status = self.env['member.relation'].search([('name', '=', marital_status)], limit=1)
                            if marital_status:
                                vals.update({'marital_status': marital_status.id})
                        if member_category != '':
                            member_category = self.env['member.category'].search([('name', '=', member_category)], limit=1)
                            if member_category:
                                vals.update({'member_category': member_category.id})
                        if nationality != '':
                            nationality = self.env['res.country'].search([('name', '=', nationality)], limit=1)
                            if nationality:
                                vals.update({'nationality': nationality.id})
                        member_type = self.env['member.type.standard'].search([('name', '=', str(member_type))],
                                                                              limit=1)
                        if member_type:
                            vals.update({'member_type': member_type.id})
                        class_no = self.env['class.name.standard'].search([('name', '=', str(class_no))], limit=1)
                        if class_no:
                            vals.update({'class_no': class_no.id})
                        occupation = self.env['ins.occupation'].search([('name', '=', str(occupation))], limit=1)
                        if occupation:
                            vals.update({'occupation': occupation.id})
                        if dob != '':
                            print(dob,'dob')
                            vals.update({'dob': dob})
                        if dob_hijra != '':
                            print(dob_hijra, 'dob_hijra')
                            vals.update({'dob_hijra': dob_hijra})
                        asn_line = self.env['client.basic.info'].create(vals)
        elif self.insurance_type_id.ins_type_select == 'is_vehicle':
            wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.import_client_file))
            for sheet in wb.sheets():
                for row in range(sheet.nrows):
                    if row == 0:
                        continue
                    else:
                        vehicle_type = sheet.cell(row, 0).value
                        plate_no = sheet.cell(row, 1).value
                        model = sheet.cell(row, 2).value
                        chasis_no = sheet.cell(row, 3).value
                        capacity = sheet.cell(row, 4).value
                        driver_insurance = sheet.cell(row, 5).value
                        repair = sheet.cell(row, 6).value
                        value = sheet.cell(row, 7).value
                        owner_name = sheet.cell(row, 8).value
                        owner_id_no = sheet.cell(row, 9).value
                        custom_id = sheet.cell(row, 10).value
                        sequence_no = sheet.cell(row, 11).value
                        user_id_no = sheet.cell(row, 12).value
                        user_name = sheet.cell(row, 13).value
                        building_no = sheet.cell(row, 14).value
                        additional_no = sheet.cell(row, 15).value
                        street = sheet.cell(row, 16).value
                        city = sheet.cell(row, 17).value
                        unit_no = sheet.cell(row, 18).value
                        po_box = sheet.cell(row, 19).value
                        zip_code = sheet.cell(row, 20).value
                        neighborhead = sheet.cell(row, 21).value
                        mobile_no = sheet.cell(row, 22).value
                        exp_date_istemara_hijry = sheet.cell(row, 23).value
                        vehicle_color = sheet.cell(row, 24).value
                        gcc_covering = sheet.cell(row, 25).value
                        natural_peril_cover = sheet.cell(row, 26).value
                        dob_owner = sheet.cell(row, 27).value
                        nationality = sheet.cell(row, 28).value
                        vals = {
                            'vehicle_type': vehicle_type,
                            'plate_no': plate_no,
                            'model': str(int(model)),
                            'chasis_no': chasis_no,
                            'capacity': capacity,
                            'driver_insurance': driver_insurance,
                            'covering_maintenance': repair,
                            'value': value,
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
                            'customer_branch_id': self.id,
                        }
                        nationality = self.env['res.country'].search([('name', '=', str(nationality))], limit=1)
                        if nationality:
                            vals.update({'nationality': nationality.id})
                        city = self.env['res.country.state'].search([('name', '=', str(city))], limit=1)
                        if city:
                            vals.update({'city': city.id})
                        client_vehicle_info = self.env['client.vehicle.info'].create(vals)



    def quotation_file_create_insurance_company(self,company):
        client_insurance_attachments = self.env['ir.attachment']
        if self.insurance_type_id.ins_type_select == 'is_medical':
            style = xlwt.easyxf('font:bold True;borders:left thin, right thin, top thin, bottom thin;')
            # style1 = xlwt.easyxf(num_format_str='MM/DD/YYYY HH:MM:SS')

            wb = xlwt.Workbook()
            worksheet = wb.add_sheet('Customer Information')
            worksheet.write(0, 0, 'Customer Information', style)
            # worksheet.write(0, 1, 'Product Name')
            worksheet.write(0, 2, 'Company Name.', style)
            worksheet.write(0, 3, company.name or '', style)
            worksheet.write(2, 0, 'Customer', style)
            worksheet.write(2, 1, self.customer_id.name or '', style)

            worksheet.write(3, 0, 'Date Time', style)
            worksheet.write(3, 1, str(fields.datetime.now()) or '', style)

            i = 1

            for i in range(0, 80):
                worksheet.col(i).width = int(20 * 260)

            rows = 5

            # worksheet.write(rows, 0, 'Client DB ID(for technical use)', style)
            worksheet.write(rows, 0, 'Member ID', style)
            worksheet.write(rows, 1, 'Dependent ID', style)
            worksheet.write(rows, 2, 'Member Name (English)', style)
            worksheet.write(rows, 3, 'Member Name (Arabic)', style)
            worksheet.write(rows, 4, 'Gregorian Birth Date', style)
            worksheet.write(rows, 5, 'Age', style)
            worksheet.write(rows, 6, 'Hajrah Birth Date', style)
            worksheet.write(rows, 7, 'Member type', style)
            worksheet.write(rows, 8, 'Gender', style)
            worksheet.write(rows, 9, 'Class no', style)
            worksheet.write(rows, 10, 'Risk No.', style)
            worksheet.write(rows, 11, 'Nationality', style)
            worksheet.write(rows, 12, 'Staff No.', style)
            worksheet.write(rows, 13, 'Member Category', style)
            worksheet.write(rows, 14, 'Mobile No. (1)', style)
            worksheet.write(rows, 15, 'Mobile No. (2)', style)
            worksheet.write(rows, 16, 'Dep Code', style)
            worksheet.write(rows, 17, 'Sponser ID', style)
            worksheet.write(rows, 18, 'Occupation', style)
            worksheet.write(rows, 19, 'Relation', style)
            worksheet.write(rows, 20, 'VAT', style)
            worksheet.write(rows, 21, 'Premium', style)
            rows += 1

            for line in self.client_ids:
                standard_type = False
                if line.branch_id.company_standard == 'sme':
                    standard_type = 'SME'
                elif line.branch_id.company_standard == 'corporate':
                    standard_type = 'Corporate'
                else:
                    standard_type = False
                company_member_type_standard = ''
                if line.member_type:
                    company_member_type_standard_env = self.env['company.member.type.standard'].search([('member_type_standard_id', '=', line.member_type.id),('insurance_company_id','=',company._origin.id)])
                    company_member_type_standard = company_member_type_standard_env.filtered(lambda b: standard_type in b.standard_type.mapped('name'))
                    if company_member_type_standard:
                        company_member_type_standard = company_member_type_standard[0].name or ''
                company_class_standard = ''
                if line.class_no:

                    # company_class_standard_env = self.env['company.class.standard'].search([])
                    # company_class_standard = company_class_standard_env.filtered(lambda b: standard_type in b.standard_type.mapped('name') and b.class_standard_id.id == line.class_no.id and b.insurance_company_id == )
                    company_class_standard_env = self.env['company.class.standard'].search([('class_standard_id', '=', line.class_no.id),('insurance_company_id','=',company._origin.id)])
                    company_class_standard = company_class_standard_env.filtered(lambda b: standard_type in b.standard_type.mapped('name'))
                    if company_class_standard:
                        company_class_standard = company_class_standard[0].name or ''
                # worksheet.write(rows, 0, line.id or '')
                worksheet.write(rows, 0, line.member_id or '')
                worksheet.write(rows, 1, line.dependent_id or '')
                worksheet.write(rows, 2, line.name or '')
                worksheet.write(rows, 3, line.arabic_name or '')
                worksheet.write(rows, 4, str(line.dob) if line.dob else '')
                worksheet.write(rows, 5, line.age or '')
                worksheet.write(rows, 6, line.dob_hijra or '')
                worksheet.write(rows, 7, company_member_type_standard or '')
                worksheet.write(rows, 8, line.gender or '')
                worksheet.write(rows, 9, company_class_standard or '')
                worksheet.write(rows, 10, str(line.risk_no) or '')
                worksheet.write(rows, 11, line.nationality.name or '')
                worksheet.write(rows, 12, line.staff_no or '')
                worksheet.write(rows, 13, line.member_category.name or '')
                worksheet.write(rows, 14, line.mobile1 or '')
                worksheet.write(rows, 15, line.mobile2 or '')
                worksheet.write(rows, 16, line.dep_no or '')
                worksheet.write(rows, 17, line.sponser_id or '')
                worksheet.write(rows, 18, line.occupation.name or '')
                worksheet.write(rows, 19, line.marital_status.name or '')
                worksheet.write(rows, 20, 15)

                rows += 1

            file_data = io.BytesIO()
            wb.save(file_data)
            attachment = self.env['ir.attachment'].create({
                'type': 'binary',
                'name': "Client Information TO "+ str(company.name) + '.xls',
                'datas': encodebytes(file_data.getvalue()),
                'is_medical': True,
                'insurance_company_id': company._origin.id,
                'description': company.name,
            })

            document = self.env['documents.document'].create({
                'name': attachment.name,
                'attachment_id': attachment.id,
                'type': 'empty',
                'folder_id': self.env.ref('insurance_management.documents_client_data_folder').id,
                'tag_ids': [(6, 0, [self.env.ref('insurance_management.documents_document_data_tag').id] or [])],
                'owner_id': self.env.user.id,
                'partner_id': company.ins_company_partner_id.id if company.ins_company_partner_id else False,
                'res_model': self._name,
                'res_id': self.id,
            })

            client_insurance_attachments += attachment
        if self.insurance_type_id.ins_type_select == 'is_vehicle':
            style = xlwt.easyxf('font:bold True;borders:left thin, right thin, top thin, bottom thin;')
            # style1 = xlwt.easyxf(num_format_str='MM/DD/YYYY HH:MM:SS')
            wb = xlwt.Workbook()
            worksheet = wb.add_sheet('Vehicle Information')
            worksheet.write(0, 0, 'Vehicle Information', style)
            # worksheet.write(0, 1, 'Product Name')
            worksheet.write(0, 2, 'Company Name.', style)
            worksheet.write(2, 0, 'Customer', style)
            # worksheet.write(2, 1, partner.name or '', style)

            worksheet.write(3, 0, 'Date Time', style)
            worksheet.write(3, 1, str(fields.datetime.now()) or '', style)

            i = 1

            for i in range(0, 80):
                worksheet.col(i).width = int(20 * 260)

            rows = 5

            worksheet.write(rows, 0, 'Client Vehicle ID(for technical use)', style)
            worksheet.write(rows, 1, 'Vehicle Type نوع السيارة', style)
            worksheet.write(rows, 2, 'Plate No.رقم اللوحة', style)
            worksheet.write(rows, 3, 'Model  سنة الصنع', style)
            worksheet.write(rows, 4, 'Chassisرقم الهيكل ', style)
            worksheet.write(rows, 5, 'Capacity السعة الإركابية', style)
            worksheet.write(rows, 6, 'Driver Insurance تأمين السائق', style)
            worksheet.write(rows, 7, 'Repair نوع الإصلاح', style)
            worksheet.write(rows, 8, 'Value القيمة السوقية', style)
            worksheet.write(rows, 9, 'Owner Name اسم المالك', style)
            worksheet.write(rows, 10, 'Owner ID No. رقم هوية المالك', style)
            worksheet.write(rows, 11, 'Custom ID رقم البطاقة الجمركية', style)
            worksheet.write(rows, 12, 'Sequence No. الرقم التسلسلي', style)
            worksheet.write(rows, 13, 'User ID No. رقم هوية المستخدم', style)
            worksheet.write(rows, 14, 'User Name اسم المستخدم', style)
            worksheet.write(rows, 15, 'Building No.  رقم المبنى', style)
            worksheet.write(rows, 16, 'Additional No. الرقم الإضافي', style)
            worksheet.write(rows, 17, ' Street اسم الشارع', style)
            worksheet.write(rows, 18, ' City المدينة', style)
            worksheet.write(rows, 19, 'Unit No. رقم الشقة', style)
            worksheet.write(rows, 20, 'PO. BOX صندوق البريد', style)
            worksheet.write(rows, 21, 'Zip Code الرمز البريدي', style)
            worksheet.write(rows, 22, 'Neighborhead اسم الحي', style)
            worksheet.write(rows, 23, 'Mobile number رقم الجوال', style)
            worksheet.write(rows, 24, 'Expiry Date of Istemara (Hijry) تاريخ انتهاء الاستمارة', style)
            worksheet.write(rows, 25, 'Vehicle COLOR لون المركبة', style)
            worksheet.write(rows, 26, 'GCC Covering التغطية الجغرافية', style)
            worksheet.write(rows, 27, 'NATURAL PERIL Cover تغطية الكوارث الطبيعية', style)
            worksheet.write(rows, 28, 'DOB for owner (AD) تاريخ ميلاد المالك', style)
            worksheet.write(rows, 29, 'NATIONALITY الجنسية', style)
            worksheet.write(rows, 30, 'VAT', style)
            worksheet.write(rows, 31, 'Premium', style)
            rows += 1

            for line in self.client_vehicle_ids:
                worksheet.write(rows, 0, line.id or '')
                worksheet.write(rows, 1, line.vehicle_type or '')
                worksheet.write(rows, 2, line.plate_no or '')
                worksheet.write(rows, 3, line.model or '')
                worksheet.write(rows, 4, line.chasis_no or '')
                worksheet.write(rows, 5, line.capacity or '')
                worksheet.write(rows, 6, line.driver_insurance or '')
                worksheet.write(rows, 7, line.covering_maintenance or '')
                worksheet.write(rows, 8, line.value or '')
                worksheet.write(rows, 9, line.owner_name or '')
                worksheet.write(rows, 10, line.owner_id_no or '')
                worksheet.write(rows, 11, line.custom_id or '')
                worksheet.write(rows, 12, line.sequence_no or '')
                worksheet.write(rows, 13, line.user_id_no or '')
                worksheet.write(rows, 14, line.user_name or '')
                worksheet.write(rows, 15, line.building_no or '')
                worksheet.write(rows, 16, line.additional_no or '')
                worksheet.write(rows, 17, line.street or '')
                worksheet.write(rows, 18, line.city or '')
                worksheet.write(rows, 19, line.unit_no or '')
                worksheet.write(rows, 20, line.po_box or '')
                worksheet.write(rows, 21, line.zip_code or '')
                worksheet.write(rows, 22, line.neighborhead or '')
                worksheet.write(rows, 23, line.mobile_no or '')
                worksheet.write(rows, 24, line.exp_date_istemara_hijry or '')
                worksheet.write(rows, 25, line.vehicle_color or '')
                worksheet.write(rows, 26, line.gcc_covering or '')
                worksheet.write(rows, 27, line.natural_peril_cover or '')
                worksheet.write(rows, 28, line.dob_owner or '')
                worksheet.write(rows, 29, line.nationality.name or '')

                rows += 1

            file_data = io.BytesIO()
            wb.save(file_data)
            attachment = self.env['ir.attachment'].create({
                'type': 'binary',
                'name': "Vehicle Information TO "+ str(company.name) + '.xls',
                'datas': encodebytes(file_data.getvalue()),
                'is_vehicle': True,
                'insurance_company_id': company._origin.id,
            })
            document = self.env['documents.document'].create({
                'name': attachment.name,
                'attachment_id': attachment.id,
                'type': 'empty',
                'folder_id': self.env.ref('insurance_management.documents_client_data_folder').id,
                'tag_ids': [(6, 0, [self.env.ref('insurance_management.documents_document_data_tag').id] or [])],
                'owner_id': self.env.user.id,
                'partner_id': company.ins_company_partner_id.id if company.ins_company_partner_id else False,
                'res_model': self._name,
                'res_id': self.id,
            })

            client_insurance_attachments += attachment

        return client_insurance_attachments



    def export_xlsx_report_client_template(self):
        if not self.insurance_type_id:
            raise ValidationError('For Exporting Template you have to select Insurance Type!')
        datas = {
            'wizard_data': self.read()
        }
        return self.env.ref('insurance_management.ins_client_report_export_template').report_action(self, data=datas)

    def submit_for_review(self):
        for rec in self:
            # rec.customer_attachment_ids.filtered(lambda b: b.name in rec.)
            name = rec.customer_attachment_ids.name.mapped('name')


            if any(rec.customer_attachment_ids.filtered(lambda b: b.is_required==True and not b.file)):
                raise ValidationError(_("Some Required Documents are Missing in Customer Attachments!, You have to Attached the following documents! %s", rec.customer_attachment_ids.filtered(lambda b: b.is_required==True and not b.file).name.mapped('name')))
            rec.state = 'review'

    def send_for_insurance_quotation(self):
        # attachments = self.quotation_file_create_insurance_company()
        # self.insurance_sent_attachment_ids = [(6,0,attachments.ids)]
        return {
            'name': "Send Insurance Email",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'insurance.email.wizard',
            'views': [(False, 'form')],
            'context': {'default_client_id': self.id},
            'target': 'new',
        }
    def open_select_quotation_wizard(self):
        return {
            'name': "Select Quotation Wizard",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'select.quotation.wizard',
            'views': [(False, 'form')],
            'context': {'default_client_id': self.id},
            'target': 'new',
        }

    def send_to_customer(self):
        return {
            'name': "Send Customer Email",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'customer.email.wizard',
            'views': [(False, 'form')],
            'context': {'default_client_id': self.id},
            'target': 'new',
        }


    def cancel(self):
        self.state = 'cancel'

class client_basic_info(models.Model):
    _name = 'client.basic.info'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'client_basic_info'

    member_id = fields.Char(string='Member ID',required=1)
    dependent_id = fields.Char(string='Dependent ID')
    name = fields.Char(string='Member Name (En)', tracking=True)
    client_image = fields.Binary(string='Client Image')
    arabic_name = fields.Char(string='Member Name (Ar)', tracking=True)
    gender = fields.Selection([('Male','Male'),('Female','Female')],string='Gender')
    dob = fields.Date(string='Birth Date')
    dob_hijra = fields.Char(string='Birth Date(Hijra)')
    age = fields.Float(string='Age',compute='get_member_age')
    member_type = fields.Many2one('member.type.standard',string='Member Type')
    class_no = fields.Many2one('class.name.standard',string='Class No')
    age_category = fields.Many2one('age.category.standard',string='Age Category')
    risk_no = fields.Char(string='Risk No')
    nationality = fields.Many2one('res.country', 'Nationality')
    staff_no = fields.Char(string='Staff No')
    # member_category = fields.Selection([('Manager','Manager'),('Staff','Staff'),('Skilled Worker','Skilled Worker'),('Supervisor','Supervisor')],string='Member Category')
    member_category = fields.Many2one('member.category', string='Member Category')
    mobile1 = fields.Char(string='Mobile No (1)')
    mobile2 = fields.Char(string='Mobile No (2)')
    dep_no = fields.Char(string='Dep Code')
    sponser_id = fields.Char(string='Sponser ID')
    occupation = fields.Many2one('ins.occupation',string='Occupation')
    # marital_status = fields.Selection([('Single','Single'),('Married','Married'),('Divorced','Divorced'),('Widowed','Widowed')],string='Relation')
    marital_status = fields.Many2one('member.relation', string='Relation')
    elm_relation = fields.Selection([('not_specified','Not Specified'),('son','Son'),('daughter','Daughter'),
                                     ('wife','Wife'),
                                     ('brother','Brother'),
                                     ('sister','Sister'),
                                     ('parent','Parent'),
                                     ('grand_parent','Grand Parent'),
                                     ('husband','Husband'),
                                     ('other','Other'),
                                     ('hoh','HOH')],string='ELM Relation')
    vip = fields.Selection([('yes','Yes'),('no','No')],string='VIP?')
    as_vip = fields.Selection([('yes','Yes'),('no','No')],string='AS VIP?')
    bank_id = fields.Many2one('res.bank', string='Bank')
    branch_id = fields.Many2one('client.branch',string='Branch ID')
    customer_id = fields.Many2one(related='branch_id.customer_id', store=True)
    document_no = fields.Char(related='branch_id.document_no', string='Document No',store=True)
    state = fields.Selection(related='branch_id.state', store=True)
    note = fields.Text(string='Note')

    def get_dob_hijra(self):
        for rec in self:
            # Convert a Hijri date to Gregorian
            # g = Hijri(1403, 2, 17).to_gregorian()
            if rec.dob:
                # Convert a Gregorian date to Hijri
                # h = Gregorian(1982, 12, 2).to_hijri()
                war_start = str(rec.dob)

                war = datetime.strptime(war_start, '%Y-%m-%d')
                hijridate = convert.Gregorian(war).to_hijri()
                rec.dob_hijra = hijridate or False
            else:
                rec.dob_hijra = False

    @api.depends('dob')
    def get_member_age(self):
        for rec in self:
            if rec.dob:
                born = rec.dob
                today = date.today()
                rec.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                rec.age = 0


class risk_location(models.Model):
    _name = 'risk.location'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'risk_location'

    code = fields.Char(string='Code', tracking=True)
    country = fields.Many2one('res.country', 'Country')
    region = fields.Char(string='Region', tracking=True)
    city = fields.Many2one('res.country.state',string='City',domain="[('country_id', '=?', country)]")
    risk = fields.Char(string='Risk')

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

class ins_occupation(models.Model):
    _name = 'ins.occupation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'mail.render.mixin']
    _description = 'ins_occupation'

    code = fields.Char(string='Occupation Code', tracking=True)
    name = fields.Char(string='Occupation Name', translate=True)
    gender = fields.Selection([('Male','Male'),('Female','Female')],string='Gender')


class Document(models.Model):
    _inherit = 'documents.document'


    @api.model
    def create(self, vals):
        if 'res_id' in vals:
            if not isinstance(vals['res_id'], int):
                source_ids = vals['res_id']
                x = source_ids.split(",")
                source_all = self.env[x[0]].search([])
                source_id = int(x[1])
                source = self.env[x[0]].search([('id','=',source_id)])
                if source:
                    vals['res_id'] = source.id
                    vals['res_model'] = source._name
        if 'uid' in self.env.context:
            vals['owner_id'] = self.env.context.get('uid')
        res = super(Document, self).create(vals)

        return res


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    client_branch_id = fields.Many2one('client.branch', string='Client Branch')

    def action_related_data_gathering(self):
        return {
            'name': "Customer Information",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'client.branch',
            'views': [(False, 'form')],
            'res_id': self.client_branch_id.id,
        }

class Task(models.Model):
    _inherit = "project.task"

    client_branch_id = fields.Many2one('client.branch', string='Client Branch')

    def action_related_data_gathering(self):
        return {
            'name': "Customer Information",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'client.branch',
            'views': [(False, 'form')],
            'res_id': self.client_branch_id.id,
        }
