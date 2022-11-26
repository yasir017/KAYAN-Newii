from odoo import models, fields, exceptions, api, _
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
class AccountMove(models.Model):
    _inherit = 'account.move'

    insurance_company_id = fields.Many2one('insurance.company', "Insurance Company")
    endorsment_ref = fields.Char("Endorsement Ref")
    commission_count = fields.Integer("commission",compute='_count_commission',store=True)
    govt_fee_count = fields.Integer("Govt. Fee", compute='_count_govt_fee',store=True)
    invoice_ref = fields.Many2one('account.move',string="Invoice Ref")
    govt_boolean = fields.Boolean("Govt Bill")
    commission_boolean = fields.Boolean('Commission Invoice')

    def _count_commission(self):
        for rec in self:
            account_move = self.env['account.move'].search([('invoice_ref','=',self.id),('move_type','=','out_invoice')])
            if account_move:
                rec.commission_count=len(account_move)

    def _count_commission(self):
        for rec in self:
            account_move = self.env['account.move'].search([('invoice_ref','=',self.id),('move_type','=','in_invoice')])
            if account_move:
                rec.govt_fee_count=len(account_move)

    def acton_calculate_commission(self):
        # account_move = self.env['account.move']

        if self.invoice_type=='policy':
            if self.policy_id:
                if self.invoice_payment_term_id:
                    params = self.env['ir.config_parameter'].sudo()
                    value= sum(self.line_ids.mapped('price_subtotal'))
                    sign = value < 0 and -1 or 1
                    percentage = params.get_param('insurance_management.percentage')
                    print(percentage)
                    if not percentage:
                        raise ValidationError("Govt percentage must be greater then 0")
                    invoice_id = []
                    currency = self.env.company.currency_id
                    balance=0.0
                    for line in self.invoice_payment_term_id.line_ids:
                        next_date = fields.Date.from_string(self.invoice_date)
                        if line.option == 'day_after_invoice_date':
                            next_date += relativedelta(days=line.days)
                            if line.day_of_the_month > 0:
                                months_delta = (line.day_of_the_month < next_date.day) and 1 or 0
                                next_date += relativedelta(day=line.day_of_the_month, months=months_delta)
                        elif line.option == 'after_invoice_month':
                            next_first_date = next_date + relativedelta(day=1, months=1)  # Getting 1st of next month
                            next_date = next_first_date + relativedelta(days=line.days - 1)
                        elif line.option == 'day_following_month':
                            next_date += relativedelta(day=line.days, months=1)
                        elif line.option == 'day_current_month':
                            next_date += relativedelta(day=line.days, months=0)

                        already_created = self.env['account.move'].search([('invoice_ref','=',self.id),('move_type','=','out_invoice'),('invoice_date','=',next_date)])
                        if line.value!='balance':
                            balance+=line.value_amount
                        print(next_date)
                        if not already_created:
                            if line.value=='balance':
                                amount=value-balance
                                commission_am = amount * (self.policy_id.approve_percentage / 100.0)

                                self.create_invoice_commsion(commission_am, next_date)
                                self.create_govt_fee(next_date, commission_am * (int(percentage) / 100.0))
                            elif line.value == 'percent':
                                amount = value*(line.value_amount/100.0)
                                commission_am = amount * (self.policy_id.approve_percentage / 100.0)

                                self.create_invoice_commsion(commission_am, next_date)
                                self.create_govt_fee(next_date, commission_am * (int(percentage) / 100.0))
                            else:

                                commission_am = line.value_amount*(self.policy_id.approve_percentage/100.0)
                                self.create_invoice_commsion(commission_am,next_date)
                                self.create_govt_fee(next_date,commission_am*(int(percentage)/100.0))

    def open_comssion_invoice(self,lst):
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.policy',
            'view_mode': 'tree,form',
            'res_id':lst,
            'domain': [('invoice_ref', '=', self.id)],
        }
    def create_invoice_commsion(self,amount,due_date):
        invoice_lst=[]
        invoice_lst.append((0, 0, {
            'product_id': '',
            'name': 'commission',
            'quantity': 1,
            'price_unit': amount

        }))

        params = self.env['ir.config_parameter'].sudo()
        gov_rel_email = params.get_param('gov_rel_email', default='')
        account_move = self.env['account.move'].create({
            'partner_id': self.partner_id.id,
            'policy_id': self.policy_id.id,
            'invoice_date':due_date,
            'invoice_type':'commission_inv',
            'journal_id': self.journal_id.id,
            # 'invoice_payment_term_id': self.payment_term_id.id,
            'move_type': 'out_invoice',
            'policy_no': self.policy_no,
            'invoice_date_due':due_date,
            'invoice_ref':self.id,
            'insurance_company_id': self.insurance_company_id.id

        })
        self.commission_boolean = True

        account_move.invoice_line_ids = invoice_lst
    def create_govt_fee(self,due_date,amount):
        invoice_lst = []
        self.govt_boolean = True
        params = self.env['ir.config_parameter'].sudo()
        govt_partnr = params.get_param('insurance_management.govt_partner',)
        print(govt_partnr)
        percentage = params.get_param('insurance_management.percentage', default='')
        journal_id = params.get_param('insurance_management.govt_bill_journal', default='')
        if not govt_partnr:
            raise ValidationError("Please Select Govt Partner in setting")
        if int(percentage)<=0:
            raise ValidationError("Govt percentage must be greater then 0")
        if not journal_id:
            raise  ValidationError("Please Select Journal For Govt. Fee in Setting")
        invoice_lst.append((0, 0, {
            'product_id': '',
            'name': 'govt. Fee',
            'quantity': 1,
            'price_unit': amount

        }))


        account_move = self.env['account.move'].create({
            'partner_id': int(govt_partnr),
            'policy_id': self.policy_id.id,
            'invoice_date': due_date,
            'invoice_type': 'commission_inv',
            'journal_id': int(journal_id),
            # 'invoice_payment_term_id': self.payment_term_id.id,
            'move_type': 'in_invoice',
            'date':due_date,
            'policy_no': self.policy_no,
            'invoice_date_due': due_date,
            'invoice_ref': self.id,
            'insurance_company_id': self.insurance_company_id.id

        })
        account_move.invoice_line_ids = invoice_lst


    def action_open_invoice(self):
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'context': {
                'default_policy_id': self.policy_id.id,
                'default_invoice_ref': self.id,
                'default_move_type': 'out_invoice',
                'default_commission_boolean': True

            },
            'domain': [('move_type','=','out_invoice'),('invoice_ref', '=', self.id)],
        }

    def action_open_govt_fee(self):
            return {
                'name': 'Bills',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'context': {
                    'default_policy_id': self.policy_id.id,
                    'default_invoice_ref':self.id,
                    'default_move_type':'in_invoice',
                    'default_govt_boolean':True

                },
                'domain': [('move_type', '=', 'in_invoice'),('invoice_ref', '=', self.id)],
            }