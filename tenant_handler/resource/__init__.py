class TenantResource(object):
  def __init__(self, name):
    self._name = name
    self._status = None

  @property
  def name(self) -> str:
    return self._name

  @property
  def status(self) -> str:
    return self._status
