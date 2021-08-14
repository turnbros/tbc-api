from typing import Union, List
from bson.objectid import ObjectId
from config_handler import Config
from tenant_handler.tenant_resource import TenantResource
from util import get_collection


class TenantResourceManifest(object):

  def __init__(self, tenant_name):
    self._config = Config()
    self._collection = self._get_collection()
    self._tenant_name = tenant_name
    self._query = {"tenant": self._tenant_name}

  @staticmethod
  def _get_collection():
    config = Config()
    return get_collection(
      config.get_string_value("database", "database"),
      config.get_string_value("database", "tenant_resource_manifest_collection")
    )

  @classmethod
  def create_resource_manifest(cls, **kwargs):
    resource_collection = {
      "tenant": kwargs.get("tenant_name"),
      "state_initialized": False,
      "version": 4,
      "terraform_version": None,
      "serial": None,
      "lineage": None,
      "lock": None,
      "outputs": {}
    }
    cls._get_collection().insert_one(resource_collection)

  @property
  def tenant_name(self) -> str:
    return self._tenant_name

  @property
  def id(self) -> str:
    return str(self._collection.find_one(self._query, {"_id": 1})["_id"])

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
    for resource in self.list_resources():
      if resource.status != "purge":
        if resource.module not in tenant_resources.keys():
          tenant_resources[resource.module] = {}
        tenant_resources[resource.module][resource.name] = resource.to_json()
    return tenant_resources

  def list_resources(self) -> List[TenantResource]:
    return TenantResource.list_resources(self.tenant_name, self.id)

  def get_resource(self, resource_id):
    return TenantResource.get_resource(self.tenant_name, self.id, resource_id)

  def find_resource(self, criteria=None) -> TenantResource:

    if criteria is None:
      criteria = {}

    criteria["tenant_name"] = self.tenant_name
    criteria["manifest_id"] = self.id

    return self._collection.find_one(self._query, { "resources": { "$elemMatch": criteria }, "_id": 0 })

  def put_resource(self, resource:dict):

    # Construct the query we'll use to get the resource.
    resource_query = {"_id": ObjectId(self.id), "resources": {"$elemMatch":{"name":resource.get("name"), "module": resource.get("module")}}}

    # If it doesn't exist we'll go ahead and push a new one.
    if self._collection.find_one(resource_query) is None:
      TenantResource.create_resource(
        tenant_name=self.tenant_name,
        manifest_id=self.id,
        name=resource.get("name"),
        module=resource.get("module"),
        parameters=resource.get("parameters")
      )

    # If the resource does exist we'll go ahead and update it.
    else:
      update_document = {
        "$set": {
          "resources.$.name": resource.get("name"),
          "resources.$.module": resource.get("module"),
          "resources.$.tf_id": f"module.{resource.get('module')}[\"{resource.get('name')}\"]",
          "resources.$.parameters": resource.get("parameters", {})
        }
      }
      self._collection.update_one(resource_query, update_document,upsert=True)

  def delete_resource(self, resource_id):
    TenantResource.delete_resource(self.tenant_name, self.id, resource_id)

  def to_json(self):
    tenant_resource_manifest = self._collection.find_one(self._query, {"_id": 1, "tenant": 0})
    tenant_resource_manifest["id"] = str(tenant_resource_manifest["_id"])
    tenant_resource_manifest.pop("_id")
    tenant_resource_manifest["resources"] = []
    for resource in TenantResource.list_resources(self.tenant_name, self.id):
      tenant_resource_manifest["resources"].append(resource.to_json())
    return tenant_resource_manifest






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

    sorted_state_resources = {}

    for resource in state["resources"]:

      if resource["mode"] == "managed":

        if resource["module"] not in sorted_state_resources.keys():
          sorted_state_resources[resource["module"]] = []

        print(f"State Resource: {resource}")
        sorted_state_resources[resource["module"]].append(resource)

    for resource_module in sorted_state_resources.keys():
      tenant_resource = TenantResource.find_resource(self.tenant_name, self.id,{"tf_id": resource_module})
      tenant_resource.update_components(sorted_state_resources[resource_module])

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
    for resource in self.list_resources():
      state_resources.extend(resource.components)

    return {
      "version": self.version,
      "terraform_version": self.terraform_version,
      "serial": self.serial,
      "lineage": self.lineage,
      "outputs": self.outputs,
      "resources": state_resources
    }
