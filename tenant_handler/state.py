from typing import Union

class TenantState(object):
  def __init__(self):
    self._lock = None
    self._state = {"version": 4}

  ############################
  ## Tenant Terraform State ##
  ############################
  @property
  def state(self) -> dict:
    return self._state

  @state.setter
  def state(self, value):
    if value is None:
      value = {"version": 4}
    self._state = value

  @property
  def lock_id(self) -> str:
    return self._lock.get("ID")

  @property
  def lock(self) -> dict:
    return self._lock

  def lock_state(self, lock) -> Union[None, dict]:
    if self._lock is None:
      self._lock = lock
    return self._lock

  def unlock_state(self, lock_id) -> Union[None, dict]:
    if lock_id == self._lock.get("ID"):
      self._lock = None
    return self._lock
