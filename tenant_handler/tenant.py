from util import config, database
from tenant_handler.tenant_resource_manifest import TenantResourceManifest


class Tenant(object):

  def __init__(self, name):
    self._collection = self._get_collection()
    self._name = name
    self._query = {"name": self._name}

  @staticmethod
  def _get_collection():
    return database.get_collection(
      config.get_string_value("database", "database"),
      config.get_string_value("database", "tenant_collection")
    )

  @classmethod
  def list_tenants(cls):
    return list(cls._get_collection().find({}, {"name": 1, "_id": 0}))

  @classmethod
  def create_tenant(cls, **kwargs):
    tenant = {
      "name": kwargs["name"],
      "members": [],
      "roles": []
    }
    cls._get_collection().insert_one(tenant)
    TenantResourceManifest.create_resource_manifest(tenant_name=kwargs["name"])
    return Tenant(kwargs["name"]).to_json()

  @property
  def name(self) -> str:
    return self._name

  @property
  def members(self) -> list:
    return self._collection.find_one(self._query, {"members": 1, "_id": 0})["members"]

  @members.setter
  def members(self, value):
    self._collection.update_one(self._query, {"$set": {"members": value}})

  @property
  def roles(self) -> list:
    return self._collection.find_one(self._query, {"roles": 1, "_id": 0})["roles"]

  @roles.setter
  def roles(self, value):
    self._collection.update_one(self._query, {"$set": {"roles": value}})

  @property
  def port_allocation(self):
    return {
      "start": 20480,
      "end": 20780,
      "size": 300,
      "available": 298,
      "allocated": 2,
      "allocations": [
        {
          "resource_id": 2345,
          "ports": [20780,20781]
        }
      ]
    }

  @property
  def resource_manifest(self):
    return TenantResourceManifest(self.name)

  def to_json(self):
    tenant = self._collection.find_one(self._query, {"_id": 0})
    tenant["resource_manifest"] = self.resource_manifest.to_json()
    return tenant
