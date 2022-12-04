import pdb

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID


class InsuranceEmailWizard(models.TransientModel):
    _name = "insurance.email.wizard"
    _description = "insurance.email.wizard"

    # def _get_attachment(self):
    #     inventory_report_attachment = self.client_id.quotation_file_create_insurance_company()
    #
    #     return [(6,0,inventory_report_attachment.ids)]

    def _get_template(self):
        template_id = self.env['ir.model.data']._xmlid_to_res_id(
            'insurance_management.email_template_info_report_customer', raise_if_not_found=False)
        template_browse = self.env['mail.template'].browse(template_id)
        return template_browse.id

    client_id = fields.Many2one('client.branch',string='Client')
    insurance_companies_ids = fields.Many2many('insurance.company',string='Insurance Companies',required=True)
    client_info_attachment_ids = fields.Many2many('ir.attachment',string='Client Info Attachments',domain="[('res_id','=',client_id),('res_model','=','qqqq')]")
    attachment_ids = fields.Many2many(
        'ir.attachment', 'mail_insurance_message_ir_attachments_rel',
        'ins_wizard_id', 'attachment_id', 'Attachments')
    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True,default=_get_template)
    subject = fields.Char(string='Subject')
    cc = fields.Char(string='CC')
    body = fields.Html(string='Body')
    @api.onchange('insurance_companies_ids')
    def generate_client_info_attachment(self):
        insurance_member_attachments = self.env['ir.attachment']
        for ins_company in self.insurance_companies_ids:
            client_information_attachment = self.client_id.quotation_file_create_insurance_company(company=ins_company)
            if client_information_attachment:
                insurance_member_attachments += client_information_attachment
        self.client_info_attachment_ids = insurance_member_attachments.ids

    @api.model
    def _insurance_company_email_send(self):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)

        for ins_company in self.insurance_companies_ids:
            insurance_member_attachments = self.env['ir.attachment']

            template_id = self.env['ir.model.data']._xmlid_to_res_id(
                'insurance_management.email_template_info_report_customer', raise_if_not_found=False)
            template_browse = self.env['mail.template'].browse(template_id)
            if template_browse:
                values = template_browse.generate_email(self.client_id.id,
                                                        ['subject', 'body_html', 'email_from',
                                                         'email_to', 'partner_to', 'email_cc',
                                                         'reply_to', 'scheduled_date',
                                                         'attachment_ids'])
                if any(self.client_info_attachment_ids.filtered(lambda b: b.insurance_company_id.id == ins_company.id)):
                    for client_attachment in self.client_info_attachment_ids.filtered(lambda b: b.insurance_company_id.id == ins_company.id):
                        insurance_member_attachments += client_attachment

                for attachment in self.attachment_ids:
                    insurance_member_attachments += attachment
                values['attachment_ids'] = insurance_member_attachments.ids or False
                # values['email_from'] = su_id.email
                values['email_from'] = 'apps@lsclogistics.com'
                values['email_to'] = ins_company.email
                values['res_id'] = False
                values['subject'] = self.subject +'   '+'   ' +str(ins_company.name) + str(
                    fields.datetime.now()) + '' + "-" + '' + 'Client Information Report'
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
        for line in insurance_member_attachments:
            self.client_id.insurance_sent_attachment_ids = [(4, line.id)]
        return True


    def action_confirm(self):
        active_id = self._context.get('active_id', False)
        self._insurance_company_email_send()
        self.client_id.state = 'sent_to_insurance'


