from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
class HealthData(models.Model):
    _name = 'insurance.health'

    _description = 'Health Data'

    policy_id = fields.Many2one('insurance.policy', 'Policy ID')
    currency_id = fields.Many2one('res.currency',"Currency")
    no_emp = fields.Float("No Of Employees")
    category_name = fields.Char('Category Name')
    auto_acceptance_limit = fields.Char("Automatic Acceptance Limit")
    max_sum_insured = fields.Float("Max Sum Insured")
    min_sum_insured = fields.Float("Min Sum Insured")
    death_rate = fields.Float("Death Rate")
    total_permanent_disability_rate = fields.Float("Total Permanent Disability Rate")
    cont_europ = fields.Selection([('continental','Continental'),('european','European')])
    is_partial_disable = fields.Boolean("Is partial Permanent Disability")
    partial_rate = fields.Float("Partial Rate")
    is_accidental_death = fields.Boolean("Is Accidental Death")
    accidental_rate = fields.Float("Accidental Rate")
    is_weekly_income = fields.Boolean("Is weekly income")
    weekly_desc = fields.Char("Desc")
    total_rate = fields.Float("Total Rate")
    employee_ids = fields.Char("Employee Detail")
    # ***********Medical*********

    total_no_person  = fields.Float("Total No of Person")
    benefit_name = fields.Char("Benefit Name")
    no_of_person = fields.Float("No of Person")
    total = fields.Float("Total")
    accommodation = fields.Many2one('insurance.accommodation','Accommodation')
    gross_prem = fields.Float("Gross Premium")
    net_prem = fields.Float("Net Premium")
    from_age = fields.Float("From Age")
    to_age = fields.Float("To Age")
    service_ids = fields.One2many('insurance.service','health_id',"Service")


class InsuranceService(models.Model):
    _name = 'insurance.service'

    health_id = fields.Many2one('insurance.health','Health')
    service_id = fields.Many2one('services','service')
    limit = fields.Float("Limit")
    co_pay_amount = fields.Float("Co-Pay Amount")
    co_percent = fields.Float("Co-Pay Percent")
    waiting_before = fields.Float("Waiting Before")
    wating_after = fields.Float("Waiting After")
    population = fields.Float("Population")

class Services(models.Model):
    _name = 'services'

    name = fields.Char('Service')
class EmployeeData(models.Model):
    _name = 'insurance.employee.data'
    _description = 'Employee Data'

    # health_id = fields.Many2one('insurance.health','Health')
    policy_id = fields.Many2one('insurance.policy', 'Policy')
    member_id = fields.Char(string='Member ID')
    dependent_id = fields.Char(string='Dependent ID')
    name = fields.Char(string='Name', tracking=True)

    client_image = fields.Binary(string='Client Image')
    arabic_name = fields.Char(string='Arabic Name', tracking=True)
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female')], string='Gender')
    dob = fields.Date(string='Birth Date')
    dob_hijra = fields.Char(string='Birth Date(Hijra)')
    age = fields.Float(string='Age',compute='get_member_age')
    # member_type = fields.Char(string='Member Type')
    # class_no = fields.Char( string='Class No')
    # age_category = fields.Char(string='Age Category')
    risk_no = fields.Char(string='Risk No')
    nationality = fields.Many2one('res.country', 'Nationality')
    staff_no = fields.Char(string='Staff No')
    # member_category = fields.Selection(
    #     [('manager', 'Manager'), ('staff', 'Staff'), ('skilled_worker', 'Skilled Worker'),
    #      ('supervisor', 'Supervisor')], string='Member Category')
    # member_category = fields.Many2one('member.category', string='Member Category')
    mobile1 = fields.Char(string='Mobile No (1)')
    mobile2 = fields.Char(string='Mobile No (2)')
    dep_no = fields.Char(string='Dep Code')
    sponser_id = fields.Char(string='Sponser ID')
    # occupation = fields.Char(string='Occupation')
    marital_status = fields.Selection(
        [('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced'), ('widowed', 'Widowed')],
        string='Marital Status')
    # marital_status = fields.Selection([('single','Singe)],string='Relation')
    elm_relation = fields.Selection([('not_specified', 'Not Specified'), ('son', 'Son'), ('daughter', 'Daughter'),
                                     ('wife', 'Wife'),
                                     ('brother', 'Brother'),
                                     ('sister', 'Sister'),
                                     ('parent', 'Parent'),
                                     ('grand_parent', 'Grand Parent'),
                                     ('husband', 'Husband'),
                                     ('other', 'Other'),
                                     ('hoh', 'HOH')], string='ELM Relation')
    vip = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='VIP?')
    as_vip = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='AS VIP?')
    bank_id = fields.Many2one('res.bank', string='Bank')
    # branch_id = fields.Many2one('insurance.branch', string='Branch ID')
    rate = fields.Float("Premium")
    vat = fields.Float("Vat")
    total = fields.Float("Total After Vat",compute='_compute_total',store=True)
    endorsment_am = fields.Float("Endorsement Amount")
    endorsment_type = fields.Selection([('add','Upgrade'),('sub','Downgrade'),('remove','Cancel')],string='Operation Type')

    @api.depends('dob')
    def get_member_age(self):
        for rec in self:
            if rec.dob:
                born = rec.dob
                today = date.today()
                rec.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                rec.age = 0

    @api.depends('rate','vat')
    def _compute_total(self):
        for rec in self:
            rec.total = rec.rate+(rec.rate*(rec.vat/100))
class InsuranceAccomodation(models.Model):
    _name = 'insurance.accommodation'
    _description = "Insurance Accommodation"

    name=  fields.Char("Name")