import pymongo
from bson.json_util import dumps
import config_handler
from tenant_handler.tenant import Tenant


class TenantStore(object):
  def __init__(self):
    self._config = config_handler.Config()
    username = self._config.get_string_value("database", "username")
    password = self._config.get_string_value("database", "password")
    endpoint = self._config.get_string_value("database", "endpoint")
    self.database = self._config.get_string_value("database", "database")
    self._client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@{endpoint}/{self.database}?retryWrites=true&w=majority")

  @property
  def client(self):
    return self._client

  @property
  def tenant_collection(self):
    return self.client[self.database].get_collection("tenant")

  @property
  def resource_collection(self):
    return self.client[self.database].get_collection("tenant_resources")

  def get_tenant_list(self):
    return dumps(list(self.tenant_collection.find({}, {"name": 1, "_id": 0})))

  def get_tenant(self, tenant_name) -> Tenant:
    for document in self.tenant_collection.find({"name": tenant_name}, {"name": 1, "resource_collection": 1, "_id": 0}):
      return Tenant(self.tenant_collection, self.resource_collection, document["name"], document["resource_collection"])
    return None

  def create_tenant(self, tenant_name):
    if tenant_name in self.get_tenant_list():
      return False

    resource_collection = {
      "state_initialized": False,
      "version": 4,
      "terraform_version": None,
      "serial": None,
      "lineage": None,
      "lock": None,
      "outputs": {},
      "resources": []
    }

    resource_collection_document_id = self.resource_collection.insert_one(resource_collection).inserted_id

    tenant = {
      "name": tenant_name,
      "members": [],
      "roles": [],
      "resource_collection": str(resource_collection_document_id),
    }

    self.tenant_collection.insert_one(tenant)

    return tenant["name"]
