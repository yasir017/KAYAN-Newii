# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import timedelta
from collections import namedtuple
from calendar import monthrange
from datetime import datetime

import calendar

class Policy(models.Model):
    _name = 'insurance.policy'

    _rec_name = 'policy_id_i'

    _inherit = ['mail.thread', 'mail.activity.mixin']
    partner_id = fields.Many2one('res.partner',string='Customer')
    policy_no = fields.Char("Policy No",)
    branch_id = fields.Many2one('insurance.branch',"Branch Name")
    start_date = fields.Date('Start Date')
    expiry_date = fields.Date('Expiry Date')
    issuance_date = fields.Date('Issuance Date')
    policy_id_i = fields.Char('policy ID',readonly=1)
    prev_policy = fields.Many2one('insurance.policy',"Policy")
    insurance_company_id = fields.Char('Insurance Company')
    business_class = fields.Many2one('business.class.config','Business Class')

    currency_id = fields.Many2one('res.currency','Currency')
    sum_insured = fields.Float('Sum Insured')
    basic_prem = fields.Float('Premium')
    net_premium = fields.Float('Net Premium')
    net_pr_percentage = fields.Float('Net Premium Percentage')
    basic_amount = fields.Float('Basic Amount')
    basic_amount_percentage = fields.Float("Basic Amount Percentage")
    gross_return = fields.Float('Gross Return')
    net_return_amount = fields.Float('Net Return')
    issuening_fee = fields.Float('Issuing Fee')
    gross_premium = fields.Float('Gross Premium')
    calculated_gross = fields.Float('Calculated Gross')
    premium_due = fields.Float('Premium Due')
    return_end_no = fields.Float('Return End No')

    is_renewel_policy  = fields.Boolean('Is Renewal Policy')
    is_extra_benfit = fields.Boolean('Is Extra Benefit')
    is_under_agreement = fields.Boolean('Is Under Agreement')
    agreement_file = fields.Binary("Agreement File")

    terms=fields.Selection([('long_term','Long Term'),('short_term','Short Term')],string="Terms",default='long_term')
    net_prem_percent = fields.Float()
    basic_percent = fields.Float()
    benefits_ids = fields.One2many('insurance.benefit.line','policy_id',string="Benefits Line")

    installment_ids = fields.One2many('insurance.installment','policy_id',string="Installment")
    paid = fields.Float('Paid Amount')
    # bussines_class_id = fields.Many2one('insurance.business.class',"Go Business Class")
    vehicle_detail = fields.One2many('insurance.vehicle','policy_id',"Vehicle detail")
    endors_vehicle_ids = fields.Many2many('insurance.vehicle',string="Endorsement Vehicle Detail")
    producer_ids = fields.One2many('insurance.producer','policy_id','Producer')
    marine_ids = fields.One2many('insurance.marine','policy_id',"Marine Details")
    health_ids = fields.One2many('insurance.health','policy_id','Health Detail')
    health_endors_ids = fields.Many2many('insurance.employee.data', string='Health Detail')
    # ******************scheduled Policy****************
    vat_premium = fields.Float('Vat Premium',default=15.0)
    total_premium_after_vat = fields.Float("Total After Vat",store=1,compute='compute_total_prem')

    premium_percent_am = fields.Float("Premium Percent")
    premium_percent_vat = fields.Float("Premium Percent Vat",default=15.0)
    premium_percent_am_total_ii= fields.Float("Premium Percent total")

    issuening_fee_percent = fields.Float("Issueing Fee Percent",default=15.0)
    issuening_fee_total = fields.Float("Issuenc Fee total")

    additional_fee_am = fields.Float("Add Fee amount")
    additional_fee_am_vat = fields.Float("Additional Fee Vat",default=15.0)
    additional_fee_am_total = fields.Float("Additional Fee Total")

    ded_fee_am = fields.Float("Ded Amount")
    ded_fee_am_vat = fields.Float("Ded Fee vat",default=15.0)
    ded_fee_am_total = fields.Float("Ded Fee total")

    total_policy_am = fields.Float("Total Policy",readonly=1)
    total_policy_vat = fields.Float("Total Policy Vat",compute='_total_vat',store=True)
    total_policy_am_after_vat=  fields.Float("Total Policy after Vat")

    move_ids = fields.One2many('account.move','policy_id',string="Invoices")
    journal_id = fields.Many2one('account.journal',string="Journal ")
    payment_term_id = fields.Many2one('account.payment.term',"Payment Term")
    policy_type = fields.Selection([('policy','Inception'),('endors','Endorsement')],default='policy',string="Transaction Type")
    endorsment_ref = fields.Char("Endorsement Ref")
    total_instalment_am = fields.Float('Total Installment after vat',compute='compute_installment')
    difference_instalment = fields.Float('Difference',compute='compute_installment')
    total_document_number = fields.Integer(string='Total Documents', compute='get_total_documents')

    def action_open_task(self):
        return {
            'name': "Task",
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'project.task',
            # 'views': [(False, 'form')],
            'context': {
                'default_policy_id': self.id,
                'default_partner_id': self.partner_id.id,
            },
            'domain': [('policy_id', '=', self.id)],
        }

    def default_coutry(self):
        country_id = self.env['res.country'].search([('code', '=', 'SA')])
        print(country_id)
        return country_id
    country_id = fields.Many2one('res.country',"Country",default=default_coutry)
    fed_state_id = fields.Many2one('res.country.state',"Branch ID",domain="[('country_id','=',192)]")

    govt_fee = fields.Float("Govt Feet", store=True, compute='_compute_govt_fee')
    sales_employee = fields.Many2one('hr.employee', string='Sales Employee')
    supervisor = fields.Many2one('hr.employee', string='Supervisor')

    total_employee_am = fields.Float("Premium Before Vat",compute='compute_health_total',store=1)
    employee_tax = fields.Float("Total Tax",compute='compute_health_total',store=1)
    employe_total_after_tax = fields.Float("Total After Tax",compute='compute_health_total',store=1)

    @api.depends('employee_ids')
    def compute_health_total(self):

        total_befor_tax = 0.0
        total_tax = 0.0
        total_after_tax = 0.0
        for rec in self:
            for emp in rec.employee_ids:
                total_befor_tax+=emp.rate
                total_after_tax+=emp.total
            rec.total_employee_am = total_befor_tax
            rec.employe_total_after_tax = total_after_tax
            rec.employee_tax = abs(total_after_tax-total_befor_tax)


    @api.onchange('premium_percent_am','premium_percent_vat')
    def _onchange_prem_percent_vat(self):
        if self.premium_percent_vat:
            print("Yasirrrrrrrrrrrrr")
            percentage = self.premium_percent_vat/100
            total_after_percentage = self.premium_percent_am*percentage
            total_am = self.premium_percent_am+total_after_percentage
            self.premium_percent_am_total_ii=total_am
        else:
            self.premium_percent_am_total_ii = self.premium_percent_am
    @api.depends('broker_commision')
    def _compute_govt_fee(self):
        for rec in self:
            if rec.broker_commision:
                params = self.env['ir.config_parameter'].sudo()

                percentage = params.get_param('insurance_management.percentage')
                if percentage:
                    rec.govt_fee = rec.broker_commision * (int(percentage) / 100)

    def action_open_policy_documents(self):
        return {
            'name': _('Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'documents.document',
            'view_mode': 'kanban',
            'context': {
                'default_res_id': self.id,
                'default_res_model': self._name,
                'default_folder_id': self.env.ref('policy_entry_insurance.documents_policy_data_folder').id,
                'default_tag_ids': [
                    (6, 0, [self.env.ref('policy_entry_insurance.documents_document_policy_data_tag').id] or [])],
            },
            'domain': [('res_id', '=', self.id), ('res_model', '=', self._name)],
        }
    def get_total_documents(self):
        for rec in self:
            rec.total_document_number = len(self.env['documents.document'].search([('res_id', '=', self.id),('res_model', '=', self._name)]))

    @api.depends('installment_ids','total_policy_am_after_vat')
    def compute_installment(self):
        instalment_am = 0.0
        for rec in self:
            if rec.installment_ids:
                for amount in rec.installment_ids:
                    if amount.type_installement=='fixed':
                        instalment_am+=amount.fix_amount
                    elif amount.type_installement=='percentage':
                        instalment_am+=amount.amount_paid
                rec.total_instalment_am=instalment_am
            rec.difference_instalment=rec.total_policy_am_after_vat-rec.total_instalment_am

    @api.constrains('start_date','expiry_date','issuance_date')
    def constrainst_date(self):
        for rec in self:
            if rec.expiry_date<rec.start_date:
                raise  ValidationError("Expiry Date should be greater then start date")
            # elif rec.issuance_date<rec.expiry_date:
            #     raise ValidationError("Issuence date should be greater then start date")
            # elif rec.expiry_date<rec.issuance_date
     # def action_create_invoice(self):
    #     invoice_lst = []
    #     product_id = self.env['product.product'].search([('insurance_product','=',True)],limit=1)
    #     invoice_lst.append((0,0,{
    #         'product_id':product_id.id,
    #         'name':product_id.name,
    #         'quantity':1,
    #         'price_unit':self.total_policy_am_after_vat
    #
    #     }))
    #     account_move = self.env['account.move'].create({
    #         'partner_id':self.partner_id.id,
    #         'policy_id':self.id,
    #         'journal_id':self.journal_id.id,
    #         'invoice_payment_term_id':self.payment_term_id.id,
    #         'move_type':'out_invoice',
    #         'policy_no':self.policy_no,
    #         'insurance_company_id':self.insurance_company_id.id
    #
    #     })
    #     account_move.invoice_line_ids = invoice_lst


    @api.depends('total_policy_am','total_policy_am_after_vat')
    def _total_vat(self):
        for rec in self:
            rec.total_policy_vat=abs(rec.total_policy_am-rec.total_policy_am_after_vat)


    # *****************Broker Commission************
    base_amount = fields.Float("Base Amount")
    approved_amount = fields.Float("Approved Amount")

    approve_percentage = fields.Float("Approve Percentage")
    broker_commision = fields.Float("Broker Commission")
    actual_sum_insured = fields.Float("Actual Sum Insured Amount",store=True,compute='_compute_insurance_amount')
    difference_sum_insured = fields.Float("Difference Sum Insured",store=True,compute='_compute_insurance_amount')
    premium_actual = fields.Float("Premium Actual",store=True,compute='_compute_insurance_amount')
    premium_difference = fields.Float("Premium Difference",compute='_compute_insurance_amount',store=True)

    # ******************vehicle Covering Page*******************

    sum_insured_vehicle = fields.Float("Sum Insured Vehicle")
    premium_car = fields.Float("Premium Car")
    issuance_fee_car = fields.Float("Issuance Fee")
    personal_accident_driver = fields.Float("Personal Accident For Driver")
    personal_accident_for_passenger = fields.Float("Personal Accident For Passengers")
    car_hire=  fields.Float("Car Hire")
    geo_ext = fields.Float("Geographical Extension")
    zero_dep = fields.Float("Zero Depreciation")
    towing_vehicle = fields.Float("Towing Vehicle")
    key_loss_thef_coverage=  fields.Float('Coverage for key loss or theft')
    glass_coverage = fields.Float('Glass Coverage')
    personal_holding_in_vehicle = fields.Float('Personal holdings in vehicle')
    employee_ids = fields.One2many('insurance.employee.data','policy_id',"Health Data")
    state = fields.Selection([('draft','Draft'),('submitted','Submitted'),('posted','Posted')],string='State',default='draft')
    total_premium_after_vat_ii = fields.Float("Total")

    def action_submit(self):
        self.state= 'submitted'

    def action_post(self):
        self.state='posted'

    @api.onchange('sum_insured','basic_prem')
    def _onchange_sum_insured(self):
        if self.sum_insured>0 and self.basic_prem:
         self.premium_percent_am=self.sum_insured/self.basic_prem




    @api.onchange('base_amount','approved_amount','approve_percentage')
    def _broker_comission_calculation(self):
        if self.approved_amount>0:
            if self.approve_percentage>0:
                self.broker_commision=(self.approved_amount*(self.approve_percentage/100))
        else:
            if self.approve_percentage>0:
                self.broker_commision=(self.base_amount*(self.approve_percentage/100))
    @api.onchange('basic_prem','vat_premium')
    def compute_total_prem(self):
        self.base_amount=self.basic_prem
        print("Yaisr")
        if self.vat_premium>0.0:
            self.total_premium_after_vat_ii =self.basic_prem+(self.basic_prem*(self.vat_premium/100))
            # print(self.total_premium_after_vat,"TOTAL")
        else:
            self.total_premium_after_vat_ii = self.basic_prem

    @api.onchange('issuening_fee','issuening_fee_percent')
    def _onchange_issueng_fee(self):
        if self.issuening_fee_percent>0:
            self.issuening_fee_total = self.issuening_fee+(self.issuening_fee*(self.issuening_fee_percent/100))
        else:
            self.issuening_fee_total = self.issuening_fee

    @api.onchange('basic_prem','issuening_fee','additional_fee_am','ded_fee_am')
    def _onchange_prem_ded_issue(self):
        self.total_policy_am = (self.basic_prem+self.issuening_fee+self.additional_fee_am)-self.ded_fee_am

    @api.onchange('total_premium_after_vat_ii','issuening_fee_total','additional_fee_am_total','ded_fee_am_total','premium_percent_am_total_ii')
    def _calculate_total(self):
        self.total_policy_am_after_vat = (self.total_premium_after_vat_ii+self.issuening_fee_total+self.premium_percent_am_total_ii+self.additional_fee_am_total)-self.ded_fee_am_total
    @api.onchange('additional_fee_am','additional_fee_am_vat')
    def _onchange_addi_fee(self):
        if self.additional_fee_am_vat>0:
            self.additional_fee_am_total = self.additional_fee_am+(self.additional_fee_am*(self.additional_fee_am_vat/100))
        else:
            self.additional_fee_am_total=self.additional_fee_am
    @api.onchange('ded_fee_am','ded_fee_am_vat')
    def _onchange_ded_am(self):
        if self.ded_fee_am_vat>0:
            self.ded_fee_am_total = self.ded_fee_am+(self.ded_fee_am*(self.ded_fee_am_vat/100))
        else:
            self.ded_fee_am_total = self.ded_fee_am

    # @api.onchange('basic_amount_percentage')
    # def _onchange_basic_percentage(self):
    #     if self.basic_amount_percentage:
    #         self.basic_amount = self.net_premium*(self.basic_amount_percentage/100)

    # @api.onchange('net_premium','issuening_fee')
    # def _gross_premium(self):
    #     self.gross_premium = self.net_premium+self.issuening_fee
    @api.onchange('business_class')
    def onchange_bussiness_class(self):
        contract = self.env['insurance.contract'].search([('insurance_company_id','=',self.insurance_company_id.id)])
        if contract:
            self.basic_amount_percentage = contract.basic_line_ids.filtered(lambda mo: mo.business_class_id.id==self.business_class.id).basic_comission
    @api.model
    def create(self, vals):

        if vals['policy_type']=='policy':
            vals['policy_id_i'] = self.env['ir.sequence'].next_by_code(
                'policy.seq')
        if vals['policy_type']=='endors':
            vals['policy_id_i'] = self.env['ir.sequence'].next_by_code(
                'endors.seq')



        return super(Policy, self).create(vals)
class BenfitLine(models.Model):
    _name = 'insurance.benefit.line'

    policy_id = fields.Many2one('insurance.policy','Policy ID')
    benefit_id = fields.Many2one('insurance.benefit','Benefits')
    amount = fields.Float("Amount")
    description = fields.Char("Description")



class Benefit(models.Model):
    _name = 'insurance.benefit'

    name = fields.Char('Name')


class Installment(models.Model):
    _name = 'insurance.installment'

    _inherit = ['mail.thread', 'mail.activity.mixin']
    policy_id = fields.Many2one('insurance.policy', 'REL')
    type_installement = fields.Selection([('fixed','Fixed'),('percentage','Percentage')],string="Type",default='fixed')
    cash_mode = fields.Many2one('cash.mode','Cash Mode')
    installment_date = fields.Date("Installment Date")
    amount_paid = fields.Float('Amount After  Percentage',store=True,compute='_compute_percentage')
    fix_amount = fields.Float('Fixed Amount')
    percentage = fields.Float("Percentage %",compute='_compute_percentage')
    no_of_installment = fields.Integer("No of Installment")

    @api.depends('policy_id','fix_amount')
    def _compute_percentage(self):
        for rec in self:
            percentage_am = 0.0
            if rec.fix_amount:
                if rec.policy_id.total_premium_after_vat_ii:
                    percentage_am = (rec.fix_amount/rec.policy_id.total_premium_after_vat_ii)*100

            rec.percentage=percentage_am
            # if rec.type_installement=='percentage':
            #     if rec.percentage:
            #         percentage_am = rec.policy_id.total_policy_am_after_vat*(rec.percentage/100)
            #         rec.amount_paid=percentage_am
            # else:
            #     rec.amount_paid=percentage_am
class CashMode(models.Model):
    _name = 'cash.mode'
    name = fields.Char("Name")


class Task(models.Model):
    _inherit = "project.task"

    policy_id = fields.Many2one('insurance.policy', string='Policy')

    def action_related_policy(self):
        return {
            'name': "Insurance Policy",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'insurance.policy',
            'views': [(False, 'form')],
            'res_id': self.policy_id.id,
        }