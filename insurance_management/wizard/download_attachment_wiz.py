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

class DownloadAttachmentWiz(models.TransientModel):
    _name = "download.attachment.wiz"
    _description = "download.attachment.wiz"


    attachment_id = fields.Many2one('ir.attachment',string='File')



    def action_confirm(self):
        print('y')