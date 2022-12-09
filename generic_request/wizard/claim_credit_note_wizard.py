import pdb

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import except_orm
from odoo.exceptions import UserError
from odoo import SUPERUSER_ID


class ClaimCreditNoteWizard(models.TransientModel):
    _name = "claim.credit.note.wizard"
    _description = "claim.credit.note.wizard"


    claim_request_id = fields.Many2one('request.request',string='Claim')
    journal_id = fields.Many2one('account.journal', string="Journal",required=True)
    due_date = fields.Date(string='Due Date',required=True)

    def create_claim_credit_note(self):
        for rec in self:
            invoice_lst = []
            if rec.claim_request_id.approved_claim_type == 'repair':
                net_amount = rec.claim_request_id.net_amount_repair
            elif rec.claim_request_id.approved_claim_type == 'total_lost':
                net_amount = rec.claim_request_id.net_amount
            else:
                net_amount = 0
            invoice_lst.append((0, 0, {
                'product_id': '',
                'name': 'Claim Credit-Note Line',
                'quantity': 1,
                # 'predict_from_name': False,
                'price_unit': net_amount
            }))
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
                'move_type': 'out_refund',
                'policy_no': rec.claim_request_id.policy_no,
                'invoice_date_due': rec.due_date,
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


