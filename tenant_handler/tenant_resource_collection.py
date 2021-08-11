from typing import Union, List, Type
from bson.objectid import ObjectId
from tenant_handler.tenant_resource import TenantResource


class TenantResourceCollection(object):
  def __init__(self, collection, document_id):
    self._collection = collection
    self._query = {"_id": ObjectId(document_id)}

  @property
  def version(self) -> int:
    return self._collection.find_one(self._query, {"version": 1, "_id": 0})["version"]

  @version.setter
  def version(self, values:int):
    self._collection.update_one(self._query, {"$set": {"version": values}})

  @property
  def terraform_version(self) -> str:
    return self._collection.find_one(self._query, {"terraform_version": 1, "_id": 0})["terraform_version"]

  @terraform_version.setter
  def terraform_version(self, values:str):
    self._collection.update_one(self._query, {"$set": {"terraform_version": values}})

  @property
  def serial(self) -> str:
    return self._collection.find_one(self._query, {"serial": 1, "_id": 0})["serial"]

  @serial.setter
  def serial(self, values:str):
    self._collection.update_one(self._query, {"$set": {"serial": values}})

  @property
  def lineage(self) -> str:
    return self._collection.find_one(self._query, {"lineage": 1, "_id": 0})["lineage"]

  @lineage.setter
  def lineage(self, values:str):
    self._collection.update_one(self._query, {"$set": {"lineage": values}})

  @property
  def lock(self) -> dict:
    return self._collection.find_one(self._query, {"lock": 1, "_id": 0})["lock"]

  @lock.setter
  def lock(self, value):
    if self.lock is None:
      self._collection.update_one(self._query, {"$set": {"lock": value}})

  @property
  def outputs(self):
    return self._collection.find_one(self._query, {"outputs": 1, "_id": 0})["outputs"]

  @outputs.setter
  def outputs(self, values):
    self._collection.update_one(self._query, {"$set": {"outputs": values}})

  @property
  def resources(self) -> dict:
    tenant_resources = {}
    for resource in self.get_resource_list():
      if resource.module not in tenant_resources.keys():
        tenant_resources[resource.module] = {}
      tenant_resources[resource.module][resource.name] = resource.to_json()
    return tenant_resources

  def get_resource_list(self) -> List[TenantResource]:
    tenant_resource_list = []
    for resource in self._collection.find_one(self._query, {"resources": 1, "_id": 0})["resources"]:
      tenant_resource_list.append(
        TenantResource(
          name=resource["name"],
          module=resource["module"],
          parameters=resource["parameters"],
          mode=resource["mode"],
          resource_type=resource["resource_type"],
          provider=resource["provider"],
          instances=resource["instances"])
      )
    return tenant_resource_list

  def find_resource(self, criteria=None) -> TenantResource:
    if criteria is None:
      criteria = {}
    return self._collection.find_one(self._query, { "resources": { "$elemMatch": criteria }, "_id": 0 })

  def put_resource(self, resource:dict):
    tenant_resource = {
      "name": resource.get("name"),
      "module": resource.get("module"),
      "tf_id": f"module.{resource.get('module')}[\"{resource.get('name')}\"]",
      "parameters": resource.get("parameters", {}),
      "mode": resource.get("mode", "pending"),
      "resource_type": resource.get("resource_type", None),
      "provider": resource.get("provider", None),
      "instances": resource.get("instances", []),
    }
    self._collection.update_one(self._query, {"$push": {"resources": tenant_resource}})

  def remove_resource(self, resource_name:str):
    self.resources.pop(resource_name)

  def to_json(self):
    return self._collection.find_one(self._query, {"_id": 0})

  ################################
  ## Terraform State Operations ##
  ################################

  def lock_state(self, lock) -> Union[None, dict]:
    if self.lock is None:
      self._collection.update_one(self._query, {"$set": {"lock": lock}})
    return self.lock

  def unlock_state(self, lock_id) -> Union[None, dict]:
    if lock_id == self.lock["ID"]:
      self._collection.update_one(self._query, {"$set": {"lock": None}})
    return self.lock

  def update_from_state(self, lock_id, state):

    if lock_id != self.lock["ID"]:
      return False

    self.version = state["version"]
    self.terraform_version = state["terraform_version"]
    self.serial = state["serial"]
    self.lineage = state["lineage"]
    self.outputs = state["outputs"]

    for resource in state["resources"]:
      if resource["mode"] == "managed":
        tenant_resource = self.find_resource({"tf_id": resource["module"]})
        print(tenant_resource)
        print(resource)

    return True

  def purge_state(self):
    self.version = None
    self.terraform_version = None
    self.serial = None
    self.lineage = None
    self.outputs = {}
    self._collection.update_one(self._query, {"$set": {"resources": []}})

  def to_state(self):
    state_resources = []
    for resource in self.get_resource_list():
      resource_state_object = resource.to_state_object()
      if resource_state_object is not None:
        state_resources.append(resource_state_object)
    return {
      "version": self.version,
      "terraform_version": self.terraform_version,
      "serial": self.serial,
      "lineage": self.lineage,
      "outputs": self.outputs,
      "resources": state_resources
    }
