import json
import auth_handler
from tenant_handler import datastore
from flask import Blueprint, request, Response

routes = Blueprint('tenant_state', __name__, url_prefix='/state')

@routes.route('/lock', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_terraform_lock(tenant_name=None):
  tenant_terraform_lock = datastore.get_tenant_store().get_tenant(tenant_name).lock
  if tenant_terraform_lock is None:
    tenant_terraform_lock = {}
  return Response(json.dumps(tenant_terraform_lock), content_type='application/json'), 200

@routes.route('', methods=['GET'])
@auth_handler.requires_auth
def get_tenant_terraform_state(tenant_name=None):
  tenant_state = datastore.get_tenant_store().get_tenant_state(tenant_name)
  return Response(tenant_state[0], content_type='application/json'), tenant_state[1]

@routes.route('', methods=['POST'])
@auth_handler.requires_auth
def update_tenant_terraform_state(tenant_name=None):
    return datastore.get_tenant_store().update_tenant_state(tenant_name, json.loads(request.data), request.args["ID"])

@routes.route('', methods=['DELETE'])
@auth_handler.requires_auth
def purge_tenant_terraform_state(tenant_name=None):
    return datastore.get_tenant_store().purge_tenant_state(tenant_name)

@routes.route('', methods=['LOCK'])
@auth_handler.requires_auth
def lock_tenant_terraform_state(tenant_name=None):
    return datastore.get_tenant_store().lock_tenant_state(tenant_name, json.loads(request.data))

@routes.route('', methods=['UNLOCK'])
@auth_handler.requires_auth
def unlock_tenant_terraform_state(tenant_name=None):
    return datastore.get_tenant_store().unlock_tenant_state(tenant_name, json.loads(request.data)["ID"])
