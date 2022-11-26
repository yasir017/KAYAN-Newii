
from odoo import api, fields, models, _

class BussinessClass(models.Model):
    _name = 'insurance.business.class'


    policy_id = fields.Many2one('insurance.policy','Policy ID')
    currency_id = fields.Many2one('res.currency','Currency')
    vehicle_line_ids = fields.One2many('vehicle.lines','class_id',"Vehicles")
    total_vehicle = fields.Float('Total')
    total_insurance=  fields.Float('Total Vehicle')

    driver_line = fields.One2many('driver.lines','class_id')

    deducation_line = fields.One2many('ded.line','class_id','Deduction Type')
    vehicle_ids = fields.One2many('insurance.vehicle','class_id',string="Vehicle Detail")

    def action_import_vehicle_data(self):
        pass

    def export_vehicle(self):
        pass

class DedLine(models.Model):
    _name = 'ded.line'

    class_id = fields.Many2one('insurance.business.class', 'Rel')
    ded_type = fields.Many2one('ded.type','Deduction Type')
    ded_percentage = fields.Float('Deduction Percentage')
    ded_amount = fields.Float('Deduction Amount')
    ded_description = fields.Char('Deduction Description')
class DeducationType(models.Model):
    _name = 'ded.type'

    name = fields.Char('Name')
class DriverLine(models.Model):
    _name = 'driver.lines'

    class_id = fields.Many2one('insurance.business.class', 'Rel')
    type_of = fields.Selection([('passenger_pa','Passenger P.A'),('driver_pa','Driver P.A'),('tpl','TPL')],string="Type")
    limit_person = fields.Float('Limit person')
    permium = fields.Float('Permium')
    ded = fields.Float('DED.')
    no = fields.Float('NO')
    # tpl = fields.Boolean('TPL')
class VehicleLines(models.Model):
    _name = 'vehicle.lines'

    class_id = fields.Many2one('insurance.business.class','Rel')
    truck_type = fields.Selection([('commercial_truck','Commercial Truck'),('private_vehicle','Private Vehicle')],string="Vehicle Type")
    commercial_truck = fields.Float('Commercial Truck')
    insurance_amount = fields.Float('Insurance Amount')
    no_of_truck = fields.Float('Total Truck No')