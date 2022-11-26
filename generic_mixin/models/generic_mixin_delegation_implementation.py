import logging
from odoo import models, api

_logger = logging.getLogger(__name__)


class GenericMixinDelegationImplementation(models.AbstractModel):
    """ Mixin that have to help to deal with "inheritance via delegation".
        This is companion mixin to 'generic.mixin.delegation.interface.

        Inheritance via delegation with multiple implementations is concept,
        when you have single interface model (that contain basic fields and
        possibly methods) and multiple implementation models for
        this interface.

        For example, we could have basic interface model
        named Resource that could have following implementations:
            - Notebook
            - Workstation
            - Car
            - Printer

        Logically, each of these models could have it's own set of fields
        that represents some characteristics. But for example for accounting
        we need only some subset of fields and methods defined by interface.
        But to make to manage this, for example assign
        some resource for some employee, we have to have different
        characteristics for each type of resource, thus we have to have
        specific model for each resource.

        Other example could be interface Device, and different implementations
        of devices

        And this mixin have to help to automatically handle one2one relation
        between interface and implementation.

        Mixin `generic.mixin.delegation.interface` is responsible for interface
        concept.
        Mixin `generic.mixin.delegation.implementation` is responsible for
        implementation of interface concept

        For example, to create new interface Thing, we have to create model
        inheriting this mixin, and define there fields that will point to
        implementation:

            class Thing(models.Model):
                _name = 'my.thing'
                _inherit = 'generic.mixin.delegation.interface'

                _generic_mixin_implementation_model_field = \
                    'implementation_model'
                _generic_mixin_implementation_id_field = 'implementation_id'

                implementation_model = fields.Char(
                    required=True, index=True, readonly=True)
                implementation_id = fields.Integer(
                    required=True, index=True, readonly=True)

                # Next define interface-specific fields:
                uuid = fields.Char()
                label = fields.Char()
                state = fields.Selection(
                    [('draft', 'Draft'),
                     ('active', 'Active')]

        Next, to be able to define implementations of this interface, we
        have to create implementation mixin, that have to inherit from
        companion mixin 'generic.mixin.delegation.implementation' and,
        this new mixin have to define delegated m2o field that points
        to Thing interface. for example:

            class ThingImplementationMixin(models.AbstractModel):
                _name = 'my.thing.implementation.mixin'
                _inherit = 'generic.mixin.delegation.implementation'

                # Here we have to define field, that points to interface model,
                # also, pay attention to 'delegate=True' paramater that is
                # required to make it work.
                thing_id = fields.Many2one(
                    'my.thing', index=True, auto_join=True,
                    required=True, delegate=True, ondelete='restrict')

        Then you can define multiple implementations of Thing using
        mixin created above.
        For example:

            class Vehicle(models.Model):
                _name = "my.vehicle"
                _inherit = 'my.thing.implementation.mixin'

                vehicle_color = fields.Char()

            class Workstation(models.Model):
                _name = 'my.workstation'
                _inherit = 'my.thing.implementation'

                workstation_cpu = fields.Char()
                workstation_memory = fields.Char()

        Next, everywhere where you need to point to anything that implements
        mentioned interface, you can use regular many2one fields that point
        to interface and work with interface. And interface itself can access
        implementation and delegate some work to implementation if needed.
        For example:

            class ThingActivationOrder(models.Model):
                _name = 'my.thing.activation.order'

                thing_id = fields.Many2one('my.thing', required=True)
                user_id = fields.Many2one('res.users')

                def action_activate_thing(self):
                    self.ensure_one()
                    self.thing_id.state = 'active'

        This way, it is possible to implement processes that do not depend on
        concrete implementation model, but require only some kind of interface.
        Also, these mixins automatically handles clean-up actions on deletion
        and automatic backlins from interface record to implementation record
        via generic many2one (model_name + record_id) fields.
    """
    _name = 'generic.mixin.delegation.implementation'
    _description = 'Generic Mixin Delegation: Implementation'
    _inherit = [
        'generic.mixin.guard.fields',
    ]

    def _generic_mixin_guard__get_deny_write_fields(self):
        res = super()._generic_mixin_guard__get_deny_write_fields() + list(
            self._generic_mixin_delegation__get_interfaces_info())
        return res

    def _generic_mixin_delegation__get_interfaces_info(self):
        """ Return dictionary with supported interfaces mapping:
                interface_field -> interface_model
        """
        # TODO: Memoize result
        return {
            field_name: m_name
            for m_name, field_name in self._inherits.items()
            if self.env[m_name]._generic_mixin_implementation_id_field and
            self.env[m_name]._generic_mixin_implementation_model_field
        }

    @api.model
    def _add_missing_default_values(self, values):
        res = super()._add_missing_default_values(values)

        to_update = {}
        interface_info = self._generic_mixin_delegation__get_interfaces_info()
        for interface_model in interface_info.values():
            # Find delegation interface model
            Interface = self.env[interface_model]

            if Interface._generic_mixin_implementation_model_field in res:
                # If value for model field already computed then skip
                continue

            impl_model_field = Interface._fields[
                Interface._generic_mixin_implementation_model_field
            ]
            if not impl_model_field.store:
                continue
            if impl_model_field.compute:
                continue
            if impl_model_field.related:
                continue

            to_update[Interface._generic_mixin_implementation_model_field] = (
                self._name)

        if to_update:
            # We have to avoid modification of input params, thus we copy res
            res = dict(res)
            res.update(to_update)
        return res

    @api.model
    def create(self, vals):
        values = dict(vals)

        interface_info = self._generic_mixin_delegation__get_interfaces_info()
        for interface_field, interface_model in interface_info.items():
            # Find delegation interface model
            Interface = self.env[interface_model]

            # Find name of field that represents ID of implementation
            implementation_id_field = (
                Interface._generic_mixin_implementation_id_field)

            # Add fake resource id to values. This is required to create
            # 'generic.resource' record, because 'res_id' field is required
            # This field will be updated after record creation
            values[
                implementation_id_field
            ] = Interface._generic_mixin_guard__wrap_field(
                implementation_id_field, -1)

        # Create record
        rec = super().create(values)

        for interface_field, interface_model in interface_info.items():
            # Find delegation interface model
            Interface = self.env[interface_model]

            # Find name of field that represents ID of implementation
            implementation_id_field = (
                Interface._generic_mixin_implementation_id_field)

            # Update res_id with created id
            rec.sudo()[interface_field].write({
                implementation_id_field:
                    Interface._generic_mixin_guard__wrap_field(
                        implementation_id_field, rec.id),
            })

            # We have to ensure that all changes writtent to avoid unique
            # constraint voilations (for implementation_id field)
            rec.sudo()[interface_field].flush(
                fnames=[Interface._generic_mixin_implementation_id_field],
                records=rec.sudo()[interface_field])

        return rec

    def unlink(self):
        interface_info = self._generic_mixin_delegation__get_interfaces_info()

        # Find deletagion interfaces to be removed
        to_cleanup = {
            interface_model: self.sudo().mapped(interface_field)
            for interface_field, interface_model in interface_info.items()
        }

        # Delete records
        res = super().unlink()

        # Delete delegation interfaces and return status
        for interface_records in to_cleanup.values():
            interface_records.unlink()
        return res
