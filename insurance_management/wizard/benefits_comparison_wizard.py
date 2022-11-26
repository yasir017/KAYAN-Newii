import pdb

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import SUPERUSER_ID
from odoo import api, fields, models, _,exceptions
from odoo.exceptions import Warning, UserError
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import file_open, formatLang
import pandas as pd
import logging
_logger = logging.getLogger(__name__)
import io
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
try:
    from base64 import encodebytes
except ImportError:
    from base64 import encodestring as encodebytes
    _logger.debug('Cannot `import base64`.')

class BenefitComparisonWizard(models.TransientModel):
    _name = "benefit.comparison.wizard"
    _description = "benefit.comparison.wizard"


    client_id = fields.Many2one('client.branch',string='Client')
    medical_visibility_check = fields.Boolean(related='client_id.medical_visibility_check',
                                              string='Medical Visibility Check',
                                              compute='get_insurance_pages_visibility')
    vehicle_visibility_check = fields.Boolean(related='client_id.vehicle_visibility_check',
                                              string='Vehicle Visibility Check',
                                              compute='get_insurance_pages_visibility')
    insurance_quotation_id = fields.Many2many('insurance.quotation',string='Insurance Quotation',domain="[('client_branch_id','=',client_id)]")
    vehicle_quotation_id = fields.Many2many('vehicle.quotation', string='Vehicle Quotation',
                                             domain="[('client_branch_id','=',client_id)]")


    def action_confirm(self):
        data = {}
        data['form'] = self.read(['client_id', 'insurance_quotation_id', 'vehicle_quotation_id'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['client_id', 'insurance_quotation_id', 'vehicle_quotation_id'])[0])
        # data['client_id']=self.client_id
        # data.append({'insurance_quotation_id': self.insurance_quotation_id})
        # data.append({'vehicle_quotation_id': self.vehicle_quotation_id})
        return self.env.ref('insurance_management.action_benefits_comparison_report').report_action(self, data=data, config=False)



    # def action_confirm(self):
    #     if self.medical_visibility_check == True:
    #         self.insurance_quotation_id.select = True
    #         self.insurance_quotation_id.state = "selected"
    #         for line in self.client_id.insurance_quotation_ids.filtered(lambda b: b.id != self.insurance_quotation_id.id):
    #             line.state = 'cancel'
    #     if self.vehicle_visibility_check == True:
    #         self.vehicle_quotation_id.select = True
    #         self.vehicle_quotation_id.state = "selected"
    #         for line in self.client_id.vehicle_quotation_ids.filtered(
    #                 lambda b: b.id != self.vehicle_quotation_id.id):
    #             line.state = 'cancel'
    #     self.client_id.state = 'validate'