import json
import auth_handler
from flask import Blueprint, Response, request
from tenant_handler.tenant_store import TenantStore

tenant_store = TenantStore()
tenant_routes = Blueprint('tenant', __name__, url_prefix='/tenant')

@tenant_routes.route('', methods=['GET'])
@auth_handler.requires_auth
def list_tenants():
  return Response(tenant_store.get_tenant_list(), content_type='application/json'), 200

@tenant_routes.route('', methods=['POST'])
@auth_handler.requires_auth
def create_tenant():
  return Response(tenant_store.create_tenant(request.get_json()["name"]), content_type='application/json'), 200

@tenant_routes.route('/<name>', methods=['GET'])
@auth_handler.requires_auth
def get_tenant(name):
  return Response(json.dumps(tenant_store.get_tenant(name).to_json()), content_type='application/json'), 200

@tenant_routes.route('/<name>/name', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_name(name):
  return Response(tenant_store.get_tenant(name).name, content_type='application/json'), 200

@tenant_routes.route('/<name>/resource_collection', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_resource_collection(name):
  return Response(json.dumps(tenant_store.get_tenant(name).resource_collection.to_json()), content_type='application/json'), 200

@tenant_routes.route('/<name>/resource_collection/<resource>', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_resource_collection_resource(name, resource):
  return Response(json.dumps(tenant_store.get_tenant(name).resource_collection.find_resources({"name": resource})), content_type='application/json'), 200

@tenant_routes.route('/<name>/resource_collection', methods=['PUT'])
@auth_handler.requires_auth
def put_tenant_resource_collection_resource(name):
  requested_resource = json.loads(request.data)
  tenant_resource = {
    "name": requested_resource.get("name", None),
    "module": requested_resource.get("module", None),
    "parameters": requested_resource.get("parameters", None)
  }
  return Response(json.dumps(tenant_store.get_tenant(name).resource_collection.put_resource(tenant_resource)), content_type='application/json'), 200

@tenant_routes.route('/<name>/resources', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_resources(name):
  return Response(json.dumps(tenant_store.get_tenant(name).resource_collection.resources), content_type='application/json'), 200

###################################
## Tenant Terraform State Routes ##
###################################

@tenant_routes.route('/<name>/resource_collection/state', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_resource_collection_state(name):
  return Response(json.dumps(tenant_store.get_tenant(name).resource_collection.to_state()), content_type='application/json'), 200


@tenant_routes.route('/<name>/resource_collection/state', methods=['POST'])
@auth_handler.requires_auth
def update_tenant_terraform_state(name=None):
  if tenant_store.get_tenant(name).resource_collection.update_from_state(request.args["ID"], json.loads(request.data)):
    return "", 200
  return "", 423

@tenant_routes.route('/<name>/resource_collection/state', methods=['DELETE'])
@auth_handler.requires_auth
def purge_tenant_terraform_state(name=None):
  return tenant_store.get_tenant(name).resource_collection.purge_state()

@tenant_routes.route('/<name>/resource_collection/state', methods=['LOCK'])
@auth_handler.requires_auth
def lock_tenant_terraform_state(name=None):
  requested_lock = json.loads(request.data)
  state_lock = tenant_store.get_tenant(name).resource_collection.lock_state(requested_lock)
  if requested_lock["ID"] == state_lock["ID"]:
    return state_lock, 200
  return state_lock, 409

@tenant_routes.route('/<name>/resource_collection/state', methods=['UNLOCK'])
@auth_handler.requires_auth
def unlock_tenant_terraform_state(name=None):
  requested_lock = json.loads(request.data)
  state_lock = tenant_store.get_tenant(name).resource_collection.unlock_state(requested_lock["ID"])
  if state_lock is None:
    return "", 200
  return state_lock, 423

@tenant_routes.route('/<name>/resource_collection/state/lock', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_terraform_lock(name=None):
  tenant_terraform_lock = tenant_store.get_tenant(name).resource_collection.lock
  if tenant_terraform_lock is None:
    tenant_terraform_lock = {}
  return Response(json.dumps(tenant_terraform_lock), content_type='application/json'), 200