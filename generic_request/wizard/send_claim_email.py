import pdb

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID


class ClaimEmailWizard(models.TransientModel):
    _name = "claim.email.wizard"
    _description = "claim.email.wizard"

    # def _get_attachment(self):
    #     inventory_report_attachment = self.client_id.export_inventory_lines_records()
    #
    #     return [(6,0,inventory_report_attachment.ids)]

    def _get_template(self):
        template_id = self.env['ir.model.data']._xmlid_to_res_id(
            'insurance_claim_system.email_template_claim_request', raise_if_not_found=False)
        template_browse = self.env['mail.template'].browse(template_id)
        return template_browse.id

    client_id = fields.Many2one('client.branch',string='Client')
    insurance_company_id = fields.Many2one('insurance.company',string='Insurance Company',required=True)
    # claim_request_attachment_ids = fields.Many2many('ir.attachment',string='Claim Request Attachments')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'mail_claim_request_ir_attachments_rel',
        'claim_wizard_id', 'attachment_id', 'Attachments')
    template_id = fields.Many2one(
        'mail.template', 'Use template', index=True,default=_get_template)
    subject = fields.Char(string='Subject')
    cc = fields.Char(string='CC')
    body = fields.Html(string='Body')
    claim_request_id = fields.Many2one('request.request',string='Claim Request')

    @api.model
    def _insurance_company_email_send(self):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        ins_company = self.insurance_company_id
        claim_attachment = None

        # if self.claim_request_attachment_ids:
        #     claim_attachment = self.claim_request_attachment_ids
        if self.attachment_ids and claim_attachment != None:
            claim_attachment += self.attachment_ids
        elif self.attachment_ids and claim_attachment == None:
            claim_attachment = self.attachment_ids
        template_id = self.env['ir.model.data']._xmlid_to_res_id(
            'insurance_management.email_template_info_report_customer', raise_if_not_found=False)
        template_browse = self.env['mail.template'].browse(template_id)
        if template_browse:
            values = template_browse.generate_email(ins_company.id,
                                                    ['subject', 'body_html', 'email_from',
                                                     'email_to', 'partner_to', 'email_cc',
                                                     'reply_to', 'scheduled_date',
                                                     'attachment_ids'])
            # values['attachment_ids'].append((4, client_information_attachment.id))
            # attachment_ids = []
            # for attachment in client_information_attachment:
            #     attachment_ids.append(attachment.id)
            # for attachment in self.attachment_ids:
            #     attachment_ids.append(attachment.id)
            if claim_attachment != None:
                values['attachment_ids'] = claim_attachment.ids or False
            # values['email_from'] = su_id.email
            values['email_from'] = self.env.user.work_email
            values['email_to'] = ins_company.email
            values['res_id'] = False
            values['cc'] = self.cc or False
            values['subject'] = self.subject or str(ins_company.name) + str(
                fields.datetime.now()) + '' + "-" + '' + 'Claim Request'
            values['body_html'] = self.body
            values['author_id'] = self.env['res.users'].browse(
                self.env['res.users']._context['uid']).partner_id.id
            author = self.env['res.users'].browse(
                self.env['res.users']._context['uid']).partner_id.id
            if not values['email_to'] and not values['email_from']:
                pass
            msg_id = self.env['mail.mail'].create({
                'email_to': values['email_to'],
                'auto_delete': True,
                'email_from': values['email_from'],
                'subject': values['subject'],
                'body_html': values['body_html'],
                'attachment_ids': values['attachment_ids'],
                'model': self.claim_request_id._name or False,
                'res_id': self.claim_request_id.id or False,
                'email_cc': values['cc'],
                'author_id': values['author_id']})
            mail_mail_obj = self.env['mail.mail']
            if msg_id:
                mail_mail_obj.sudo().send(msg_id)
        # inventory_report_attachment.unlink()
        return True


    def action_confirm(self):
        active_id = self._context.get('active_id', False)
        self._insurance_company_email_send()
        stage = self.env['request.stage'].search([('name','=','Sent To Insurance Company'),('request_type_id','=',self.claim_request_id.type_id.id)],limit=1)
        if stage:
            self.claim_request_id.stage_id = stage.id
        else:
            stage = self.env['request.stage'].create({
                'name': _('Sent To Insurance Company'),
                'code': 'Sent-To-Insurance-Company',
                'request_type_id': self.claim_request_id.type_id.id,
                'sequence': 10,
                'closed': False,
                'type_id': self.env.ref(
                    'generic_request.request_stage_send_to_insurance_company').id,
            })
            # stage = self.env['request.stage'].create(
            #     {'name', '=', 'Insurance Company Response Waiting',
            #      'code', '=', 'Insurance-Company-Response-Waiting',
            #      'request_type_id', '=', self.claim_request_id.type_id.id
            #      })
            self.claim_request_id.stage_id = stage.id


