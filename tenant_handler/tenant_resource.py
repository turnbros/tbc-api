class TenantResource(object):
  def __init__(self,
               name,
               module,
               parameters=None,
               mode=None,
               resource_type=None,
               provider=None,
               instances=None
               ):

    if parameters is None:
      parameters = dict()
    if instances is None:
      instances = []

    self._name = name
    self._module = module
    self._parameters = parameters
    self._mode = mode
    self._type = resource_type
    self._provider = provider
    self._instances = instances

  @property
  def name(self) -> str:
    return self._name

  @property
  def module(self) -> str:
    return self._module

  @property
  def parameters(self):
    return self._parameters

  @property
  def mode(self):
    return self._mode

  @property
  def type(self):
    return self._type

  @property
  def provider(self):
    return self._provider

  @property
  def instances(self):
    return self._instances

  def to_json(self) -> dict:
    return {
      "name": self.name,
      "module": self.module,
      "mode": self.mode,
      "parameters": self.parameters
    }

  def to_state_object(self) -> dict:
    if self.mode == "pending":
      return None

    return {
      "module": f"module.{self.module}[\"{self.name}\"]",
      "mode": self.mode,
      "type": self.type,
      "name": self.module,
      "provider": self.provider,
      "instances": self.instances
    }
