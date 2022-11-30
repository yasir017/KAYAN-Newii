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

class CustomerEmailWizard(models.TransientModel):
    _name = "customer.email.wizard"
    _description = "customer.email.wizard"

    # def _get_attachment(self):
    #     inventory_report_attachment = self.client_id.quotation_file_create_insurance_company()
    #
    #     return [(6,0,inventory_report_attachment.ids)]

    def _get_template(self):
        template_id = self.env['ir.model.data']._xmlid_to_res_id(
            'insurance_management.email_template_quotation_report_to', raise_if_not_found=False)
        template_browse = self.env['mail.template'].browse(template_id)
        return template_browse.id

    client_id = fields.Many2one('client.branch',string='Client')
    medical_visibility_check = fields.Boolean(related='client_id.medical_visibility_check',string='Medical Visibility Check',
                                              compute='get_insurance_pages_visibility')
    vehicle_visibility_check = fields.Boolean(related='client_id.vehicle_visibility_check',string='Vehicle Visibility Check',
                                              compute='get_insurance_pages_visibility')
    insurance_quotation_ids = fields.Many2many('insurance.quotation',string='Insurance Quotation',domain="[('client_branch_id','=',client_id)]")
    vehicle_quotation_ids = fields.Many2many('vehicle.quotation',string='Vehicle Quotation',domain="[('client_branch_id','=',client_id)]")
    client_info_attachment_ids = fields.Many2many('ir.attachment',string='Client Info Attachments')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'mail_client_message_ir_attachments_rel',
        'ins_wizard_id', 'attachment_id', 'Attachments')
    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True,default=_get_template)
    subject = fields.Char(string='Subject')
    cc = fields.Char(string='CC')
    body = fields.Html(string='Body')

    @api.model
    def _insurance_company_email_send(self):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        customer_all_attachments = self.env['ir.attachment']
        # for ins_quotation in self.insurance_quotation_ids:
        # if self.medical_visibility_check == True:
        #     client_quotatons_send_attachment = self.make_send_quotations(ins_quotations=self.insurance_quotation_ids)
        # if self.vehicle_visibility_check == True:
        #     client_quotatons_send_attachment = self.make_send_quotations(ins_quotations=self.vehicle_quotation_ids)
        # if client_quotatons_send_attachment:
        #     customer_all_attachments += client_quotatons_send_attachment
        # else:
        #     client_information_attachment = self.client_id.insurance_sent_attachment_ids
        template_id = self.env['ir.model.data']._xmlid_to_res_id(
            'insurance_management.email_template_info_report_customer', raise_if_not_found=False)
        template_browse = self.env['mail.template'].browse(template_id)
        if template_browse:
            values = template_browse.generate_email(self.client_id.id,
                                                    ['subject', 'body_html', 'email_from',
                                                     'email_to', 'partner_to', 'email_cc',
                                                     'reply_to', 'scheduled_date',
                                                     'attachment_ids'])
            for attachment in self.attachment_ids:
                customer_all_attachments += attachment

            values['attachment_ids'] = customer_all_attachments.ids or False
            # values['email_from'] = su_id.email
            values['email_from'] = 'apps@lsclogistics.com'
            values['email_to'] = self.client_id.customer_id.email
            values['res_id'] = False
            values['subject'] = self.subject +'   '+'   ' +str(self.client_id.customer_id.name) + str(
                fields.datetime.now()) + '' + "-" + '' + 'Insurance Quotations'
            values['cc'] = self.cc or False
            # add_date = self.body + str(fields.date.today())
            # pdb.set_trace()
            values['body_html'] = self.body
            # values['body_html'] = values['body_html'],
            values['author_id'] = self.env['res.users'].browse(
                self.env['res.users']._context['uid']).partner_id.id
            author = self.env['res.users'].browse(
                self.env['res.users']._context['uid']).partner_id.id
            if not values['email_to'] and not values['email_from']:
                pass
            msg_id = self.env['mail.mail'].create({
                'email_to': values['email_to'],
                'auto_delete': False,
                'email_from': values['email_from'],
                'subject': values['subject'],
                'email_cc': values['cc'],
                'body_html': values['body_html'],
                'message_type': 'comment',
                'model': self.client_id._name or False,
                'res_id': self.client_id.id or False,
                'attachment_ids': values['attachment_ids'],
                'author_id': values['author_id']})
            mail_mail_obj = self.env['mail.mail']
            if msg_id:
                mail_mail_obj.sudo().send(msg_id)
    # for line in insurance_member_attachments:
    #     self.client_id.insurance_sent_attachment_ids = [(4, line.id)]
        return True


    def action_confirm(self):
        active_id = self._context.get('active_id', False)
        self._insurance_company_email_send()
        self.client_id.state = 'sent_to_customer'


    def make_send_quotations(self,ins_quotations):
        client_insurance_attachments = self.env['ir.attachment']
        if self.client_id.insurance_type_id.ins_type_select == 'is_medical':
            style = xlwt.easyxf('font:bold True;borders:left thin, right thin, top thin, bottom thin;')
            # style1 = xlwt.easyxf(num_format_str='MM/DD/YYYY HH:MM:SS')

            wb = xlwt.Workbook()
            for quotation in ins_quotations:
                worksheet = wb.add_sheet(quotation.insurance_company_id.name)
                worksheet.write(0, 0, 'Customer Quotation', style)
                worksheet.write(0, 1, self.client_id.customer_id.name)
                worksheet.write(0, 2, 'Company Name.', style)
                worksheet.write(0, 3, quotation.insurance_company_id.name)
                # worksheet.write(2, 0, 'Customer', style)
                # worksheet.write(2, 1, partner.name or '', style)

                worksheet.write(3, 0, 'Date Time', style)
                worksheet.write(3, 1, str(fields.datetime.now()) or '', style)

                worksheet.write(1, 4, 'Total Premium', style)
                worksheet.write(1, 5, quotation.total_rate or '', style)
                worksheet.write(2, 4, 'Total Premium(*VAT)', style)
                worksheet.write(2, 5, quotation.amount or '', style)

                i = 1

                for i in range(0, 80):
                    worksheet.col(i).width = int(20 * 260)

                rows = 5

                worksheet.write(rows, 0, 'Client DB ID(for technical use)', style)
                worksheet.write(rows, 1, 'Member ID', style)
                worksheet.write(rows, 2, 'Dependent ID', style)
                worksheet.write(rows, 3, 'Member Name (English)', style)
                worksheet.write(rows, 4, 'Member Name (Arabic)', style)
                worksheet.write(rows, 5, 'Gregorian Birth Date', style)
                worksheet.write(rows, 6, 'Age', style)
                worksheet.write(rows, 7, 'Hajrah Birth Date', style)
                worksheet.write(rows, 8, 'Member type', style)
                worksheet.write(rows, 9, 'Gender', style)
                worksheet.write(rows, 10, 'Class no', style)
                worksheet.write(rows, 11, 'Risk No.', style)
                worksheet.write(rows, 12, 'Nationality', style)
                worksheet.write(rows, 13, 'Staff No.', style)
                worksheet.write(rows, 14, 'Member Category', style)
                worksheet.write(rows, 15, 'Mobile No. (1)', style)
                worksheet.write(rows, 16, 'Mobile No. (2)', style)
                worksheet.write(rows, 17, 'Dep Code', style)
                worksheet.write(rows, 18, 'Sponser ID', style)
                worksheet.write(rows, 19, 'Occupation', style)
                worksheet.write(rows, 20, 'Marital status(Saudi EMP &Boarder no(Employee,Dependent)', style)
                worksheet.write(rows, 21, 'VAT', style)
                worksheet.write(rows, 22, 'Premium', style)
                rows += 1

                for line in quotation.quotation_line_ids:
                    # company_member_type_standard = ''
                    # if line.member_type:
                    #     company_member_type_standard = self.env['company.member.type.standard'].search([('member_type_standard_id', '=', line.member_type.id),('insurance_company_id','=',company.id)], limit=1).name or ''
                    # company_class_standard = ''
                    # if line.class_no:
                    #     company_class_standard = self.env['company.class.standard'].search([('class_standard_id', '=', line.class_no.id),('insurance_company_id','=',company.id)], limit=1).name or ''
                    worksheet.write(rows, 0, line.id or '')
                    worksheet.write(rows, 1, line.member_id or '')
                    worksheet.write(rows, 2, line.dependent_id or '')
                    worksheet.write(rows, 3, line.name or '')
                    worksheet.write(rows, 4, line.arabic_name or '')
                    worksheet.write(rows, 5, line.dob or '')
                    worksheet.write(rows, 6, line.age or '')
                    worksheet.write(rows, 7, line.dob_hijra or '')
                    worksheet.write(rows, 8, line.member_type.name or '')
                    worksheet.write(rows, 9, line.gender or '')
                    worksheet.write(rows, 10, line.class_no.name or '')
                    worksheet.write(rows, 11, str(line.risk_no) or '')
                    worksheet.write(rows, 12, line.nationality.name or '')
                    worksheet.write(rows, 13, line.staff_no or '')
                    worksheet.write(rows, 14, line.member_category or '')
                    worksheet.write(rows, 15, line.mobile1 or '')
                    worksheet.write(rows, 16, line.mobile2 or '')
                    worksheet.write(rows, 17, line.dep_no or '')
                    worksheet.write(rows, 18, line.sponser_id or '')
                    worksheet.write(rows, 19, line.occupation.name or '')
                    # worksheet.write(rows, 20, line.marital_status or '')
                    worksheet.write(rows, 21, line.vat)
                    worksheet.write(rows, 22, line.rate)

                    rows += 1
                benefits_worksheet = wb.add_sheet(quotation.insurance_company_id.name+' Benefits')
                benefits_worksheet.write(0, 1, 'Company Name.', style)
                benefits_worksheet.write(0, 2, quotation.insurance_company_id.name)
                i = 1

                for i in range(0, 80):
                    worksheet.col(i).width = int(20 * 260)

                rows = 3

                benefits_worksheet.write(rows, 0, 'Category Type', style)
                benefits_worksheet.write(rows, 1, 'Benefit', style)
                benefits_worksheet.write(rows, 2, 'Included?', style)
                benefits_worksheet.write(rows, 3, 'Vary?', style)
                benefits_worksheet.write(rows, 4, 'From Value', style)
                benefits_worksheet.write(rows, 5, 'To Value', style)
                benefits_worksheet.write(rows, 6, 'Value', style)
                rows += 1

                for line in quotation.custom_benefits_ids:
                    benefits_worksheet.write(rows, 0, line.category_type or '')
                    benefits_worksheet.write(rows, 1, line.benefit_id.name or '')
                    benefits_worksheet.write(rows, 2, line.included or '')
                    benefits_worksheet.write(rows, 3, line.vary or '')
                    benefits_worksheet.write(rows, 4, line.from_value or '')
                    benefits_worksheet.write(rows, 5, line.to_value or '')
                    benefits_worksheet.write(rows, 6, line.benefit_value or '')
                    rows += 1

            file_data = io.BytesIO()
            wb.save(file_data)
            attachment = self.env['ir.attachment'].create({
                'type': 'binary',
                'name': "Insurance Quotations To "+str(self.client_id.customer_id.name)+ str(self.id) + '.xls',
                'datas': encodebytes(file_data.getvalue()),
                'is_medical': True,
                'description': self.client_id.customer_id.name + "sent quotations to customer",
            })
            document = self.env['documents.document'].create({
                'name': attachment.name,
                'attachment_id': attachment.id,
                'description': attachment.description,
                'type': 'empty',
                'folder_id': self.env.ref('insurance_management.documents_client_data_folder').id,
                'tag_ids': [(6, 0, [self.env.ref('insurance_management.documents_document_data_tag').id] or [])],
                'owner_id': self.env.user.id,
                'partner_id': self.client_id.id if self.client_id else False,
                'res_model': self.client_id._name,
                'res_id': self.client_id.id,
            })

            client_insurance_attachments += attachment
        if self.client_id.insurance_type_id.ins_type_select == 'is_vehicle':
            style = xlwt.easyxf('font:bold True;borders:left thin, right thin, top thin, bottom thin;')
            # style1 = xlwt.easyxf(num_format_str='MM/DD/YYYY HH:MM:SS')
            wb = xlwt.Workbook()
            for quotation in ins_quotations:
                worksheet = wb.add_sheet(quotation.insurance_company_id.name)
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

                for line in quotation.vehicle_quotation_line_ids:
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
                    worksheet.write(rows, 30, line.vat or '')
                    worksheet.write(rows, 31, line.rate or '')

                    rows += 1

                benefits_worksheet = wb.add_sheet(quotation.insurance_company_id.name + ' Benefits')
                benefits_worksheet.write(0, 1, 'Company Name.', style)
                benefits_worksheet.write(0, 2, quotation.insurance_company_id.name)
                i = 1

                for i in range(0, 80):
                    worksheet.col(i).width = int(20 * 260)

                rows = 3

                benefits_worksheet.write(rows, 0, 'Category Type', style)
                benefits_worksheet.write(rows, 1, 'Benefit', style)
                benefits_worksheet.write(rows, 2, 'Included?', style)
                benefits_worksheet.write(rows, 3, 'Vary?', style)
                benefits_worksheet.write(rows, 4, 'From Value', style)
                benefits_worksheet.write(rows, 5, 'To Value', style)
                benefits_worksheet.write(rows, 6, 'Value', style)
                rows += 1

                for line in quotation.vehicle_custom_benefits_ids:
                    benefits_worksheet.write(rows, 0, line.category_type or '')
                    benefits_worksheet.write(rows, 1, line.benefit_id.name or '')
                    benefits_worksheet.write(rows, 2, line.included or '')
                    benefits_worksheet.write(rows, 3, line.vary or '')
                    benefits_worksheet.write(rows, 4, line.from_value or '')
                    benefits_worksheet.write(rows, 5, line.to_value or '')
                    benefits_worksheet.write(rows, 6, line.benefit_value or '')

                    rows += 1

            file_data = io.BytesIO()
            wb.save(file_data)
            attachment = self.env['ir.attachment'].create({
                'type': 'binary',
                'name': "Vehicle Quotations"+ str(self.id) + '.xls',
                'datas': encodebytes(file_data.getvalue()),
                'is_vehicle': True,
            })
            document = self.env['documents.document'].create({
                'name': attachment.name,
                'attachment_id': attachment.id,
                'description': attachment.description,
                'type': 'empty',
                'folder_id': self.env.ref('insurance_management.documents_client_data_folder').id,
                'tag_ids': [(6, 0, [self.env.ref('insurance_management.documents_document_data_tag').id] or [])],
                'owner_id': self.env.user.id,
                'partner_id': self.client_id.id if self.client_id else False,
                'res_model': self.client_id._name,
                'res_id': self.client_id.id,
            })

            client_insurance_attachments += attachment

        return client_insurance_attachments


