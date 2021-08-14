from typing import List

from bson import ObjectId
from config_handler import Config
from util import get_collection


class TenantResource(object):
  def __init__(self, resource_id):
    self._config = Config()
    self._collection = self._get_collection()
    self._resource_id = resource_id
    self._query = {"_id": ObjectId(self._resource_id)}

  @staticmethod
  def _get_collection():
    config = Config()
    return get_collection(
      config.get_string_value("database", "database"),
      config.get_string_value("database", "tenant_resource_collection")
    )

  @classmethod
  def list_resources(cls, tenant_name, manifest_id):
    resource_list = list(cls._get_collection().find({"tenant_name": tenant_name, "manifest_id": manifest_id},{"_id":1}))
    resources = []
    for resource in resource_list:
      resources.append(TenantResource(str(resource["_id"])))
    return resources

  @classmethod
  def get_resource(cls, tenant_name, manifest_id, resource_id):
    resource = cls._get_collection().find_one({"tenant_name": tenant_name, "manifest_id": manifest_id, "_id": ObjectId(resource_id)},{"manifest_id": 0,"tenant_name": 0})
    resource["id"] = str(resource["_id"])
    resource.pop("_id")
    return resource

  @classmethod
  def find_resource(cls, tenant_name, manifest_id, criteria=None):
    if criteria is None:
      criteria = {}
    criteria["tenant_name"] = tenant_name
    criteria["manifest_id"] = manifest_id
    return TenantResource(str(cls._get_collection().find_one(criteria, {"_id": 1})["_id"]))

  @classmethod
  def create_resource(cls, **kwargs):
    resource = {
      "tenant_name": kwargs.get("tenant_name"),
      "manifest_id": kwargs.get("manifest_id"),
      "name": kwargs.get("name"),
      "module": kwargs.get("module"),
      "tf_id": f"module.{kwargs.get('module')}[\"{kwargs.get('name')}\"]",
      "status": "pending",
      "parameters": kwargs.get("parameters"),
      "components": []
    }
    cls._get_collection().insert_one(resource)

  @classmethod
  def delete_resource(cls, tenant_name, manifest_id, resource_id):
    cls._get_collection().update_one(
      {'_id': ObjectId(resource_id), "tenant_name": tenant_name, "manifest_id": manifest_id},
      {"$set": {"status": "purge"}}
    )

  @classmethod
  def purge_resource(cls, tenant_name, manifest_id, resource_id):
    cls._get_collection().delete_one({'_id': ObjectId(resource_id), "tenant_name": tenant_name, "manifest_id": manifest_id})

  @property
  def tenant_name(self) -> int:
    return self._collection.find_one(self._query, {"tenant_name": 1, "_id": 0})["tenant_name"]

  @property
  def manifest_id(self) -> int:
    return self._collection.find_one(self._query, {"manifest_id": 1, "_id": 0})["manifest_id"]

  @property
  def resource_id(self) -> str:
    return self._resource_id

  @property
  def name(self) -> str:
    return self._collection.find_one(self._query, {"name": 1, "_id": 0})["name"]

  @property
  def module(self) -> str:
    return self._collection.find_one(self._query, {"module": 1, "_id": 0})["module"]

  @property
  def status(self) -> str:
    return self._collection.find_one(self._query, {"status": 1, "_id": 0})["status"]

  @property
  def parameters(self) -> dict:
    return self._collection.find_one(self._query, {"parameters": 1, "_id": 0})["parameters"]

  @property
  def components(self) -> list:
    return self._collection.find_one(self._query, {"components": 1, "_id": 0})["components"]

  def update_components(self, components):
    self._collection.update_one(self._query, {"$set": {"components": components}})

  def to_json(self) -> dict:
    resource = self._collection.find_one(self._query, {
      "_id": 1,
      "name": 1,
      "module": 1,
      "status": 1,
      "parameters": 1,
      "components": 1
    })
    resource["id"] = str(resource["_id"])
    resource.pop("_id")
    return resource

  def to_state_object(self) -> list:
    return self.components
