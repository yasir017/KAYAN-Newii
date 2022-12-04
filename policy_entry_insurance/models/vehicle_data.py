from datetime import datetime

from odoo import api, fields, models, _

class Vehicle(models.Model):
    _name = 'insurance.vehicle'
    _rec_name = "owener_name"

    class_id = fields.Many2one('insurance.business.class', 'Rel')
    policy_id = fields.Many2one('insurance.policy', 'Policy ID')
    currency_id = fields.Many2one('res.currency','Currency')
    vehicle_image = fields.Binary(string='Vehicle Image')

    vehicle_type_id = fields.Many2one('vehicle.type',"Vehicle Type")
    plate_no = fields.Char("Plate No. (En)")
    plate_no_ar = fields.Char(string='Plate No. (Ar)')
    model_no =  fields.Selection([(str(num), str(num)) for num in range(1900, (datetime.now().year)+1 )],string="Model Year")
    chassis = fields.Char("Chassis",required=1)
    capacity = fields.Integer("Capacity")
    driver_insurance=  fields.Boolean("Driver Insurance")
    covering_maintenance = fields.Selection([('work_shop', 'Workshop'),('agency', 'Agency')], string="Covering Maintenance")
    value = fields.Float("Sum Insured")
    owener_name = fields.Char("Owner Name")
    owner_id = fields.Char("Owner ID No")
    custom_id  = fields.Char("Custom ID")
    seq_no = fields.Char("Sequence No")
    user_id_no = fields.Char("User ID No")
    user_name = fields.Char("User Name")
    building_no = fields.Char("Building No")
    additional_no = fields.Char("Additional No")
    street = fields.Char("stree")
    city = fields.Many2one('insurance.city','City')
    unit_no = fields.Char("Unit No")
    po_box = fields.Char("PO Box")
    zip_code = fields.Char("Zip Code")
    neighbour_head = fields.Char("Neighbor Head")
    mobile_no = fields.Integer("Mobile No")
    istamara_expiry = fields.Date("Istemara Expiry")
    vehicle_color = fields.Char("Vehicle Color")
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand', string='Vehicle Manufacturer')
    vehicle_model_id = fields.Many2one('fleet.vehicle.model', string='Vehicle Model',domain="[('brand_id', '=?', vehicle_make_id)]")
    gcc_cover = fields.Boolean("GCC Cover")
    natural_peril_cover = fields.Boolean("NATURAL PERIL Cover")
    dob_owner = fields.Date("DOB Owner")
    nationality = fields.Many2one('res.country',"Nationality")
    premium = fields.Float("Premium")
    vat = fields.Float(string='VAT', default=15)
    total = fields.Float(string='Total',store=True, compute='_get_q_line_total')
    endorsment_am = fields.Float("Endorsement Amount")
    endorsment_type = fields.Selection([('add', 'Upgrade'), ('sub', 'Downgrade'), ('remove', 'Cancel')],
                                       string='Operation Type')

    @api.onchange('vehicle_make_id')
    def set_model_wrt_vehicle_make_id(self):
        for rec in self:
            if rec.vehicle_model_id:
                if rec.vehicle_model_id.brand_id.id != rec.vehicle_make_id.id:
                    rec.vehicle_model_id = False

    @api.onchange('vehicle_model_id')
    def set_make_wrt_vehicle_model_id(self):
        for rec in self:
            rec.vehicle_make_id = rec.vehicle_model_id.brand_id.id

    @api.depends('vat', 'premium')
    def _get_q_line_total(self):
        for rec in self:
            rec.total = rec.premium+(rec.premium*(rec.vat/100))
    # rate = fields.Float(string='Premium')
    # effective_date = fields.Date('Effective Date')
    # ben_name = fields.Char('Ben.Name')
    # ben_address = fields.Char('Ben.Address')
    # owener_address = fields.Char("Owner Address")
    # motor_no = fields.Char("Motor No")
    #
    # brand_name = fields.Many2one('vehicle.brand','Brand Name')
    # contact_person = fields.Char('Contact person')
    # contacy_phone_no = fields.Integer("Contact Person No")
    # location = fields.Many2one('insurance.location')
    # insurance_amount = fields.Float("Insurance Amount",required=1)
    # net_premium = fields.Float("Net Premium")
    # over_age_am = fields.Float("Over Age Amount")
    # current_net_premium = fields.Float("Current Net Premium")
    # total_net_premium = fields.Float("Total Net premium")
    #
    # include_eq = fields.Boolean("Include Equipment")
    # eq_description = fields.Char("Eq.description")
    # eq_net_premium = fields.Float("Equipment Net Premium")
    # eq_insurance_am = fields.Float("Eq. Insurance Amount")
    # exclusion_survey = fields.Binary("Exclusion Survey")


class LocationMaster(models.Model):
    _name = 'insurance.location'

    name = fields.Char("Location")
class BrandName(models.Model):
    _name = 'vehicle.brand'

    name = fields.Char('Brand Name')
class VehicleType(models.Model):
    _name = 'vehicle.type'

    name = fields.Char("Vehicle Type")

class City(models.Model):
    _name = 'insurance.city'

    name = fields.Char("Name")