from typing import Union, Tuple, List
from bson.objectid import ObjectId
from util import config, database
from util.enums import ResourceLifecycleStatus as status
from tenant_handler.tenant_resource import TenantResource


class TenantResourceManifest(object):

  def __init__(self, tenant_name):
    self._collection = self._get_collection()
    self._tenant_name = tenant_name
    self._query = {"tenant": self._tenant_name}

  @staticmethod
  def _get_collection():
    return database.get_collection(
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
      "outputs": {},
      "tenant_configuration_components": []
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
    return TenantResource.list_resources(self.tenant_name, self.id)

  @property
  def tenant_configuration_components(self) -> list:
    components = self._collection.find_one(self._query, {"tenant_configuration_components": 1, "_id": 0})["tenant_configuration_components"]
    if components is None:
      return []
    return components

  @tenant_configuration_components.setter
  def tenant_configuration_components(self, values):
    self._collection.update_one(self._query, {"$set": {"tenant_configuration_components": values}})

  def get_resource(self, resource_id):
    return TenantResource.get_resource(self.tenant_name, self.id, resource_id)

  def find_resources(self, criteria=None) -> List[TenantResource]:
    return TenantResource.find_resources(self.tenant_name, self.id, criteria)

  def put_resource(self, resource:dict) -> Tuple[bool,str]:

    # Construct the query we'll use to get the resource.
    resource_query = {"_id": ObjectId(self.id), "resources": {"$elemMatch":{"name":resource.get("name"), "module": resource.get("module")}}}

    # If it doesn't exist we'll go ahead and push a new one.
    if self._collection.find_one(resource_query) is None:
      return TenantResource.create_resource(
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
    for resource in self.resources:
      tenant_resource_manifest["resources"].append(resource.to_json())
    return tenant_resource_manifest

  ################################
  ## Terraform State Operations ##
  ################################

  def get_workspace_variables(self) -> dict:
    tenant_resources = {}
    for resource in self.resources:
      if resource.status not in [status.PURGING, status.PURGED, status.PURGE_ERROR]:
        if resource.module not in tenant_resources.keys():
          tenant_resources[resource.module] = {}
        tenant_resources[resource.module][resource.name] = resource.to_json()
    return tenant_resources

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

    tenant_config_components = []
    sorted_state_resources = {}

    for resource in state["resources"]:
      if resource["mode"] == "managed":
        if resource["module"] == "module.tenant_configuration":
          tenant_config_components.append(resource)
        else:
          if resource["module"] not in sorted_state_resources.keys():
            sorted_state_resources[resource["module"]] = []
          sorted_state_resources[resource["module"]].append(resource)

    # Update the tenant configuration component array.
    self.tenant_configuration_components = tenant_config_components

    # This is where we take tenant resources Terraform state objects and update the tenant resources.
    for resource_module in sorted_state_resources.keys():

      found_resources = TenantResource.find_resources(self.tenant_name, self.id, {"tf_id": resource_module})

      if len(found_resources) == 0:
        print(f"Unable to locate resource with query: {self.tenant_name} {self.id} {{\"tf_id\": {resource_module}}}")

      tenant_resource = found_resources[0]
      tenant_resource.update_components(sorted_state_resources[resource_module])

      # If the resource was marked for deletion and something is stuck, mark that it's errored.
      if tenant_resource.status == status.PURGING:
        tenant_resource.status = status.PURGE_ERROR
      else:
        # If everything has gone well, then we mark this as complete.
        tenant_resource.status = status.PROVISIONED

    # Find the resources that should have been purged and mark
    for resource in TenantResource.find_resources(self.tenant_name, self.id,{"status": status.PURGING.value}):
      resource.status = status.PURGED

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

    # Get the tenants configuration components
    state_resources.extend(self.tenant_configuration_components)

    # Get the resource configuration components
    for resource in self.resources:
      if resource.status not in [status.PURGING, status.PURGED, status.PURGE_ERROR]:
        state_resources.extend(resource.components)

    return {
      "version": self.version,
      "terraform_version": self.terraform_version,
      "serial": self.serial,
      "lineage": self.lineage,
      "outputs": self.outputs,
      "resources": state_resources
    }
