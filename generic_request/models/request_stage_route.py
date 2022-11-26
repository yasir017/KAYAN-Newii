from odoo import models, fields, api, exceptions, _


class RequestStageRoute(models.Model):
    _name = "request.stage.route"
    _inherit = [
        'generic.mixin.track.changes',
        'mail.thread',
    ]
    _description = "Request Stage Route"
    _order = "sequence"

    name = fields.Char(readonly=False, translate=True)
    sequence = fields.Integer(
        default=5, index=True, required=True, tracking=True)
    stage_from_id = fields.Many2one(
        'request.stage', 'From', ondelete='restrict',
        required=True, index=True, tracking=True)
    stage_to_id = fields.Many2one(
        'request.stage', 'To', ondelete='restrict',
        required=True, index=True, tracking=True)
    request_type_id = fields.Many2one(
        'request.type', 'Request Type', ondelete='cascade',
        required=True, index=True, tracking=True)

    allowed_group_ids = fields.Many2many(
        'res.groups', string='Allowed groups')
    allowed_user_ids = fields.Many2many(
        'res.users', string='Allowed users')
    close = fields.Boolean(
        related='stage_to_id.closed', store=True, index=True, readonly=True,
        help='If set, then this route will close request')

    require_response = fields.Boolean(
        store=True,
        help="If set, then user will be asked for comment on this route")
    default_response_text = fields.Html(translate=True)

    button_style = fields.Selection([
        ('default', 'Default'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('success', 'Success'),
        ('danger', 'Danger'),
        ('warning', 'Warning'),
        ('info', 'Info'),
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('link', 'Link'),
    ], default='default', help='Buttons style')

    reopen_as_type_ids = fields.Many2many(
        'request.type', 'request_type_request_stage_route_rel',
        string='Reopen request type')

    _sql_constraints = [
        ('stage_stage_from_to_type_uniq',
         'UNIQUE (request_type_id, stage_from_id, stage_to_id)',
         'Such route already present in this request type')
    ]

    def name_get(self):
        res = []
        for record in self:
            name = "%s -> %s" % (record.stage_from_id.name,
                                 record.stage_to_id.name)
            if record.name:
                name = "%s [%s]" % (name, record.name)

            if self.env.context.get('name_only', False) and record.name:
                name = record.name

            res += [(record.id, name)]
        return res

    def _ensure_can_move(self, request):
        self.ensure_one()

        if self.env.su:
            # no access rights checks for superuser
            return

        # Access rights checks (user & group)
        not_allowed_by_user = (
            self.allowed_user_ids and
            self.env.user not in self.allowed_user_ids)
        not_allowed_by_group = (
            self.allowed_group_ids and
            not self.allowed_group_ids & self.env.user.groups_id)
        if not_allowed_by_user or not_allowed_by_group:
            raise exceptions.AccessError(
                _(
                    "This stage change '%(route)s' restricted by "
                    "access rights.\n"
                    "Request: %(request)s\n"
                    "Request Type: %(request_type)s\n"
                    "Request Category: %(request_category)s\n"
                ) % {
                    'route': self.display_name,
                    'request': request.sudo().display_name,
                    'request_type': request.sudo().type_id.display_name,
                    'request_category': (
                        request.sudo().category_id.display_name),
                }
            )

    @api.model
    def ensure_route(self, request, to_stage_id):
        """ Ensure that route to specified stage_id for this request exists
            and current user have right to use it

            :return: return route for this move
        """
        route = self.search([('request_type_id', '=', request.type_id.id)])
        # if not route:
        #     RequestStage = self.env['request.stage']
        #     stage = RequestStage.browse(to_stage_id) if to_stage_id else None
        #     raise exceptions.ValidationError(_(
        #         "Cannot move request to this stage: no route.\n"
        #         "\tRequest: %(request)s\n"
        #         "\tTo stage id: %(to_stage_id)s\n"
        #         "\tTo stage name: %(to_stage_name)s\n"
        #         "\tFrom stage name: %(from_stage_name)s\n"
        #     ) % {
        #         'request': request.name,
        #         'to_stage_id': to_stage_id,
        #         'to_stage_name': stage.name if stage else None,
        #         'from_stage_name': (
        #             request.stage_id.name if request.stage_id else None),
        #     })

        route._ensure_can_move(request)
        return route
