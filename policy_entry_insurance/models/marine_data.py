
from odoo import api, fields, models, _

class InsuranceMarine(models.Model):
    _name = 'insurance.marine'

    cargo_description = fields.Char("Cargo Description")
    vessel_name = fields.Char("Vessel Name")
    loading_port = fields.Char('Loading Port')
    credit_letter_no = fields.Char('Credit Limit No')
    sailing_date  = fields.Date("Sailing Date")
    parcel_no = fields.Char("Parcel No")
    cardo_sum_insured = fields.Char("Sum Insured")
    currency_id = fields.Many2one('res.currency',"Currency")
    packing_type = fields.Many2one('packing.type','Packing Type')
    nationality = fields.Many2one('res.country',"Nationality")
    discharge_port = fields.Char('Discharge Port')
    average_percentage = fields.Float("Average Percentage")
    package_no = fields.Char("Package No")
    deductible = fields.Float("Deductible")
    good_type = fields.Many2one('insurance.good.type',"Good Type")
    vessel_build_date = fields.Date("Vessel Build Date")
    single_policy = fields.Boolean("Single Policy")
    cover_cluase = fields.Char("Cover Clause")
    clause_type = fields.Selection([('store_port','Store - Port'),('port_store','Port Store')],string="Clause Type")
    policy_id = fields.Many2one('insurance.policy', 'Policy ID')
    premium = fields.Float("Premium")
class GoodType(models.Model):
    _name = 'insurance.good.type'

    name = fields.Char("Name")
class PackingType(models.Model):
    _name = 'packing.type'

    name = fields.Char("Name")