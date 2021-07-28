import json
import auth_handler
from flask import Blueprint, request, Response
from tenant_handler.tenant_store import TenantStore

tenant_store = TenantStore()
routes = Blueprint('tenant', __name__)

###################
## State Methods ##
###################
@routes.route('/', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_list():
  return Response(json.dumps(tenant_store.get_tenant_names()), content_type='application/json'), 200

@routes.route('/<tenant_name>', methods=['GET'])
@auth_handler.requires_auth
def get_tenant(tenant_name=None):
  return Response(json.dumps(tenant_store.get_tenant(tenant_name).to_json()), content_type='application/json'), 200

@routes.route('/<tenant_name>/lock', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_terraform_lock(tenant_name=None):
  tenant_terraform_lock = tenant_store.get_tenant(tenant_name).lock
  if tenant_terraform_lock is None:
    tenant_terraform_lock = {}
  return Response(json.dumps(tenant_terraform_lock), content_type='application/json'), 200

@routes.route('/<tenant_name>/state', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_terraform_state(tenant_name=None):
  tenant_state = tenant_store.get_tenant_state(tenant_name)
  return Response(tenant_state[0], content_type='application/json'), tenant_state[1]

@routes.route('/<tenant_name>/state', methods=['POST'])
@auth_handler.requires_auth
def update_tenant_terraform_state(tenant_name=None):
    return tenant_store.update_tenant_state(tenant_name, json.loads(request.data), request.args["ID"])

@routes.route('/<tenant_name>/state', methods=['DELETE'])
@auth_handler.requires_auth
def purge_tenant_terraform_state(tenant_name=None):
    return tenant_store.purge_tenant_state(tenant_name)

@routes.route('/<tenant_name>/state', methods=['LOCK'])
@auth_handler.requires_auth
def lock_tenant_terraform_state(tenant_name=None):
    return tenant_store.lock_tenant_state(tenant_name, json.loads(request.data))

@routes.route('/<tenant_name>/state', methods=['UNLOCK'])
@auth_handler.requires_auth
def unlock_tenant_terraform_state(tenant_name=None):
    return tenant_store.unlock_tenant_state(tenant_name, json.loads(request.data)["ID"])

@routes.route('/<tenant_name>/resources', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_resources(tenant_name=None):
    return  Response(tenant_store.get_tenant_resources(tenant_name)[0], content_type='application/json'), 200
