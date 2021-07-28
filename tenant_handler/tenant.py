import json
from collections import KeysView
from tenant_handler.state import TenantState
from tenant_handler.resource import TenantResourceCollection, TenantResource


class Tenant(object):
  def __init__(self, name):
    self._name = name
    self._state = TenantState()
    self._resources = TenantResourceCollection()

    example_null_module_1_instance_1 = TenantResource("instance_1", "example_null_module_1")
    example_null_module_1_instance_1.parameters = {
      "value_1": "foo_1",
      "value_2": "bar_1",
      "value_3": "baz_1"
    }

    example_null_module_1_instance_2 = TenantResource("instance_2", "example_null_module_1")
    example_null_module_1_instance_2.parameters = {
      "value_1": "foo_2",
      "value_2": "bar_2",
      "value_3": "baz_2"
    }

    example_null_module_1_instance_3 = TenantResource("instance_3", "example_null_module_1")
    example_null_module_1_instance_3.parameters = {
      "value_1": "foo_3",
      "value_2": "bar_3",
      "value_3": "baz_3"
    }


  ########################
  ## Tenant Information ##
  ########################
  @property
  def name(self) -> str:
    return self._name

  ############################
  ## Tenant Terraform State ##
  ############################
  @property
  def lock(self):
    return self._state.lock

  def lock_state(self, lock):
    return self._state.lock_state(lock)

  def unlock_state(self, lock_id):
    return self._state.unlock_state(lock_id)

  @property
  def state(self)-> dict:
    return self._state.state

  @state.setter
  def state(self, value):
    self._state.state = value

  ######################
  ## Tenant Resources ##
  ######################
  @property
  def resources(self):
    return self._resources

  def get_resources(self):
    return json.dumps(self._resources)

  def get_resource(self, tenant_resource_name) -> TenantResource:
    return self._resources.get_by_name(tenant_resource_name)

  def add_resource(self, tenant_resource):
    self._resources.put_resource(tenant_resource)

  def update_resource(self, tenant_resource):
    self._resources.put_resource(tenant_resource)

  def remove_resource(self, tenant_resource_name):
    self._resources.remove_resource(tenant_resource_name)

  def to_json(self):
    return {
      "name": self.name,
      "lock": self.lock,
      "state": self.state,
      "resources": self.resources
    }
