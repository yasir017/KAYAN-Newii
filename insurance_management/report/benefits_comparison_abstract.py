# -*- coding: utf-8 -*-
import pdb
import time
from odoo import api, models
from dateutil.parser import parse
from odoo.exceptions import UserError

class BenefitsComparison(models.AbstractModel):
    _name = 'report.insurance_management.comparison_benefits'
    _description = 'Benefits Comparison Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        active_model = self.env.context.get('active_model')
        # pdb.set_trace()
        client_id = data['form'].get('client_id')[0]
        insurance_quotation_id = data['form'].get('insurance_quotation_id')
        vehicle_quotation_id = data['form'].get('vehicle_quotation_id')
        client = self.env['client.branch'].search([('id', '=', client_id)])

        customer_custom_benefits = self.env['customer.custom.benefit']
        insurance_quotations = self.env['insurance.quotation'].search([('id', 'in', insurance_quotation_id)], order="insurance_company_id")
        for quoit in insurance_quotations:
            for benefit in quoit.custom_benefits_ids:
                customer_custom_benefits += benefit

        vip_dict_benefit_wise = {}
        vip_benefits = customer_custom_benefits.filtered(lambda b: b.category_type == 'vip')
        vip_benefits.search([], order="insurance_company_id")
        for vip_line in vip_benefits:
            key = vip_line.benefit_id.id
            if key in vip_dict_benefit_wise:

                vip_dict_benefit_wise[key].get('company_value_list').append(
                    {'company': vip_line.insurance_company_id, 'value': vip_line.benefit_value})
            else:
                vip_dict_benefit_wise[key] = {
                    'key': key,
                    'company_value_list': [{'company': vip_line.insurance_company_id,'value': vip_line.benefit_value}],
                    'benefit_id': vip_line.benefit_id,
                }

        a_plus_dict_benefit_wise = {}
        a_plus_benefits = customer_custom_benefits.filtered(lambda b: b.category_type == 'a+')
        vip_benefits.search([], order="insurance_company_id")
        for a_plus_line in vip_benefits:
            key = a_plus_line.benefit_id.id
            if key in a_plus_dict_benefit_wise:

                a_plus_dict_benefit_wise[key].get('company_value_list').append(
                    {'company': a_plus_line.insurance_company_id, 'value': a_plus_line.benefit_value})
            else:
                a_plus_dict_benefit_wise[key] = {
                    'key': key,
                    'company_value_list': [{'company': a_plus_line.insurance_company_id, 'value': a_plus_line.benefit_value}],
                    'benefit_id': a_plus_line.benefit_id,
                }



        a_benefits = customer_custom_benefits.filtered(lambda b: b.category_type == 'a')



        vehicle_quotations = self.env['vehicle.quotation'].search([('id', 'in', vehicle_quotation_id)])
        # docs = self.env[active_model].browse(self.env.context.get('active_id'))
        outstanding_invoice = []       
        # invoices = self.env['account.move'].search([('invoice_date_due', '>=', docs.start_date),('invoice_date_due', '<=', docs.end_date),('move_type','=', 'out_invoice'),('state','=','posted')])
        # if invoices:
        amount_due = 0
        # for total_amount in invoices:
        #     amount_due += total_amount.amount_residual
        # docs.total_amount_due = amount_due

        return {
            'client': client,
            'insurance_quotations': insurance_quotations,
            'vehicle_quotations': vehicle_quotations,
            'vip_dict_benefit_wise': vip_dict_benefit_wise,
            'a_plus_dict_benefit_wise': a_plus_dict_benefit_wise,
        }
        # else:
        #     raise UserError("There is not any Outstanding invoice")
