from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Policy(models.Model):
    _inherit = 'insurance.policy'

    insurance_company_id = fields.Many2one('insurance.company', "Insurance Company")
    insurance_partner = fields.Many2one('res.partner','Insurance Partner')

    @api.onchange('insurance_company_id')
    def onchange_insurance_company_id(self):
        self.insurance_partner = self.insurance_company_id.ins_company_partner_id.id
    insurance_type_id = fields.Many2one('insurance.type', string='Insurance Type', required='1')
    insurance_sub_type_id = fields.Many2one('insurance.sub.type', string='Insurance Sub Type',
                                            domain="[('insurance_type_id','=',insurance_type_id)]")
    benefits_custome_ids = fields.One2many('policy.benefits','policy_id',"Benefits")

    medical_boolean = fields.Boolean("Is medical",store=1,compute='_type_of_insurance')
    vehicle_boolean = fields.Boolean("Is vehicle",store=1,compute='_type_of_insurance')
    marine_boolean = fields.Boolean("Is Marine ",store=1,compute='_type_of_insurance')
    company_standard = fields.Selection([('sme', 'SME'), ('corporate', 'Corporate')
                                         ], string='Company Standard')
    type_of_business = fields.Selection([('renewal', 'Renewal'), ('new_business', 'New')
                                         ], string='Type of Business')
    data_collect_id = fields.Many2one('client.branch','Data collection')
    attachment_count = fields.Integer('Count',compute='_attachments')
    health_count = fields.Integer("Health Count",compute='_count_health',store=True)
    vehicle_count = fields.Integer("Vehicle Count",compute='_count_vehicle',store=True)
    hide_credit_note_button = fields.Boolean(compute='_compute_negative',store=True)

    count_endors_health = fields.Integer(compute='endors_health_count')
    invoice_count = fields.Integer(compute='_count_invoices',store=True)
    count_credit_notes = fields.Integer(compute='_count_credit_notes',store=True)
    count_endors_vehicle = fields.Integer(compute='endors_vehicle_count')
    count_commission_invoice = fields.Integer("Count Commission Invoice",compute='_commission_inv')
    count_govt_fee = fields.Integer("Govt Fee",compute='compute_govt')


    @api.depends('move_ids')
    def compute_govt(self):
        for rec in self:
            invoices = rec.move_ids.filtered(lambda b: b.move_type == 'in_invoice')
            rec.count_govt_fee = len(invoices)
    @api.depends('move_ids')
    def _commission_inv(self):
        for rec in self:
            invoices = rec.move_ids.filtered(lambda b: b.move_type == 'out_invoice' and b.invoice_type=='commission_inv')
            rec.count_commission_invoice=len(invoices)
    @api.depends('endors_vehicle_ids')
    def endors_vehicle_count(self):
        for rec in self:
            rec.count_endors_vehicle = len(rec.endors_vehicle_ids)
    @api.depends('move_ids')
    def _count_credit_notes(self):
        for rec in self:
            invoices = rec.move_ids.filtered(lambda b: b.move_type == 'out_refund')
            rec.count_credit_notes = len(invoices)
    @api.depends('move_ids')
    def _count_invoices(self):
        for rec in self:
            invoices = rec.move_ids.filtered(lambda b: b.move_type=='out_invoice' and b.invoice_type=='policy')
            rec.invoice_count=len(invoices)

    @api.depends('health_endors_ids')
    def endors_health_count(self):
        for rec in self:
            rec.count_endors_health=len(rec.health_endors_ids)

    def action_health_endors(self):
        return {
            'name': 'Endors Health Details',
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.employee.data',
            'views': [
                [self.env.ref('policy_entry_insurance.view_health_data_tree').id, 'list'],
                [self.env.ref('policy_entry_insurance.view_health_data_form').id, 'form']],
            'view_mode': 'tree,form,kanban',
            'context': {
                # 'default_policy_id': self.id,
            },
            'domain': [('id', 'in', self.health_endors_ids.ids)],
        }

    def action_vehicle_endors(self):
        return {
            'name': 'Endors Vehicle Details',
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.vehicle',
            'views': [
                [self.env.ref('policy_entry_insurance.view_insurance_vehicle_tree').id, 'list'],
                [self.env.ref('policy_entry_insurance.view_insurance_vehicle_form').id, 'form']],
            'view_mode': 'tree,form,kanban',
            'context': {
                # 'default_policy_id': self.id,
            },
            'domain': [('id', 'in', self.endors_vehicle_ids.ids)],
        }

    def action_open_invoices(self):
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'context': {
                'default_policy_id': self.id,
                # 'default_invoice_ref': self.id,
                'default_insurance_company_id':self.insurance_company_id.id,
                'default_move_type': 'out_invoice',
                'default_partner_id':self.partner_id.id,
                'default_policy_no':self.policy_no,
                'default_invoice_type': 'endors' if self.policy_type == 'endors' else 'policy'
                # 'default_commission_boolean': True

            },
            'domain': [('move_type','=','out_invoice'),('invoice_type','=','policy'),('id', '=', self.move_ids.ids)],
        }

    def action_commission_invoices(self):
        return {
            'name': 'Commission Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'context': {
                'default_policy_id': self.id,
                # 'default_invoice_ref': self.id,
                'default_insurance_company_id':self.insurance_company_id.id,
                'default_move_type': 'out_invoice',
                'default_partner_id':self.insurance_company_id.ins_company_partner_id.id,
                'default_policy_no':self.policy_no,
                'default_invoice_type': 'commission_inv',
                'default_commission_boolean': True

            },
            'domain': [('move_type','=','out_invoice'),('id', '=', self.move_ids.ids),('invoice_type','=','commission_inv')],
        }


    def action_govt_fee(self):
        params = self.env['ir.config_parameter'].sudo()
        govt_partnr = params.get_param('insurance_management.govt_partner', )
        return {
                'name': 'Bills',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'context': {
                    'default_policy_id': self.id,
                    # 'default_invoice_ref':self.id,
                    'default_partner_id':govt_partnr,
                    'default_move_type':'in_invoice',
                    'default_govt_boolean':True

                },
                'domain': [('move_type', '=', 'in_invoice'),('id', '=', self.move_ids.ids)],
            }
    def action_credit_invoices(self):
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'context': {
                'default_policy_id': self.id,
                # 'default_invoice_ref': self.id,
                'default_insurance_company_id':self.insurance_company_id.id,
                'default_move_type': 'out_invoice',
                'default_partner_id':self.partner_id.id,
                'default_policy_no':self.policy_no,
                'default_invoice_type':'endors' if self.policy_type=='endors' else 'policy'
                # 'default_commission_boolean': True

            },
            'domain': [('move_type','=','out_refund'),('id', '=', self.move_ids.ids)],
        }
    # hide_invoice=  fields.Boolean(compute='_compute_negative')
    @api.depends('total_policy_am_after_vat')
    def _compute_negative(self):
        for rec in self:
           if  rec.total_policy_am_after_vat<0:
               rec.hide_credit_note_button=True
               # rec.hide_invoice=False
           else:
               rec.total_premium_after_vat=False
               # rec.hide_invoice=True
           # if rec.total_premium_after_vat>0:
           #     rec.hide_invoice=True


    @api.constrains('health_endors_ids')
    def _contraint_endors(self):
        for records in self:
            if records.insurance_type_id.ins_type_select=='is_medical':
                if records.policy_type == 'endors':
                    for rec in records.health_endors_ids:
                        if rec.endorsment_type:
                            if rec.endorsment_type == 'sub':
                                if rec.endorsment_am > 0:
                                    raise ValidationError(
                                        "The amount should be in negative if endorsement type is downgrade")
                            elif rec.endorsment_type == 'add':
                                if rec.endorsment_am < 0:
                                    raise ValidationError(
                                        "The endorsement amount should be greater then 0 if type is upgrade")

    @api.onchange('prev_policy')
    def _onchange_prev(self):
        line = [(5,0,0)]
        self.partner_id = self.prev_policy.partner_id.id
        self.insurance_company_id = self.prev_policy.insurance_company_id.id
        self.insurance_sub_type_id = self.prev_policy.insurance_sub_type_id.id
        self.insurance_type_id = self.prev_policy.insurance_type_id.id
        self.type_of_business = self.prev_policy.type_of_business
        self.company_standard = self.prev_policy.company_standard
        self.journal_id = self.prev_policy.journal_id.id
        self.payment_term_id = self.prev_policy.payment_term_id.id
        self.country_id = self.prev_policy.country_id.id
        self.fed_state_id = self.prev_policy.fed_state_id.id
        self.expiry_date = self.prev_policy.expiry_date
        self.start_date  = self.prev_policy.start_date
        for benefits in self.prev_policy.benefits_custome_ids:
            vals={
                # 'policy_id': policy.id,
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
            }
            line.append((0,0,vals))
        self.benefits_custome_ids=line

    def action_create_create_note(self):
        invoice_lst = []
        product_id = self.env['product.product'].search([('insurance_product', '=', True)], limit=1)
        invoice_lst.append((0, 0, {
            'product_id': product_id.id,
            'name': product_id.name,
            'quantity': 1,
            'price_unit': self.total_policy_am_after_vat

        }))
        account_move = self.env['account.move'].create({
            'partner_id': self.partner_id.id,
            'policy_id': self.id,
            'journal_id': self.journal_id.id,
            'invoice_payment_term_id': self.payment_term_id.id,
            'move_type': 'out_refund',
            'policy_no': self.policy_no,
            'insurance_company_id': self.insurance_company_id.id

        })
        account_move.invoice_line_ids = invoice_lst
        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': account_move.id,
            # 'domain': [('move_type', '=', 'out_invoice'), ('invoice_ref', '=', self.id)],
        }

    def action_create_invoice(self):
        invoice_lst = []
        product_id = self.env['product.product'].search([('insurance_product','=',True)],limit=1)
        invoice_lst.append((0,0,{
            'product_id':product_id.id,
            'name':product_id.name,
            'quantity':1,
            'price_unit':self.total_policy_am_after_vat

        }))
        account_move = self.env['account.move'].create({
            'partner_id':self.partner_id.id,
            'policy_id':self.id,
            'journal_id':self.journal_id.id,
            'invoice_payment_term_id':self.payment_term_id.id,
            'move_type':'out_invoice',
            'policy_no':self.policy_no,
            'invoice_type': 'endors' if self.policy_type == 'endors' else 'policy',
            'insurance_company_id':self.insurance_company_id.id

        })
        account_move.invoice_line_ids = invoice_lst

        return {
            'name': 'Invoice',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id':account_move.id,
            # 'domain': [('move_type', '=', 'out_invoice'), ('invoice_ref', '=', self.id)],
        }
    @api.depends('vehicle_detail','endors_vehicle_ids','policy_type','health_endors_ids', 'sum_insured', 'marine_ids', 'basic_prem', 'employee_ids')
    def _compute_insurance_amount(self):
        net_premium = 0.0
        amount = 0.0
        for rec in self:
            if rec.policy_type=='policy':
                if rec.insurance_type_id.ins_type_select=='is_vehicle':
                    if rec.vehicle_detail:
                        for line in rec.vehicle_detail:
                            amount += line.value
                            net_premium += line.premium
                elif rec.insurance_type_id.ins_type_select=='is_marine':
                    for line in rec.marine_ids:
                        net_premium += line.premium
                        amount += line.cardo_sum_insured
                elif rec.insurance_type_id.ins_type_select == 'is_medical':
                    if rec.employee_ids:
                        for health in rec.employee_ids:
                            net_premium += health.rate

            elif rec.policy_type=='endors':
                if rec.insurance_type_id.ins_type_select == 'is_medical':
                    if rec.health_endors_ids:
                        for health in rec.health_endors_ids:
                            net_premium += health.endorsment_am
                if rec.insurance_type_id.ins_type_select == 'is_vehicle':
                    if rec.endors_vehicle_ids:
                        for vehicle_endors in rec.endors_vehicle_ids:
                            net_premium+=vehicle_endors.endorsment_am
            rec.actual_sum_insured = amount
            rec.premium_actual = net_premium
            rec.premium_difference = abs(rec.basic_prem - net_premium)
            rec.difference_sum_insured = abs(amount - rec.sum_insured)
    @api.depends('vehicle_detail')
    def _count_vehicle(self):
        for rec in self:
            rec.vehicle_count=len(rec.vehicle_detail)
    @api.depends('employee_ids')
    def _count_health(self):
        for rec in self:
            rec.health_count=len(rec.employee_ids)
    def _attachments(self):
        for rec in self:
            total_attachment = self.env['customer.attachment'].search([('policy_id','=',rec.id)])
            rec.attachment_count = len(total_attachment)
    def action_open_attachment(self):
        return {
            'name': 'Attachments Details',
            'type': 'ir.actions.act_window',
            'res_model': 'customer.attachment',
            'views': [
                      [self.env.ref('insurance_management.view_customer_attachment_tree').id, 'list'],
                    [self.env.ref('insurance_management.view_customer_attachment_form').id, 'form']],
            'view_mode': 'tree,form,kanban',
            'context': {
                'default_policy_id': self.id,
            },
            'domain': [('policy_id', '=', self.id)],
        }

    def action_health_lines(self):
        return {
            'name': 'Health Details',
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.employee.data',
            'views': [
                      [self.env.ref('policy_entry_insurance.view_health_data_tree').id, 'list'],
                    [self.env.ref('policy_entry_insurance.view_health_data_form').id, 'form']],
            'view_mode': 'tree,form,kanban',
            'context': {
                'default_policy_id': self.id,
            },
            'domain': [('policy_id', '=', self.id)],
        }

    def action_vehicle_lines(self):
        return {
            'name': 'Vehicle Details',
            'type': 'ir.actions.act_window',
            'res_model': 'insurance.vehicle',
            'views': [
                [self.env.ref('policy_entry_insurance.view_insurance_vehicle_tree').id, 'list'],
                [self.env.ref('policy_entry_insurance.view_insurance_vehicle_form').id, 'form']],
            'view_mode': 'tree,form,kanban',
            'context': {
                'default_policy_id': self.id,
            },
            'domain': [('policy_id', '=', self.id)],
        }
    @api.depends('insurance_type_id')
    def _type_of_insurance(self):

        for rec in self:
            rec.medical_boolean=False
            rec.vehicle_boolean=False
            rec.marine_boolean=False
            if rec.insurance_type_id.ins_type_select=='is_medical':
                rec.medical_boolean=True

            elif rec.insurance_type_id.ins_type_select=='is_vehicle':
                rec.vehicle_boolean=True
            elif rec.insurance_type_id.ins_type_select=='is_marine':
                rec.marine_boolean=True
class PolicyBenfits(models.Model):
    _name = 'policy.benefits'

    policy_id = fields.Many2one('insurance.policy','Policy ID')
    name = fields.Char()
    benefit_name = fields.Char(store=True)
    # insurance_company_id = fields.Many2one(related='insurance_quotation_id.insurance_company_id',
    #                                        string='Insurance Company')
    category_type = fields.Selection([('vip', 'VIP'), ('a+', 'A+'), ('a', 'A'), ('b', 'B'), ('c', 'C')],
                                     string='Category Type')
    benefit_id = fields.Many2one('benefit.name', string='Benefit')
    benefit_value = fields.Char(string='Value')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)
    client_branch_id = fields.Many2one('client.branch', string='Client Branch')
    # insurance_quotation_id = fields.Many2one('insurance.quotation', string='Insurance Quotation')

    # excluded_included = fields.Selection([('excluded','Excluded'),('included','Included')],string='Excluded/Included')
    # fixed_vary = fields.Selection([('fixed','Fixed'),('vary','Vary')],string='Fixed/Vary')

    included = fields.Boolean(string='Included?')
    vary = fields.Boolean(string='Is Vary?')
    from_value = fields.Float(string='From Value')
    to_value = fields.Float(string='To Value')
    description = fields.Char('description')
    @api.onchange('benefit_id')
    def custom_benefit_name(self):
        self.benefit_name = self.benefit_id.name


class EmployeeData(models.Model):
    _inherit = 'insurance.employee.data'

    insurance_company_id = fields.Many2one('insurance.company', string="Insurance Company",compute='_compute_insurance_company',store=1)

    @api.depends('policy_id')
    def _compute_insurance_company(self):
        for rec in self:
            rec.insurance_company_id = rec.policy_id.insurance_company_id.id
