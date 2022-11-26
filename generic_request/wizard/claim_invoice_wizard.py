import pdb

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID


class ClaimInvoiceWizard(models.TransientModel):
    _name = "claim.invoice.wizard"
    _description = "claim.invoice.wizard"


    claim_request_id = fields.Many2one('request.request',string='Claim')
    journal_id = fields.Many2one('account.journal', string="Journal",required=True)
    due_date = fields.Date(string='Due Date',required=True)

    def create_claim_invoice(self):
        for rec in self:
            invoice_lst = []
            invoice_lst.append((0, 0, {
                'product_id': '',
                'name': 'Claim',
                'quantity': 1,
                'price_unit': rec.claim_request_id.net_amount
            }))

            params = self.env['ir.config_parameter'].sudo()
            gov_rel_email = params.get_param('gov_rel_email', default='')
            account_move = self.env['account.move'].create({
                'partner_id': rec.claim_request_id.client_id.id,
                'policy_id': rec.claim_request_id.policy_id.id,
                'claim_request_id': rec.claim_request_id.id,
                'vehicle_detail_id': rec.claim_request_id.vehicle_detail_id,
                'claim_boolean': True,
                # 'invoice_date':due_date,
                'invoice_type': 'claim_inv',
                'journal_id': rec.journal_id.id,
                # 'invoice_payment_term_id': rec.claim_request_id.payment_term_id.id,
                'move_type': 'out_invoice',
                'policy_no': rec.claim_request_id.policy_no,
                'invoice_date_due': rec.due_date,
                'invoice_ref': rec.claim_request_id.id,
                'insurance_company_id': rec.claim_request_id.insurance_company_id.id

            })


            account_move.invoice_line_ids = invoice_lst

            if account_move:
                rec.claim_request_id.account_move_ids = [(4, account_move.id)]
                return {
                    'name': "Claim Invoice",
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'domain': [('id', '=', account_move.id)],
                }


