from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    request_event_live_time = fields.Integer(default=90)
    request_event_live_time_uom = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months')], default='days', ondelete='set default')
    request_event_auto_remove = fields.Boolean(
        string='Automatically remove events older than',
        default=True)

    request_mail_suggest_partner = fields.Boolean(
        string="Suggest request partner for mail recipients")
    request_mail_suggest_global_cc = fields.Boolean(
        default=True,
        string="Suggest request's global CC for mail recipients")
    request_mail_create_author_contact_from_email = fields.Boolean(
        string="Create partners from incoming emails",
        help="If set to True, then if request came from email that has no "
             "related partner, then partner will be created automatically. "
             "Also, same logic applied to requests created from website by "
             "unregistered users.")
    request_mail_create_cc_contact_from_email = fields.Boolean(
        string="Create partners from CC of incoming emails",
        help="If set to True, then if request came from email where CC has no "
             "related partner, then partner will be created automatically. "
             "Also, same logic applied to requests created from website by "
             "unregistered users.")
    request_mail_auto_subscribe_cc_contacts = fields.Boolean(
        string="Auto subscribe CC contacts on mail",
        help="If set to True, CC contacts will be automatically subscribed "
             "on the specified mail")
    request_preferred_list_view_mode = fields.Selection(
        [('default', 'Default'),
         ('kanban', 'Kanban'),
         ('list', 'List')],
        default='default', string='Preferred view type',
        help='Choose preferred view type for requests')
