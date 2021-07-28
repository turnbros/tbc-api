import json
from tenant_handler.tenant import Tenant

class TenantStore(object):

  def __init__(self):
    self._tenant_store = {}

  def get_tenant_names(self):
    return list(self._tenant_store.keys())

  def get_tenant(self, tenant_name) -> Tenant:
    tenant = self._tenant_store.get(tenant_name)
    if tenant is None:
      tenant = self.create_tenant(tenant_name)
    return tenant

  def create_tenant(self, tenant_name) -> Tenant:
    tenant = Tenant(tenant_name)
    self._tenant_store[tenant_name] = tenant
    return tenant

  def lock_tenant_state(self, tenant_name, lock):
    state_lock = self.get_tenant(tenant_name).lock_state(lock)
    if state_lock["ID"] != lock["ID"]:
      return json.dumps(state_lock), 409
    return "", 200

  def unlock_tenant_state(self, tenant_name, lock_id):
    state_lock = self.get_tenant(tenant_name).unlock_state(lock_id)
    if state_lock is not None:
      return json.dumps(state_lock), 423
    return "", 200

  def get_tenant_state(self, tenant_name):
    return json.dumps(self.get_tenant(tenant_name).state), 200

  def update_tenant_state(self, tenant_name, tenant_state, lock_id):
    tenant = self.get_tenant(tenant_name)
    if tenant.lock_id == lock_id:
      tenant.state = tenant_state
      return "", 200
    return json.dumps(tenant.lock), 409

  def purge_tenant_state(self, tenant_name):
    self.get_tenant(tenant_name).state = {"version": 4}
    return "", 200

  def get_tenant_resources(self, tenant_name):
    return self.get_tenant(tenant_name).get_resources(), 200

tenant_store = TenantStore()

def get_tenant_store():
  return tenant_store