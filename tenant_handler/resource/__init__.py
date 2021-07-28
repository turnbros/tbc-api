class TenantResource(object):
  def __init__(self, name, module, status=None, parameters=dict()):
    self._name = name
    self.module = module
    self._status = status
    self._parameters = parameters

  @property
  def name(self) -> str:
    return self._name

  @property
  def status(self) -> str:
    return self._status

  @status.setter
  def status(self, status_value):
    self._status = status_value

  @property
  def parameters(self):
    return self._parameters

  @parameters.setter
  def parameters(self, values):
    self._parameters = values

class TenantResourceCollection(object):
  def __init__(self):
    self._resources = dict()

  def put_resource(self, resource):
    self._resources[resource.name] = resource

  def remove_resource(self, resource_name):
    self._resources.pop(resource_name)

  @property
  def resources(self):
    return list(self._resources.values())

  def get_by_name(self, resource_name) -> TenantResource:
    return self._resources.get(resource_name)

  def get_by_module(self, module):
    found_resources = []
    for x in self.resources:
      if x.module == module:
        found_resources.append(x)
    return found_resources
