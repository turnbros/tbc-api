import json
from collections import KeysView
from tenant_handler.resource import TenantResource

class Tenant(object):
  def __init__(self, name):
    self._name = name
    self._lock = None
    self._state = {"version": 4}
    self._resources = {
      "example_null_module_1": [
        {
          "value_1": "foo_1",
          "value_2": "bar_1",
          "value_3": "baz_1"
        },
        {
          "value_1": "foo_2",
          "value_2": "bar_2",
          "value_3": "baz_2"
        },
        {
          "value_1": "foo_3",
          "value_2": "bar_3",
          "value_3": "baz_3"
        }
      ]
    }

  ########################
  ## Tenant Information ##
  ########################
  @property
  def name(self):
    return self._name

  ############################
  ## Tenant Terraform State ##
  ############################
  @property
  def state(self):
    return self._state

  @state.setter
  def state(self, value):
    self._state = value

  @property
  def lock_id(self):
    return self._lock.get("ID")

  @property
  def lock(self):
    return self._lock

  def lock_state(self, lock):
    if self._lock is None:
      self._lock = lock
    return self._lock

  def unlock_state(self, lock_id):
    if lock_id == self._lock.get("ID"):
      self._lock = None
    return self._lock

  ######################
  ## Tenant Resources ##
  ######################
  @property
  def resources(self):
    return self._resources

  def get_resources(self):
    return json.dumps(self._resources)

  def get_resource_keys(self) -> KeysView:
    return self._resources.keys()

  def get_resource(self, tenant_resource_name) -> TenantResource:
    return self._resources.get(tenant_resource_name)

  def add_resource(self, tenant_resource):
    self._resources[tenant_resource.name] = tenant_resource

  def update_resource(self, tenant_resource):
    self._resources[tenant_resource.name] = tenant_resource

  def remove_resource(self, tenant_resource_name):
    self._resources.pop(tenant_resource_name)

  def to_json(self):
    return {
      "name": self.name,
      "lock": self.lock,
      "state": self.state,
      "resources": self.resources
    }
