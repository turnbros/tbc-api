from tenant_handler.tenant_resource_collection import TenantResourceCollection

class Tenant(object):
  def __init__(self, collection, resource_collection, name, document_id):
    self._collection = collection
    self._query = {"name": name}
    self._resource_collection = TenantResourceCollection(resource_collection, document_id)

  @property
  def name(self) -> str:
    return self._collection.find_one(self._query, {"name": 1, "_id": 0})["name"]

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
  def resource_collection(self):
    return self._resource_collection

  def to_json(self):
    tenant = self._collection.find_one(self._query, {"_id": 0})
    tenant["resource_collection"] = self.resource_collection.to_json()
    return tenant
