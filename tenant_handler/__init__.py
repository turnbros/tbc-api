import json
from util import auth
from flask import Blueprint, Response, request
from tenant_handler.tenant import Tenant
from terraform_runner import runner
import traceback
from urllib.parse import unquote

tenant_routes = Blueprint('tenant', __name__, url_prefix='/tenants')

###################
## Tenant Routes ##
###################

@tenant_routes.route('', methods=['GET'])
@auth.requires_auth
def list_tenants():
  return Response(json.dumps(Tenant.list_tenants()), content_type='application/json'), 200

@tenant_routes.route('', methods=['POST'])
@auth.requires_auth
def create_tenant():
  return Response(json.dumps(Tenant.create_tenant(name=request.get_json()["name"])), content_type='application/json'), 200

@tenant_routes.route('/<name>', methods=['GET'])
@auth.requires_auth
def get_tenant(name):
  return Response(json.dumps(Tenant(name).to_json()), content_type='application/json'), 200


############################
## Tenant Resource Routes ##
############################

@tenant_routes.route('/<name>/resources', methods=['GET'])
@auth.requires_auth
def get_tenant_resource_collection(name):
  # TODO: Need to revisit the difference between `resource_manifest.to_json()` and `resource_manifest.find_resources`
#  if len(request.args) > 0:
  search_criteria = {}
  for criteria_key in request.args.keys():
    search_criteria[criteria_key] = json.loads(unquote(request.args.get(criteria_key)))
  print(search_criteria)
  found_resources = Tenant(name).resource_manifest.find_resources(criteria=search_criteria)
  response_json = [x.to_json() for x in found_resources]
  return Response(json.dumps(response_json), content_type='application/json'), 200
  #return Response(json.dumps(response_json), content_type='application/json'), 200
#  else:
#    return Response(json.dumps(Tenant(name).resource_manifest.to_json()), content_type='application/json'), 200

@tenant_routes.route('/<name>/resources', methods=['POST', 'PUT'])
@auth.requires_auth
def create_tenant_resource(name):
  requested_resource = json.loads(request.data)
  tenant_resource = {
    "name": requested_resource.get("name", None),
    "module": requested_resource.get("module", None),
    "parameters": requested_resource.get("parameters", None)
  }
  print(tenant_resource)
  Tenant(name).resource_manifest.put_resource(tenant_resource)

  print(runner.run_terraform(name))
  return Response(json.dumps(tenant_resource), content_type='application/json'), 200

@tenant_routes.route('/<name>/resources/<resource_id>', methods=['GET'])
@auth.requires_auth
def get_tenant_resource(name, resource_id):
  return Response(json.dumps(Tenant(name).resource_manifest.get_resource(resource_id)), content_type='application/json'), 200

@tenant_routes.route('/<name>/resources/<resource_id>', methods=['DELETE'])
@auth.requires_auth
def delete_tenant_resource(name, resource_id):
  try:
    Tenant(name).resource_manifest.delete_resource(resource_id)
    print(runner.run_terraform(name))
  except Exception as error:
    print(error)
    traceback.print_exc()
    return Response(json.dumps({"message": "Failed to delete resource"}), content_type='application/json'), 500
  return Response(json.dumps({"message": "Resource deleted"}), content_type='application/json'), 200

#######################################
## Tenant Terraform Workspace Routes ##
#######################################

@tenant_routes.route('/<name>/workspace/variables', methods=['GET'])
@auth.requires_auth
def get_tenant_workspace_variables(name):
  tenant_workspace_variables = Tenant(name).resource_manifest.get_workspace_variables()
  return Response(json.dumps(tenant_workspace_variables), content_type='application/json'), 200

@tenant_routes.route('/<name>/workspace/apply', methods=['PUT'])
@auth.requires_auth
def run_terraform_apply_job(name=None):
  result = runner.run_terraform(name)
  return Response(json.dumps(result), content_type='application/json'), 200

@tenant_routes.route('/<name>/workspace/state', methods=['GET'])
@auth.requires_auth
def get_tenant_resource_collection_state(name):
  manifest_state = Tenant(name).resource_manifest.to_state()
  return Response(json.dumps(manifest_state), content_type='application/json'), 200

@tenant_routes.route('/<name>/workspace/state', methods=['POST'])
@auth.requires_auth
def update_tenant_terraform_state(name=None):
  if Tenant(name).resource_manifest.update_from_state(request.args["ID"], json.loads(request.data)):
    return "", 200
  return "", 423

@tenant_routes.route('/<name>/workspace/state', methods=['DELETE'])
@auth.requires_auth
def purge_tenant_terraform_state(name=None):
  return Tenant(name).resource_manifest.purge_state()

@tenant_routes.route('/<name>/workspace/state', methods=['LOCK'])
@auth.requires_auth
def lock_tenant_terraform_state(name=None):
  requested_lock = json.loads(request.data)
  state_lock = Tenant(name).resource_manifest.lock_state(requested_lock)
  if requested_lock["ID"] == state_lock["ID"]:
    return state_lock, 200
  return state_lock, 409

@tenant_routes.route('/<name>/workspace/state', methods=['UNLOCK'])
@auth.requires_auth
def unlock_tenant_terraform_state(name=None):
  requested_lock = json.loads(request.data)
  state_lock = Tenant(name).resource_manifest.unlock_state(requested_lock["ID"])
  if state_lock is None:
    return "", 200
  return state_lock, 423

@tenant_routes.route('/<name>/workspace/state/lock', methods=['GET'])
@auth.requires_auth
def get_tenant_terraform_lock(name=None):
  tenant_terraform_lock = Tenant(name).resource_manifest.lock
  if tenant_terraform_lock is None:
    tenant_terraform_lock = {}
  return Response(json.dumps(tenant_terraform_lock), content_type='application/json'), 200
