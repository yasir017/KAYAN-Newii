from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date




class InsurancComission(models.Model):
    _name = 'commission.scheme'


    name = fields.Char("Name")
    com_type = fields.Selection([('new','New Bussiness'),('renew','Renewel')],required=1,string="Package Type")
    salary_package = fields.Float("Salary Range")
    line_ids = fields.One2many('commission.scheme.line','com_id',string="Commission Lines")

class ComissionLines(models.Model):
    _name = 'commission.scheme.line'

    com_id = fields.Many2one('commission.scheme',"Commission")
    percentage = fields.Float('Percentage')
    revenue_from = fields.Float('Revenue From')
    revenue_to = fields.Float("Revenue To")


class SalesPerson(models.Model):
    _name = 'sale.person.commission'


    employee_id = fields.Many2one('hr.employee','Salesperson')
    salary = fields.Float('Salary')
    move_ids = fields.One2many('account.move','saleperson_id',string="Invoices")